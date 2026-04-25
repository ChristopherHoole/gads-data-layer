"""Fetch context needed to render prompts: client config + row data.

Two responsibilities:
  - Client-level context for the system prompt's CLIENT CONTEXT section
  - Per-row context for the user prompt's term/phrase list

Order preservation in the row fetchers is critical — the classifier zips
input ids against Claude's response, so any reordering on the way out
of the DB would mis-attribute every verdict.
"""
from __future__ import annotations

from datetime import date, timedelta

# Sentinel for empty/null prompt-context fields (avoids prompt rendering
# either {{var}} literally or showing "None" in the system context).
_EMPTY = '(none specified)'


# ---------------------------------------------------------------------------
# Client-level context
# ---------------------------------------------------------------------------
def get_client_context(con, client_id: str) -> dict:
    """Return dict of values needed for the system-prompt CLIENT CONTEXT section.

    Returned keys (every value MUST be a string for prompt substitution):
        client_name, persona, target_cpa, service_area, clinic_location,
        services_advertised_csv, services_not_advertised_csv,
        brand_terms_csv, competitor_brands_csv, converters_last_30d_csv

    NOTE: client_id itself is NOT in the returned dict — the caller
    (classifier) merges it in at render time. Keeps responsibilities clean.
    """
    row = con.execute(
        """SELECT client_name, persona, target_cpa,
                  service_locations, services_advertised,
                  services_not_advertised, client_brand_terms
             FROM act_v2_clients
            WHERE client_id = ?""",
        [client_id],
    ).fetchone()
    if not row:
        # Caller validated existence upstream; defensive fallback so the
        # prompt still renders if the row vanished mid-flight.
        return {
            'client_name': _EMPTY,
            'persona': _EMPTY,
            'target_cpa': _EMPTY,
            'service_area': _EMPTY,
            'clinic_location': _EMPTY,
            'services_advertised_csv': _EMPTY,
            'services_not_advertised_csv': _EMPTY,
            'brand_terms_csv': _EMPTY,
            'competitor_brands_csv': _EMPTY,
            'converters_last_30d_csv': _EMPTY,
        }

    (client_name, persona, target_cpa,
     service_locations, services_advertised,
     services_not_advertised, client_brand_terms) = row

    # Competitor brands come from the negative_keyword_lists/keywords
    # tables — list_role = 'competitor_exact' or 'competitor_phrase'.
    # Cap the list length so we don't blow the system-prompt budget on
    # clients with hundreds of competitors.
    competitor_rows = con.execute(
        """SELECT DISTINCT k.keyword_text
             FROM act_v2_negative_list_keywords k
             JOIN act_v2_negative_keyword_lists l USING (list_id)
            WHERE l.client_id = ?
              AND l.list_role IN ('competitor_exact', 'competitor_phrase')
              AND k.keyword_text IS NOT NULL
            ORDER BY 1
            LIMIT 200""",
        [client_id],
    ).fetchall()
    competitor_brands_csv = ', '.join(r[0] for r in competitor_rows) or _EMPTY

    # Converters in the last 30 days: search_term where total_conversions > 0
    # in any review row whose analysis_date is within window. Cap at 200
    # — any one client should rarely cross that, and if they do, the
    # prompt budget matters more than completeness.
    cutoff = date.today() - timedelta(days=30)
    conv_rows = con.execute(
        """SELECT DISTINCT search_term
             FROM act_v2_search_term_reviews
            WHERE client_id = ?
              AND analysis_date >= ?
              AND total_conversions > 0
              AND search_term IS NOT NULL
            ORDER BY 1
            LIMIT 200""",
        [client_id, cutoff],
    ).fetchall()
    converters_csv = ', '.join(r[0] for r in conv_rows) or _EMPTY

    # service_locations is the CSV of postcodes/areas; clinic_location
    # isn't a separate column on act_v2_clients today, so use a pragmatic
    # fallback of the first listed location.
    service_area = (service_locations or '').strip() or _EMPTY
    clinic_location = service_area.split(',')[0].strip() if service_area != _EMPTY else _EMPTY

    return {
        'client_name': client_name or _EMPTY,
        'persona': persona or _EMPTY,
        'target_cpa': str(target_cpa) if target_cpa is not None else _EMPTY,
        'service_area': service_area,
        'clinic_location': clinic_location,
        'services_advertised_csv': (services_advertised or '').strip() or _EMPTY,
        'services_not_advertised_csv': (services_not_advertised or '').strip() or _EMPTY,
        'brand_terms_csv': (client_brand_terms or '').strip() or _EMPTY,
        'competitor_brands_csv': competitor_brands_csv,
        'converters_last_30d_csv': converters_csv,
    }


# ---------------------------------------------------------------------------
# Per-row context (block/review flows)
# ---------------------------------------------------------------------------
def get_review_rows(con, review_ids: list[int]) -> list[dict]:
    """Fetch per-row context for block/review flows.

    Order preservation: WHERE id IN (...) returns rows in arbitrary order.
    The classifier zips this output with Claude's parsed response — if
    order differs, every row gets the WRONG verdict. Reorder via dict
    keyed on review_id then iterate input list.

    Each returned dict:
        review_id, search_term, pass1_reason, pass1_reason_detail,
        total_cost, total_clicks, total_impressions, total_conversions,
        triggering_keywords (str or '—'), campaigns (str or '—')
    """
    if not review_ids:
        return []
    placeholders = ','.join(['?'] * len(review_ids))
    rows = con.execute(
        f"""SELECT r.id AS review_id,
                   r.search_term,
                   r.pass1_reason,
                   r.pass1_reason_detail,
                   r.total_cost,
                   r.total_clicks,
                   r.total_impressions,
                   r.total_conversions,
                   r.client_id,
                   r.first_seen_date,
                   r.last_seen_date
              FROM act_v2_search_term_reviews r
             WHERE r.id IN ({placeholders})""",
        review_ids,
    ).fetchall()

    base_by_id: dict[int, dict] = {}
    for r in rows:
        (rid, term, p1r, p1d, cost, clicks, impr, conv,
         client_id, fsd, lsd) = r
        base_by_id[rid] = {
            'review_id': rid,
            'search_term': term,
            'pass1_reason': p1r,
            'pass1_reason_detail': p1d,
            'total_cost': cost,
            'total_clicks': clicks,
            'total_impressions': impr,
            'total_conversions': conv,
            '_client_id': client_id,
            '_first_seen': fsd,
            '_last_seen': lsd,
        }

    # Triggering keywords + campaigns: aggregate from act_v2_search_terms
    # using the same join shape v2_negatives_api uses
    # (snapshot_date BETWEEN first_seen AND last_seen).
    if base_by_id:
        triggers = con.execute(
            f"""SELECT r.id,
                       STRING_AGG(DISTINCT NULLIF(st.keyword_text, ''), ', ')
                           FILTER (WHERE st.keyword_text IS NOT NULL),
                       STRING_AGG(DISTINCT NULLIF(st.campaign_name, ''), ', ')
                           FILTER (WHERE st.campaign_name IS NOT NULL)
                  FROM act_v2_search_term_reviews r
                  JOIN act_v2_search_terms st
                    ON st.client_id   = r.client_id
                   AND st.search_term = r.search_term
                   AND st.snapshot_date BETWEEN r.first_seen_date
                                            AND r.last_seen_date
                 WHERE r.id IN ({placeholders})
                 GROUP BY r.id""",
            review_ids,
        ).fetchall()
        for rid, kws, camps in triggers:
            d = base_by_id.get(rid)
            if d is not None:
                d['triggering_keywords'] = kws or '—'
                d['campaigns'] = camps or '—'

    out: list[dict] = []
    for rid in review_ids:
        d = base_by_id.get(rid)
        if d is None:
            continue  # validated upstream — rare race condition
        d.setdefault('triggering_keywords', '—')
        d.setdefault('campaigns', '—')
        # Strip private keys before returning
        for k in ('_client_id', '_first_seen', '_last_seen'):
            d.pop(k, None)
        out.append(d)
    return out


# ---------------------------------------------------------------------------
# Per-row context (pass3 flow)
# ---------------------------------------------------------------------------
def get_phrase_suggestion_rows(con, phrase_suggestion_ids: list[int]
                                ) -> list[dict]:
    """Fetch per-row context for pass3 flow. Order-preserving."""
    if not phrase_suggestion_ids:
        return []
    placeholders = ','.join(['?'] * len(phrase_suggestion_ids))
    rows = con.execute(
        f"""SELECT id AS phrase_id, fragment, word_count, occurrence_count,
                   risk_level, target_list_role
              FROM act_v2_phrase_suggestions
             WHERE id IN ({placeholders})""",
        phrase_suggestion_ids,
    ).fetchall()
    by_id = {
        r[0]: {
            'phrase_id': r[0],
            'fragment': r[1],
            'word_count': r[2],
            'occurrence_count': r[3],
            'risk_level': r[4],
            'engine_suggested_target_list_role': r[5],
        }
        for r in rows
    }
    return [by_id[i] for i in phrase_suggestion_ids if i in by_id]


# ---------------------------------------------------------------------------
# User-prompt formatters
# ---------------------------------------------------------------------------
def render_term_list(rows: list[dict]) -> str:
    """Format block/review rows for the user prompt per scope §7.3.

    NULL numeric coercion (`or 0`) handles early-ingestion rows where
    cost/clicks could be NULL.
    """
    out: list[str] = []
    for r in rows:
        cost = r.get('total_cost') or 0
        clicks = r.get('total_clicks') or 0
        impressions = r.get('total_impressions') or 0
        conversions = r.get('total_conversions') or 0
        out.append(f'[{r["review_id"]}] "{r["search_term"]}"')
        out.append(
            f'    pass1_reason: {r.get("pass1_reason") or "—"} '
            f'/ detail: {r.get("pass1_reason_detail") or "—"}'
        )
        out.append(
            f'    cost: £{float(cost):.2f} | clicks: {clicks} '
            f'| impressions: {impressions} | conversions: {conversions}'
        )
        out.append(
            f'    triggered by keyword: "{r.get("triggering_keywords") or "—"}"'
        )
        out.append(f'    campaigns: {r.get("campaigns") or "—"}')
        out.append('')  # blank separator
    return '\n'.join(out).rstrip()


def render_phrase_list(rows: list[dict]) -> str:
    """Format pass3 rows for the user prompt."""
    out: list[str] = []
    for r in rows:
        out.append(
            f'[{r["phrase_id"]}] "{r["fragment"]}" '
            f'(word_count: {r["word_count"]}, '
            f'occurrence_count: {r["occurrence_count"]}, '
            f'risk_level: {r["risk_level"]}, '
            f'engine_suggested: {r["engine_suggested_target_list_role"]})'
        )
    return '\n'.join(out)
