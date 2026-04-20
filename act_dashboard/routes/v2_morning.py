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
from flask import Blueprint, render_template, request, redirect, url_for

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
        active_page='morning-review',
    )
