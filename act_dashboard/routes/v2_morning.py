"""
ACT v2 Morning Review Route

Blueprint: v2_morning_bp, URL prefix: /v2
Pages:
    /v2/morning-review  — main dashboard
    /v2                 — redirect to /v2/morning-review

Aggregates approval/action/monitoring/alert data across ALL clients
(or filtered to one client via ?client=X).
Reads scheduler status from act_v2_scheduler_runs.
"""

import json
import os
from collections import defaultdict
from datetime import datetime, timedelta

import duckdb
from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

v2_morning_bp = Blueprint('v2_morning', __name__, url_prefix='/v2')

_WAREHOUSE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "warehouse.duckdb")
)


def _get_db():
    return duckdb.connect(_WAREHOUSE_PATH, read_only=True)


def _parse_json(val):
    if isinstance(val, str):
        try:
            return json.loads(val)
        except Exception:
            return None
    return val


@v2_morning_bp.route('/')
def v2_index():
    """v2 landing page redirects to Morning Review."""
    q = request.query_string.decode()
    return redirect('/v2/morning-review' + ('?' + q if q else ''))


@v2_morning_bp.route('/morning-review')
def morning_review():
    """Render the Morning Review dashboard."""
    client_filter = request.args.get('client', 'all')

    con = _get_db()
    try:
        # All active clients for switcher + badge rendering
        all_clients_rows = con.execute(
            "SELECT client_id, client_name FROM act_v2_clients WHERE active = TRUE ORDER BY client_name"
        ).fetchall()
        clients = [{'id': r[0], 'name': r[1]} for r in all_clients_rows]

        # Current client for switcher display
        if client_filter == 'all':
            current_client = {'id': 'all', 'name': 'All Clients'}
        else:
            row = con.execute(
                "SELECT client_id, client_name FROM act_v2_clients WHERE client_id = ?",
                [client_filter]
            ).fetchone()
            if not row:
                return f"Client '{client_filter}' not found", 404
            current_client = {'id': row[0], 'name': row[1]}

        client_id_to_name = {c['id']: c['name'] for c in clients}

        # Client filter clause (SQL)
        if client_filter == 'all':
            client_clause = ""
            client_params = []
        else:
            client_clause = " AND r.client_id = ?"
            client_params = [client_filter]

        # --------------------------------------------------------------
        # 1. AWAITING APPROVAL — pending recommendations
        # --------------------------------------------------------------
        rec_rows = con.execute(f"""
            SELECT r.recommendation_id, r.client_id, r.level, r.entity_name,
                   r.action_category, r.risk_level, r.summary, r.recommendation_text,
                   r.estimated_impact, r.decision_tree_json, r.identified_at,
                   r.current_value_json, r.proposed_value_json
            FROM act_v2_recommendations r
            WHERE r.status = 'pending' {client_clause}
            ORDER BY r.identified_at DESC
        """, client_params).fetchall()

        awaiting = []
        for r in rec_rows:
            awaiting.append({
                'id': r[0],
                'client_id': r[1],
                'client_name': client_id_to_name.get(r[1], r[1]),
                'level': r[2],
                'entity_name': r[3],
                'action_category': r[4],
                'risk_level': r[5],
                'summary': r[6],
                'recommendation_text': r[7],
                'estimated_impact': r[8],
                'decision_tree': _parse_json(r[9]),
                'identified_at': r[10],
                'current_value': _parse_json(r[11]),
                'proposed_value': _parse_json(r[12]),
            })

        # Group by level
        awaiting_by_level = defaultdict(list)
        for rec in awaiting:
            awaiting_by_level[rec['level']].append(rec)

        # --------------------------------------------------------------
        # 2. ACTIONS EXECUTED OVERNIGHT (last 24h)
        # --------------------------------------------------------------
        act_rows = con.execute(f"""
            SELECT r.action_id, r.client_id, r.level, r.entity_name,
                   r.action_type, r.before_value_json, r.after_value_json,
                   r.reason, r.executed_at, r.undo_requested_at
            FROM act_v2_executed_actions r
            WHERE r.execution_status = 'success'
            AND r.executed_at >= CURRENT_TIMESTAMP - INTERVAL 24 HOUR
            {client_clause}
            ORDER BY r.executed_at DESC
        """, client_params).fetchall()

        executed = []
        for r in act_rows:
            executed.append({
                'id': r[0],
                'client_id': r[1],
                'client_name': client_id_to_name.get(r[1], r[1]),
                'level': r[2],
                'entity_name': r[3],
                'action_type': r[4],
                'before': _parse_json(r[5]),
                'after': _parse_json(r[6]),
                'reason': r[7],
                'executed_at': r[8],
                'undo_requested_at': r[9],
            })

        executed_by_level = defaultdict(list)
        for a in executed:
            executed_by_level[a['level']].append(a)

        # --------------------------------------------------------------
        # 3. CURRENTLY MONITORING — resolved_at IS NULL
        # --------------------------------------------------------------
        mon_rows = con.execute(f"""
            SELECT r.monitoring_id, r.client_id, r.level, r.entity_id,
                   r.monitoring_type, r.started_at, r.ends_at,
                   r.health_status, r.consecutive_days_stable
            FROM act_v2_monitoring r
            WHERE r.resolved_at IS NULL {client_clause}
            ORDER BY r.started_at DESC
        """, client_params).fetchall()

        monitoring = []
        now = datetime.now()
        for r in mon_rows:
            started = r[5]
            ends = r[6]
            progress_pct = 0
            time_remaining = ''
            if started and ends:
                total = (ends - started).total_seconds()
                elapsed = (now - started).total_seconds() if started <= now else 0
                if total > 0:
                    progress_pct = round(min(100, max(0, elapsed / total * 100)), 1)
                remaining = ends - now
                if remaining.total_seconds() > 0:
                    hours = remaining.total_seconds() / 3600
                    if hours < 24:
                        time_remaining = f'{hours:.0f}h remaining'
                    else:
                        time_remaining = f'{hours / 24:.0f} days remaining'
                else:
                    time_remaining = 'Period ended'
            monitoring.append({
                'id': r[0],
                'client_id': r[1],
                'client_name': client_id_to_name.get(r[1], r[1]),
                'level': r[2],
                'entity_id': r[3],
                'type': r[4],
                'started_at': started,
                'ends_at': ends,
                'health': r[7],
                'stable_days': r[8],
                'progress_pct': progress_pct,
                'time_remaining': time_remaining,
            })

        monitoring_by_level = defaultdict(list)
        for m in monitoring:
            monitoring_by_level[m['level']].append(m)

        # --------------------------------------------------------------
        # 4. RECENT ALERTS (last 7 days)
        # --------------------------------------------------------------
        alert_rows = con.execute(f"""
            SELECT r.alert_id, r.client_id, r.level, r.alert_type, r.severity,
                   r.title, r.description, r.entity_id, r.raised_at,
                   r.resolved_at, r.resolution
            FROM act_v2_alerts r
            WHERE r.raised_at >= CURRENT_TIMESTAMP - INTERVAL 7 DAY
            {client_clause}
            ORDER BY r.raised_at DESC
        """, client_params).fetchall()

        alerts = []
        for r in alert_rows:
            alerts.append({
                'id': r[0],
                'client_id': r[1],
                'client_name': client_id_to_name.get(r[1], r[1]),
                'level': r[2],
                'type': r[3],
                'severity': r[4],
                'title': r[5],
                'description': r[6],
                'entity_id': r[7],
                'raised_at': r[8],
                'resolved_at': r[9],
                'resolution': r[10],
            })

        alerts_by_level = defaultdict(list)
        for a in alerts:
            alerts_by_level[a['level']].append(a)

        # --------------------------------------------------------------
        # 5. Stats summary
        # --------------------------------------------------------------
        stats = {
            'awaiting_count': len(awaiting),
            'alerts_count': len(alerts),
            'executed_count': len(executed),
            'monitoring_count': len(monitoring),
        }

        # --------------------------------------------------------------
        # 5b. N1b — Search-term review pending count (today's classifier)
        # --------------------------------------------------------------
        if client_filter == 'all':
            st_params = []
            st_clause = ''
        else:
            st_params = [client_filter]
            st_clause = ' AND client_id = ?'
        pending_search_term_count = con.execute(f"""
            SELECT COUNT(*) FROM act_v2_search_term_reviews
            WHERE analysis_date = CURRENT_DATE
              AND pass1_status IN ('block','review')
              AND review_status = 'pending'
              {st_clause}
        """, st_params).fetchone()[0]
        classified_search_term_count = con.execute(f"""
            SELECT COUNT(*) FROM act_v2_search_term_reviews
            WHERE analysis_date = CURRENT_DATE
              {st_clause}
        """, st_params).fetchone()[0]

        # --------------------------------------------------------------
        # 6. Scheduler status — "ACT last ran" + any failures today
        # --------------------------------------------------------------
        last_ran_row = con.execute("""
            SELECT MAX(completed_at) FROM act_v2_scheduler_runs
            WHERE status = 'success'
        """).fetchone()
        last_ran_raw = last_ran_row[0] if last_ran_row else None
        if last_ran_raw:
            if isinstance(last_ran_raw, datetime):
                last_ran = last_ran_raw.strftime('%d %b %Y, %H:%M')
            else:
                last_ran = str(last_ran_raw)
        else:
            last_ran = None

        # Running / failed status today
        today = datetime.now().strftime('%Y-%m-%d')
        status_rows = con.execute("""
            SELECT client_id, phase, status, error_message, started_at, completed_at
            FROM act_v2_scheduler_runs
            WHERE CAST(started_at AS DATE) = CURRENT_DATE
            ORDER BY started_at DESC
        """).fetchall()
        scheduler_today = []
        for r in status_rows:
            scheduler_today.append({
                'client_id': r[0],
                'client_name': client_id_to_name.get(r[0], r[0]),
                'phase': r[1],
                'status': r[2],
                'error': r[3],
                'started_at': r[4],
                'completed_at': r[5],
            })
        any_running = any(s['status'] == 'running' for s in scheduler_today)
        any_failed = any(s['status'] == 'failed' for s in scheduler_today)

        # Overnight impact summary (count + summed estimated savings if available)
        impact_total_actions = len(executed)
        # estimated_impact is free-text; can't sum. Just show action count.

        # Fix 1.6 — PMax CSV watcher activity (last 24h) for the banner.
        # We surface the most recent terminal row of each kind (failed first
        # for visibility, then most-recent ingested) so the template can
        # show a red banner OR a green pill, not both.
        csv_watch_failed = None
        csv_watch_ingested = None
        try:
            row = con.execute(
                """SELECT file_path, client_id, error_message, detected_at
                   FROM act_v2_csv_watch_log
                   WHERE status = 'failed'
                     AND detected_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
                   ORDER BY detected_at DESC LIMIT 1"""
            ).fetchone()
            if row:
                csv_watch_failed = {
                    'file_path': row[0],
                    'client_id': row[1],
                    'error_message': row[2],
                    'detected_at': row[3],
                }
        except Exception:
            # Table may not exist yet on a pre-N5 install — fail silent.
            pass
        try:
            row = con.execute(
                """SELECT file_path, client_id, rows_ingested, processed_at
                   FROM act_v2_csv_watch_log
                   WHERE status = 'ingested'
                     AND detected_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
                   ORDER BY detected_at DESC LIMIT 1"""
            ).fetchone()
            if row:
                csv_watch_ingested = {
                    'file_path': row[0],
                    'client_id': row[1],
                    'rows_ingested': row[2],
                    'processed_at': row[3],
                }
        except Exception:
            pass

    finally:
        con.close()

    return render_template(
        'v2/morning_review.html',
        client=current_client,
        clients=clients,
        awaiting_by_level=dict(awaiting_by_level),
        executed_by_level=dict(executed_by_level),
        monitoring_by_level=dict(monitoring_by_level),
        alerts_by_level=dict(alerts_by_level),
        awaiting=awaiting,
        executed=executed,
        monitoring=monitoring,
        alerts=alerts,
        stats=stats,
        last_ran=last_ran,
        scheduler_today=scheduler_today,
        any_running=any_running,
        any_failed=any_failed,
        impact_total_actions=impact_total_actions,
        pending_search_term_count=pending_search_term_count,
        classified_search_term_count=classified_search_term_count,
        csv_watch_failed=csv_watch_failed,
        csv_watch_ingested=csv_watch_ingested,
        active_page='morning-review',
    )


# ---------------------------------------------------------------------------
# Fix 1.6 follow-up — PMax CSV upload endpoint
# ---------------------------------------------------------------------------
# Drops the uploaded file into client_csvs/<client_id>/incoming/ and returns
# 200. Ingestion is NOT performed here — we deliberately route through the
# watcher so there's exactly one ingestion code path. The watcher's
# on_created event will fire ~immediately after the file lands and run the
# normal validate -> ingest -> archive pipeline.
@v2_morning_bp.route('/api/csv/upload', methods=['POST'])
def csv_upload():
    # Lazy import so the route module doesn't pull in watchdog at app
    # boot — watcher is a separate process; the Flask app only needs the
    # folder path helpers.
    from act_dashboard.data_pipeline.pmax_csv_watcher import (
        ensure_client_folders,
        incoming_dir,
    )

    client_id = (request.form.get('client_id') or '').strip()
    if not client_id:
        return jsonify({'status': 'error', 'message': 'client_id required'}), 400

    # Validate client_id against active clients (avoid path traversal via
    # crafted client_id and avoid accidental writes for inactive clients).
    con = _get_db()
    try:
        row = con.execute(
            "SELECT 1 FROM act_v2_clients WHERE client_id = ? AND active = TRUE",
            [client_id],
        ).fetchone()
    finally:
        con.close()
    if not row:
        return jsonify({
            'status': 'error',
            'message': f'unknown or inactive client_id: {client_id}',
        }), 400

    upload = request.files.get('file')
    if upload is None or not upload.filename:
        return jsonify({'status': 'error', 'message': 'file required'}), 400

    # secure_filename strips path components and unsafe chars; we still
    # constrain to .csv to keep the watcher's filter happy.
    fname = secure_filename(upload.filename)
    if not fname.lower().endswith('.csv'):
        return jsonify({
            'status': 'error',
            'message': 'only .csv files are accepted',
        }), 400

    # Ensure folders exist (idempotent — same helper the watcher uses).
    ensure_client_folders([client_id])
    target = incoming_dir(client_id) / fname

    # If the same name was uploaded earlier today, append _2, _3 etc. so
    # we don't clobber a CSV the watcher hasn't picked up yet.
    if target.exists():
        stem = target.stem
        suffix = target.suffix
        n = 2
        while True:
            candidate = target.with_name(f"{stem}_{n}{suffix}")
            if not candidate.exists():
                target = candidate
                break
            n += 1

    try:
        upload.save(str(target))
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'failed to save file: {e}',
        }), 500

    return jsonify({
        'status': 'ok',
        'client_id': client_id,
        'saved_as': target.name,
        'path': str(target),
    }), 200
