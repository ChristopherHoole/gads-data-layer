"""N1b Gate 3 — Google Ads mutate service for negative-keyword push.

Single public entry point: push_negatives_to_shared_lists(client_id, items)
- Looks up the live shared_set google_ads_list_id per item via
  act_v2_negative_keyword_lists (must be is_linked_to_campaign=TRUE)
- Groups by list_id, one SharedCriterionService.mutate_shared_criteria call
  per list
- Uses partial_failure=True so one bad keyword doesn't kill the batch
- Daily op-budget guard: fails early with daily_op_budget_exceeded when
  (ops pushed today) + len(items) > 15000 (Basic Access ceiling)

Caller updates source rows with the returned results per the pattern in the
brief — this module does NOT write back to act_v2_* tables.
"""
import logging
import os
from pathlib import Path

import duckdb
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
YAML_PATH = str(PROJECT_ROOT / "secrets" / "google-ads.yaml")
DB_PATH = str(PROJECT_ROOT / "warehouse.duckdb")

DAILY_OP_BUDGET = 15000  # Basic Access ceiling
OP_BUDGET_ERROR = 'daily_op_budget_exceeded'
LIST_NOT_LINKED_ERROR = 'target_list_not_linked_to_campaign'

logger = logging.getLogger('act_v2_mutate')
if not logger.handlers:
    import sys
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(h)
logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _load_client_context(con, client_id: str) -> dict:
    """Return {customer_id, role_to_list_id: {role: google_ads_list_id}}.
    Only LINKED lists are included — unlinked ones can't receive negs."""
    row = con.execute(
        "SELECT google_ads_customer_id FROM act_v2_clients WHERE client_id = ?",
        [client_id],
    ).fetchone()
    if not row:
        raise ValueError(f'client_id {client_id!r} not found in act_v2_clients')
    customer_id = row[0]

    role_rows = con.execute(
        """SELECT list_role, google_ads_list_id
           FROM act_v2_negative_keyword_lists
           WHERE client_id = ?
             AND list_role IS NOT NULL
             AND is_linked_to_campaign = TRUE""",
        [client_id],
    ).fetchall()
    role_to_list_id = {role: gid for role, gid in role_rows}
    return {'customer_id': customer_id, 'role_to_list_id': role_to_list_id}


def _count_ops_today(con, client_id: str) -> int:
    """Sum of today's successful pushes across both source tables."""
    row = con.execute(
        """SELECT
             (SELECT COUNT(*) FROM act_v2_search_term_reviews
              WHERE client_id = ? AND CAST(pushed_to_ads_at AS DATE) = CURRENT_DATE)
           +
             (SELECT COUNT(*) FROM act_v2_phrase_suggestions
              WHERE client_id = ? AND CAST(pushed_to_ads_at AS DATE) = CURRENT_DATE)
        """,
        [client_id, client_id],
    ).fetchone()
    return int(row[0] or 0)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def push_negatives_to_shared_lists(
    client_id: str,
    items: list[dict],
    google_ads_client: GoogleAdsClient | None = None,
    db_path: str = DB_PATH,
) -> dict:
    """Push a batch of negatives to Google Ads shared lists.

    items: list of dicts, each with:
      source_table: 'search_term_reviews' | 'phrase_suggestions'
      source_row_id: int
      keyword_text: str
      match_type: 'EXACT' | 'PHRASE'
      list_role: str

    Returns:
      {
        'succeeded': [{'source_row_id', 'source_table', 'criterion_id',
                       'resource_name', 'keyword_text', 'match_type'}],
        'failed':    [{'source_row_id', 'source_table', 'keyword_text',
                       'match_type', 'error'}],
        'ops_budget_remaining': int,
      }
    """
    if not items:
        return {'succeeded': [], 'failed': [], 'ops_budget_remaining': None}

    # -------------------------------------------------------------------
    # Op-budget guard
    # -------------------------------------------------------------------
    con = duckdb.connect(db_path, read_only=True)
    try:
        ops_today = _count_ops_today(con, client_id)
        ctx = _load_client_context(con, client_id)
    finally:
        con.close()

    if ops_today + len(items) > DAILY_OP_BUDGET:
        remaining = max(0, DAILY_OP_BUDGET - ops_today)
        return {
            'succeeded': [],
            'failed': [
                {
                    'source_row_id': it['source_row_id'],
                    'source_table': it['source_table'],
                    'keyword_text': it['keyword_text'],
                    'match_type': it['match_type'],
                    'error': (
                        f'{OP_BUDGET_ERROR}: {ops_today} pushed today, '
                        f'{len(items)} requested, ceiling {DAILY_OP_BUDGET}'
                    ),
                }
                for it in items
            ],
            'ops_budget_remaining': remaining,
        }

    # -------------------------------------------------------------------
    # Resolve list_role -> shared_set_id; short-circuit unresolved items
    # -------------------------------------------------------------------
    role_to_list_id = ctx['role_to_list_id']
    customer_id = ctx['customer_id']

    grouped: dict[str, list[dict]] = {}  # shared_set_id -> [items]
    failed: list[dict] = []
    for it in items:
        role = it['list_role']
        gid = role_to_list_id.get(role)
        if not gid:
            failed.append({
                'source_row_id': it['source_row_id'],
                'source_table': it['source_table'],
                'keyword_text': it['keyword_text'],
                'match_type': it['match_type'],
                'error': f'{LIST_NOT_LINKED_ERROR}: no linked list found for role={role!r}',
            })
            continue
        grouped.setdefault(gid, []).append(it)

    # -------------------------------------------------------------------
    # Execute one mutate call per shared_set with partial_failure=True
    # -------------------------------------------------------------------
    if google_ads_client is None:
        google_ads_client = GoogleAdsClient.load_from_storage(YAML_PATH)

    crit_svc = google_ads_client.get_service('SharedCriterionService')
    shared_set_svc = google_ads_client.get_service('SharedSetService')
    match_type_enum = google_ads_client.enums.KeywordMatchTypeEnum

    succeeded: list[dict] = []
    for gid, group in grouped.items():
        shared_set_resource = shared_set_svc.shared_set_path(customer_id, gid)
        ops = []
        for it in group:
            op = google_ads_client.get_type('SharedCriterionOperation')
            op.create.shared_set = shared_set_resource
            op.create.keyword.text = it['keyword_text']
            mt = it['match_type'].upper()
            if mt == 'EXACT':
                op.create.keyword.match_type = match_type_enum.EXACT
            elif mt == 'PHRASE':
                op.create.keyword.match_type = match_type_enum.PHRASE
            else:
                raise ValueError(f'unsupported match_type: {it["match_type"]!r}')
            ops.append(op)

        try:
            req = google_ads_client.get_type('MutateSharedCriteriaRequest')
            req.customer_id = str(customer_id)
            req.operations.extend(ops)
            req.partial_failure = True
            resp = crit_svc.mutate_shared_criteria(request=req)
        except GoogleAdsException as e:
            # Whole batch failed at the RPC layer — mark each item as failed
            err = _format_ads_exception(e)
            for it in group:
                failed.append({
                    'source_row_id': it['source_row_id'],
                    'source_table': it['source_table'],
                    'keyword_text': it['keyword_text'],
                    'match_type': it['match_type'],
                    'error': f'batch_failure: {err}',
                })
            continue

        # Parse per-op outcomes: resp.results[i] is populated for successes,
        # resp.partial_failure_error describes the per-op failures by index.
        per_op_errors = _parse_partial_failure(google_ads_client, resp)
        for idx, it in enumerate(group):
            if idx in per_op_errors:
                failed.append({
                    'source_row_id': it['source_row_id'],
                    'source_table': it['source_table'],
                    'keyword_text': it['keyword_text'],
                    'match_type': it['match_type'],
                    'error': per_op_errors[idx],
                })
            else:
                rn = resp.results[idx].resource_name
                # resource_name format: customers/{cid}/sharedCriteria/{set_id}~{crit_id}
                crit_id = rn.split('~')[-1] if '~' in rn else None
                succeeded.append({
                    'source_row_id': it['source_row_id'],
                    'source_table': it['source_table'],
                    'criterion_id': crit_id,
                    'resource_name': rn,
                    'keyword_text': it['keyword_text'],
                    'match_type': it['match_type'],
                })

    return {
        'succeeded': succeeded,
        'failed': failed,
        'ops_budget_remaining': DAILY_OP_BUDGET - ops_today - len(succeeded),
    }


# ---------------------------------------------------------------------------
# Low-level helpers for error parsing
# ---------------------------------------------------------------------------
def _format_ads_exception(e: GoogleAdsException) -> str:
    try:
        msgs = [f'{err.error_code}: {err.message}' for err in e.failure.errors]
        return '; '.join(msgs)[:400]
    except Exception:  # noqa: BLE001
        return str(e)[:400]


def _parse_partial_failure(client: GoogleAdsClient, response) -> dict[int, str]:
    """Return {operation_index: error_message} parsed from partial_failure_error."""
    result: dict[int, str] = {}
    pf = getattr(response, 'partial_failure_error', None)
    if not pf or not getattr(pf, 'details', None):
        return result

    # The GoogleAdsFailure detail is packed in an Any proto
    ga_failure_type = client.get_type('GoogleAdsFailure')
    for detail in pf.details:
        try:
            failure = type(ga_failure_type).deserialize(detail.value)
        except Exception:  # noqa: BLE001
            continue
        for err in failure.errors:
            idx = None
            # error.location.field_path_elements[0].index is the operation index
            fpe = list(err.location.field_path_elements or [])
            if fpe:
                idx = fpe[0].index
            if idx is None:
                continue
            result[idx] = f'{err.error_code}: {err.message}'[:400]
    return result


# ---------------------------------------------------------------------------
# Convenience: also expose a tiny helper to remove by resource_name (used by
# the probe script and potentially future cleanup flows)
# ---------------------------------------------------------------------------
def remove_shared_criteria(customer_id: str, resource_names: list[str],
                           google_ads_client: GoogleAdsClient | None = None) -> dict:
    if google_ads_client is None:
        google_ads_client = GoogleAdsClient.load_from_storage(YAML_PATH)
    crit_svc = google_ads_client.get_service('SharedCriterionService')
    ops = []
    for rn in resource_names:
        op = google_ads_client.get_type('SharedCriterionOperation')
        op.remove = rn
        ops.append(op)
    req = google_ads_client.get_type('MutateSharedCriteriaRequest')
    req.customer_id = str(customer_id)
    req.operations.extend(ops)
    req.partial_failure = True
    resp = crit_svc.mutate_shared_criteria(request=req)
    return {
        'results': [r.resource_name for r in resp.results],
        'partial_failure': str(getattr(resp, 'partial_failure_error', '') or ''),
    }
