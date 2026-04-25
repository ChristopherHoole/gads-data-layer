"""Tier 2.1 Stage 2 — AI endpoints (stub scaffolding).

Blueprint: v2_ai_api, URL prefix /v2/api/ai.

Endpoints (all CSRF-exempt, JSON in/out):
  POST /classify-terms     classify a batch of review or pass3 ids
  POST /explain-row        deep reasoning for one review row
  POST /chat               flow-scoped AI chat
  GET  /chat-history       chat replay for a (client, flow, date)

This file is intentionally STUBS ONLY. Validation is full-strength —
shape/schema rejection here keeps the request contract honest before
Stage 4/5 wire Claude in. Stub responses include "stub": true so callers
can spot-check they hit the scaffold; that flag goes away when real
classification + chat lands.

Mirrors v2_negatives_api.py for connection, logging, and Blueprint shape.
The brief specifies a {"error": "<reason>"} response on validation
failure (single-key), distinct from the negatives module's
{"error": code, "detail": detail} shape — using the brief's shape here
since the AI surface is new.
"""
from __future__ import annotations

import logging
import os
from datetime import date, datetime

import duckdb
from flask import Blueprint, jsonify, request

from act_dashboard.ai import chatter, classifier, explainer
from act_dashboard.ai.claude_subprocess import ClaudeError
from act_dashboard.ai.locks import LockContentionError

v2_ai_api_bp = Blueprint('v2_ai_api', __name__, url_prefix='/v2/api/ai')

logger = logging.getLogger('act_v2_ai_api')

_WAREHOUSE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'warehouse.duckdb')
)

_VALID_FLOWS = {
    'search_block', 'search_review',
    'pmax_block', 'pmax_review',
    'pass3',
}

_MAX_BATCH_IDS = 500
_MAX_QUESTION_CHARS = 1000
_MAX_MESSAGE_CHARS = 4000
_MIN_MESSAGE_CHARS = 1
_DEFAULT_HISTORY_LIMIT = 50
_MAX_HISTORY_LIMIT = 500


# ---------------------------------------------------------------------------
# Connection + error helpers
# ---------------------------------------------------------------------------
def _db():
    return duckdb.connect(_WAREHOUSE_PATH, read_only=True)


def _err(message: str, http: int = 400):
    """Brief-spec error shape: {"error": "<reason>"}."""
    return jsonify({'error': message}), http


# ---------------------------------------------------------------------------
# Shared validators (raise ValueError; callers translate to 400)
# ---------------------------------------------------------------------------
def _validate_client_id(con, client_id) -> None:
    if not client_id or not isinstance(client_id, str):
        raise ValueError('client_id required')
    row = con.execute(
        "SELECT 1 FROM act_v2_clients WHERE client_id = ?",
        [client_id],
    ).fetchone()
    if not row:
        raise ValueError(f'unknown client_id: {client_id}')


def _validate_flow(flow) -> None:
    if not flow or not isinstance(flow, str):
        raise ValueError('flow required')
    if flow not in _VALID_FLOWS:
        raise ValueError(
            f'flow must be one of {sorted(_VALID_FLOWS)} (got {flow!r})'
        )


def _parse_analysis_date(raw) -> date:
    if not raw or not isinstance(raw, str):
        raise ValueError('analysis_date required (YYYY-MM-DD)')
    try:
        return datetime.strptime(raw, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError(
            f'analysis_date must be YYYY-MM-DD (got {raw!r})'
        )


def _validate_id_list(arr, name: str) -> list[int]:
    if not isinstance(arr, list) or not arr:
        raise ValueError(f'{name} required, non-empty list of ints')
    if len(arr) > _MAX_BATCH_IDS:
        raise ValueError(
            f'{name} length {len(arr)} exceeds max {_MAX_BATCH_IDS}'
        )
    out: list[int] = []
    for v in arr:
        # JSON booleans are also instance of int in Python — exclude them.
        if isinstance(v, bool) or not isinstance(v, int):
            raise ValueError(f'{name} entries must be ints (got {v!r})')
        out.append(v)
    return out


def _validate_bool(val, name: str, default: bool = False) -> bool:
    if val is None:
        return default
    if not isinstance(val, bool):
        raise ValueError(f'{name} must be a JSON boolean (got {type(val).__name__})')
    return val


# ---------------------------------------------------------------------------
# POST /classify-terms
# ---------------------------------------------------------------------------
@v2_ai_api_bp.route('/classify-terms', methods=['POST'])
def classify_terms():
    body = request.get_json(silent=True) or {}
    flow = body.get('flow')
    review_ids_raw = body.get('review_ids')
    phrase_ids_raw = body.get('phrase_suggestion_ids')

    # Both id arrays present is invalid regardless of flow.
    if review_ids_raw is not None and phrase_ids_raw is not None:
        return _err('review_ids and phrase_suggestion_ids are mutually exclusive')
    if review_ids_raw is None and phrase_ids_raw is None:
        return _err('one of review_ids or phrase_suggestion_ids is required')

    # Stage 4: validate against a read-only DB; the orchestrator opens its
    # own read-write connection below for the actual classify+persist.
    val_con = _db()
    try:
        try:
            _validate_client_id(val_con, body.get('client_id'))
            _parse_analysis_date(body.get('analysis_date'))
            _validate_flow(flow)
            force_reclassify = _validate_bool(
                body.get('force_reclassify'), 'force_reclassify', default=False,
            )
            if flow == 'pass3':
                if phrase_ids_raw is None:
                    return _err('pass3 flow requires phrase_suggestion_ids')
                ids = _validate_id_list(phrase_ids_raw, 'phrase_suggestion_ids')
            else:
                if review_ids_raw is None:
                    return _err(f'{flow} flow requires review_ids')
                ids = _validate_id_list(review_ids_raw, 'review_ids')
        except ValueError as e:
            return _err(str(e))
    finally:
        val_con.close()

    client_id = body['client_id']
    analysis_date = body['analysis_date']

    # Stage 4: open a read-write connection for the classifier (it INSERTs
    # to act_v2_ai_classifications + act_v2_ai_errors) and own the
    # lifecycle here so the orchestrator stays connection-agnostic.
    con = duckdb.connect(_WAREHOUSE_PATH)
    try:
        result = classifier.classify_batch(
            con,
            client_id=client_id,
            analysis_date=analysis_date,
            flow=flow,
            ids=ids,
            force_reclassify=force_reclassify,
        )
        return jsonify(result), 200
    except LockContentionError as e:
        return jsonify({
            'error': 'another classify batch is in flight for this client',
            'client_id': e.client_id,
        }), 409
    except ClaudeError as e:
        logger.error(
            'classify_terms ClaudeError: type=%s msg=%s',
            e.error_type, str(e)[:300],
        )
        return jsonify({
            'error': 'AI classification failed',
            'error_type': e.error_type,
        }), 502
    finally:
        con.close()


# ---------------------------------------------------------------------------
# POST /explain-row
# ---------------------------------------------------------------------------
@v2_ai_api_bp.route('/explain-row', methods=['POST'])
def explain_row():
    body = request.get_json(silent=True) or {}
    review_id = body.get('review_id')
    question = body.get('question')

    val_con = _db()
    try:
        try:
            _validate_client_id(val_con, body.get('client_id'))
            if isinstance(review_id, bool) or not isinstance(review_id, int):
                raise ValueError('review_id required, integer')
            row = val_con.execute(
                "SELECT 1 FROM act_v2_search_term_reviews WHERE id = ?",
                [review_id],
            ).fetchone()
            if not row:
                raise ValueError(f'unknown review_id: {review_id}')
            if question is not None:
                if not isinstance(question, str):
                    raise ValueError('question must be a string')
                if len(question) > _MAX_QUESTION_CHARS:
                    raise ValueError(
                        f'question max {_MAX_QUESTION_CHARS} chars (got {len(question)})'
                    )
            # Stage 5: flow + analysis_date are required for chat_log persistence.
            # Extends the existing block — Stage 2 fields above remain authoritative.
            _validate_flow(body.get('flow'))
            _parse_analysis_date(body.get('analysis_date'))
        except ValueError as e:
            return _err(str(e))
    finally:
        val_con.close()

    client_id = body['client_id']
    flow = body['flow']
    analysis_date = body['analysis_date']

    # Read-write connection for the explainer (it INSERTs to
    # act_v2_ai_chat_log + act_v2_ai_errors). Same lifecycle pattern as
    # classify-terms.
    con = duckdb.connect(_WAREHOUSE_PATH)
    try:
        result = explainer.explain_row(
            con,
            client_id=client_id,
            review_id=review_id,
            flow=flow,
            analysis_date=analysis_date,
            question=question,
        )
        return jsonify(result), 200
    except LockContentionError as e:
        return jsonify({
            'error': 'another AI call is in flight for this client',
            'client_id': e.client_id,
        }), 409
    except ClaudeError as e:
        logger.error(
            'explain_row ClaudeError: type=%s msg=%s',
            e.error_type, str(e)[:300],
        )
        return jsonify({
            'error': 'AI explanation failed',
            'error_type': e.error_type,
        }), 502
    finally:
        con.close()


# ---------------------------------------------------------------------------
# POST /chat
# ---------------------------------------------------------------------------
@v2_ai_api_bp.route('/chat', methods=['POST'])
def chat():
    body = request.get_json(silent=True) or {}
    message = body.get('message')

    val_con = _db()
    try:
        try:
            _validate_client_id(val_con, body.get('client_id'))
            _validate_flow(body.get('flow'))
            _parse_analysis_date(body.get('analysis_date'))
            if not isinstance(message, str):
                raise ValueError('message required, string')
            if len(message) < _MIN_MESSAGE_CHARS or len(message) > _MAX_MESSAGE_CHARS:
                raise ValueError(
                    f'message length must be {_MIN_MESSAGE_CHARS}–'
                    f'{_MAX_MESSAGE_CHARS} chars (got {len(message)})'
                )
        except ValueError as e:
            return _err(str(e))
    finally:
        val_con.close()

    client_id = body['client_id']
    flow = body['flow']
    analysis_date = body['analysis_date']

    # Stage 9 — read-write connection for the chatter (it INSERTs to
    # act_v2_ai_chat_log + act_v2_ai_errors). Same lifecycle pattern as
    # classify-terms / explain-row.
    con = duckdb.connect(_WAREHOUSE_PATH)
    try:
        result = chatter.chat(
            con,
            client_id=client_id,
            flow=flow,
            analysis_date=analysis_date,
            message=message,
        )
        return jsonify(result), 200
    except LockContentionError as e:
        return jsonify({
            'error': 'another AI call is in flight for this client',
            'client_id': e.client_id,
        }), 409
    except ClaudeError as e:
        logger.error(
            'chat ClaudeError: type=%s msg=%s',
            e.error_type, str(e)[:300],
        )
        return jsonify({
            'error': 'AI chat failed',
            'error_type': e.error_type,
        }), 502
    finally:
        con.close()


# ---------------------------------------------------------------------------
# GET /chat-history
# ---------------------------------------------------------------------------
@v2_ai_api_bp.route('/chat-history', methods=['GET'])
def chat_history():
    con = _db()
    try:
        try:
            _validate_client_id(con, request.args.get('client_id'))
            _validate_flow(request.args.get('flow'))
            _parse_analysis_date(request.args.get('analysis_date'))
            limit_raw = request.args.get('limit')
            if limit_raw is None or limit_raw == '':
                limit = _DEFAULT_HISTORY_LIMIT
            else:
                try:
                    limit = int(limit_raw)
                except (TypeError, ValueError):
                    raise ValueError('limit must be an integer')
                if limit < 1 or limit > _MAX_HISTORY_LIMIT:
                    raise ValueError(
                        f'limit must be in [1, {_MAX_HISTORY_LIMIT}] (got {limit})'
                    )
        except ValueError as e:
            return _err(str(e))

        client_id = request.args['client_id']
        flow = request.args['flow']
        analysis_date = request.args['analysis_date']

        rows = con.execute(
            """SELECT id, role, message, model_version,
                      related_review_id, created_at
                 FROM act_v2_ai_chat_log
                WHERE client_id = ?
                  AND flow = ?
                  AND analysis_date = ?
                  AND cleared_at IS NULL
                ORDER BY created_at DESC
                LIMIT ?""",
            [client_id, flow, analysis_date, limit],
        ).fetchall()
    finally:
        con.close()

    # Reverse for chronological render (oldest first) — the LIMIT keeps
    # the most-recent N; we just need to flip the order back on the way out.
    messages = [
        {
            'id': r[0],
            'role': r[1],
            'message': r[2],
            'model_version': r[3],
            'related_review_id': r[4],
            'created_at': r[5].isoformat() if r[5] else None,
        }
        for r in reversed(rows)
    ]
    return jsonify({'messages': messages}), 200


# ---------------------------------------------------------------------------
# POST /chat-clear — soft-delete all messages for a (client, flow, date).
# ---------------------------------------------------------------------------
# DuckDB UPDATE caution: cleared_at is NOT in any UNIQUE constraint
# (per Stage 1 schema), so this UPDATE is safe — the project-memory
# false-positive PK bug only fires on UNIQUE-constrained columns.
@v2_ai_api_bp.route('/chat-clear', methods=['POST'])
def chat_clear():
    body = request.get_json(silent=True) or {}
    val_con = _db()
    try:
        try:
            _validate_client_id(val_con, body.get('client_id'))
            _validate_flow(body.get('flow'))
            _parse_analysis_date(body.get('analysis_date'))
        except ValueError as e:
            return _err(str(e))
    finally:
        val_con.close()

    client_id = body['client_id']
    flow = body['flow']
    analysis_date = body['analysis_date']

    con = duckdb.connect(_WAREHOUSE_PATH)
    try:
        con.execute(
            """UPDATE act_v2_ai_chat_log
                  SET cleared_at = CURRENT_TIMESTAMP
                WHERE client_id = ? AND flow = ? AND analysis_date = ?
                  AND cleared_at IS NULL""",
            [client_id, flow, analysis_date],
        )
        return jsonify({'cleared': True}), 200
    finally:
        con.close()
