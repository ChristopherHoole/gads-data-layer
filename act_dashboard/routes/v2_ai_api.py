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

    con = _db()
    try:
        try:
            _validate_client_id(con, body.get('client_id'))
            _parse_analysis_date(body.get('analysis_date'))
            _validate_flow(flow)
            force_reclassify = _validate_bool(
                body.get('force_reclassify'), 'force_reclassify', default=False,
            )
            if flow == 'pass3':
                if phrase_ids_raw is None:
                    return _err('pass3 flow requires phrase_suggestion_ids')
                _validate_id_list(phrase_ids_raw, 'phrase_suggestion_ids')
            else:
                if review_ids_raw is None:
                    return _err(f'{flow} flow requires review_ids')
                _validate_id_list(review_ids_raw, 'review_ids')
        except ValueError as e:
            return _err(str(e))
    finally:
        con.close()

    # TODO Stage 4: acquire shared per-client lock (keyed on client_id, shared
    #               with explain-row + chat); return 409 on contention.
    # TODO Stage 4: 30s in-memory idempotency cache keyed on hash(ids + prompt_version).
    # TODO Stage 4: subprocess.run(['claude', '-p', '--output-format', 'json',
    #               '--model', 'claude-sonnet-4-6'], ...).
    # TODO Stage 4: filter out already-classified rows where (source_id,
    #               prompt_version) exists, unless force_reclassify=true.
    # TODO Stage 4: persist results to act_v2_ai_classifications, errors to
    #               act_v2_ai_errors.
    _ = force_reclassify  # silenced until Stage 4 consumes it
    return jsonify({
        'classified': 0,
        'results': [],
        'skipped_already_classified': 0,
        'tokens_used': 0,
        'wall_clock_ms': 0,
        'stub': True,
    }), 200


# ---------------------------------------------------------------------------
# POST /explain-row
# ---------------------------------------------------------------------------
@v2_ai_api_bp.route('/explain-row', methods=['POST'])
def explain_row():
    body = request.get_json(silent=True) or {}
    review_id = body.get('review_id')
    question = body.get('question')

    con = _db()
    try:
        try:
            _validate_client_id(con, body.get('client_id'))
            if isinstance(review_id, bool) or not isinstance(review_id, int):
                raise ValueError('review_id required, integer')
            row = con.execute(
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
        except ValueError as e:
            return _err(str(e))
    finally:
        con.close()

    # TODO Stage 5: acquire shared per-client lock (same lock as classify-terms + chat).
    # TODO Stage 5: subprocess.run with --model claude-opus-4-7.
    # TODO Stage 5: persist user question + assistant response to
    #               act_v2_ai_chat_log with related_review_id set.
    return jsonify({
        'review_id': review_id,
        'explanation': '<stub: deep reasoning will appear here>',
        'model_version': 'stub',
        'tokens_used': 0,
        'wall_clock_ms': 0,
        'chat_log_id': None,
        'stub': True,
    }), 200


# ---------------------------------------------------------------------------
# POST /chat
# ---------------------------------------------------------------------------
@v2_ai_api_bp.route('/chat', methods=['POST'])
def chat():
    body = request.get_json(silent=True) or {}
    message = body.get('message')

    con = _db()
    try:
        try:
            _validate_client_id(con, body.get('client_id'))
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
        con.close()

    # TODO Stage 4/9: acquire shared per-client lock (same lock as classify-terms + explain-row).
    # TODO Stage 4/9: subprocess.run with --model claude-sonnet-4-6 + chat_v1.txt system prompt.
    # TODO Stage 4/9: persist user message + assistant response to act_v2_ai_chat_log.
    return jsonify({
        'response': '<stub: chat response will appear here>',
        'model_version': 'stub',
        'tokens_used': 0,
        'wall_clock_ms': 0,
        'chat_log_id': None,
        'stub': True,
    }), 200


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
    finally:
        con.close()

    # TODO Stage 9: SELECT id, role, message, model_version, related_review_id,
    #               created_at FROM act_v2_ai_chat_log
    #               WHERE client_id=? AND flow=? AND analysis_date=?
    #                 AND cleared_at IS NULL
    #               ORDER BY created_at DESC LIMIT ?  -- then reverse for
    #               chronological render
    _ = limit  # silenced until Stage 9 consumes it
    return jsonify({
        'messages': [],
        'stub': True,
    }), 200
