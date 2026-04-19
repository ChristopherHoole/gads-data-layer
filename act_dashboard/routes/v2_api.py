"""
ACT v2 Shared API Routes

Endpoints used by ALL level pages (Account, Campaign, etc.)
- Approve/decline recommendations
"""

import os
import threading
from datetime import datetime

import duckdb
from flask import Blueprint, request, jsonify

v2_api_bp = Blueprint('v2_api', __name__, url_prefix='/v2/api')

_WAREHOUSE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "warehouse.duckdb")
)

# Serialize writes within this Flask process to avoid DuckDB UPDATE races
# (DuckDB implements UPDATE as DELETE+INSERT; concurrent writers on the same
# row raise a PK-constraint or tuple-deletion conflict).
_write_lock = threading.Lock()


def _get_db():
    return duckdb.connect(_WAREHOUSE_PATH)


@v2_api_bp.route('/recommendations/<int:rec_id>/approve', methods=['POST'])
def approve_recommendation(rec_id):
    """Approve a recommendation (idempotent: no-op if already actioned)."""
    with _write_lock:
        con = _get_db()
        try:
            con.execute("""
                UPDATE act_v2_recommendations
                SET status = 'approved', actioned_at = CURRENT_TIMESTAMP, actioned_by = 'user'
                WHERE recommendation_id = ? AND status = 'pending'
            """, [rec_id])
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            con.close()


@v2_api_bp.route('/recommendations/<int:rec_id>/decline', methods=['POST'])
def decline_recommendation(rec_id):
    """Decline a recommendation (idempotent: no-op if already actioned)."""
    with _write_lock:
        con = _get_db()
        try:
            con.execute("""
                UPDATE act_v2_recommendations
                SET status = 'declined', actioned_at = CURRENT_TIMESTAMP, actioned_by = 'user'
                WHERE recommendation_id = ? AND status = 'pending'
            """, [rec_id])
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            con.close()


@v2_api_bp.route('/recommendations/bulk-approve', methods=['POST'])
def bulk_approve_recommendations():
    """Approve multiple recommendations in one call.

    Payload: {"ids": [1, 2, 3]}
    Returns: {"success": true, "results": [{"id": 1, "success": true}, ...]}
    """
    data = request.get_json() or {}
    ids = data.get('ids', [])
    if not isinstance(ids, list) or not ids:
        return jsonify({'success': False, 'error': 'ids must be a non-empty list'}), 400

    results = []
    with _write_lock:
        con = _get_db()
        try:
            for rec_id in ids:
                try:
                    con.execute("""
                        UPDATE act_v2_recommendations
                        SET status = 'approved', actioned_at = CURRENT_TIMESTAMP, actioned_by = 'user'
                        WHERE recommendation_id = ? AND status = 'pending'
                    """, [rec_id])
                    results.append({'id': rec_id, 'success': True})
                except Exception as e:
                    results.append({'id': rec_id, 'success': False, 'error': str(e)[:200]})
            return jsonify({'success': True, 'results': results})
        finally:
            con.close()


@v2_api_bp.route('/actions/<int:action_id>/undo-request', methods=['POST'])
def undo_request_action(action_id):
    """Mark an executed action as undo-requested (DB flag only, no API revert).

    The actual Google Ads API revert will be implemented in the G-series
    (execution/rollback layer). For now, this endpoint only sets the
    undo_requested_at timestamp so the UI can show an "Undo requested" state.
    """
    con = _get_db()
    try:
        con.execute("""
            UPDATE act_v2_executed_actions
            SET undo_requested_at = CURRENT_TIMESTAMP
            WHERE action_id = ?
        """, [action_id])
        return jsonify({
            'success': True,
            'note': 'Undo marked in DB. Google Ads API revert will land with G-series.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Campaign slide-in data blob — used by /v2/account campaign name clicks.
# Returns everything needed to render the 10 body sections.
# ---------------------------------------------------------------------------
import json as _json
from calendar import monthrange
from datetime import datetime as _dt, timedelta as _td


def _parse_metrics(m):
    if isinstance(m, str):
        try:
            return _json.loads(m)
        except Exception:
            return {}
    return m or {}


def _safe_div(n, d):
    return (n / d) if d else 0.0


ROLE_LABEL = {'BD': 'Brand Defence', 'CP': 'Core Performance', 'RT': 'Retargeting',
              'PR': 'Prospecting', 'TS': 'Testing'}


@v2_api_bp.route('/account/campaign-slidein/<client_id>/<campaign_id>')
def campaign_slidein_data(client_id, campaign_id):
    """Return all data needed to render the campaign slide-in on /v2/account."""
    con = duckdb.connect(_WAREHOUSE_PATH, read_only=True)
    try:
        # Client context
        crow = con.execute(
            """SELECT client_name, persona, monthly_budget, target_cpa, target_roas
               FROM act_v2_clients WHERE client_id = ?""", [client_id]
        ).fetchone()
        if not crow:
            return jsonify({'success': False, 'error': 'client not found'}), 404
        client_name, persona, monthly_budget, target_cpa, target_roas = crow
        monthly_budget = float(monthly_budget or 0)
        target_cpa = float(target_cpa) if target_cpa else None
        target_roas = float(target_roas) if target_roas else None

        # Latest snapshot date
        latest = con.execute(
            "SELECT MAX(snapshot_date) FROM act_v2_snapshots WHERE client_id = ? AND level='campaign'",
            [client_id]
        ).fetchone()[0]
        if not latest:
            return jsonify({'success': False, 'error': 'no snapshots'}), 404
        if isinstance(latest, str):
            latest = _dt.strptime(latest, '%Y-%m-%d').date()
        mtd_start = latest.replace(day=1)

        # Pull last 60 days for this campaign
        start_60 = latest - _td(days=60)
        rows = con.execute(
            """SELECT snapshot_date, entity_name, metrics_json
               FROM act_v2_snapshots
               WHERE client_id = ? AND level='campaign' AND entity_id = ?
               AND snapshot_date BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
               ORDER BY snapshot_date""",
            [client_id, campaign_id, str(start_60), str(latest)]
        ).fetchall()
        if not rows:
            return jsonify({'success': False, 'error': 'campaign not found'}), 404

        snaps = [{'date': str(r[0]), 'name': r[1], 'm': _parse_metrics(r[2])} for r in rows]
        campaign_name = snaps[-1]['name']

        def window_agg(days_back):
            cutoff = str(latest - _td(days=days_back))
            ws = [s for s in snaps if s['date'] > cutoff]
            return (sum(s['m'].get('cost', 0) for s in ws),
                    sum(s['m'].get('conversions', 0) for s in ws),
                    sum(s['m'].get('conversion_value', 0) for s in ws))

        # MTD
        mtd_snaps = [s for s in snaps if s['date'] >= str(mtd_start)]
        mtd_cost = sum(s['m'].get('cost', 0) for s in mtd_snaps)
        mtd_conv = sum(s['m'].get('conversions', 0) for s in mtd_snaps)
        cpa_mtd = mtd_cost / mtd_conv if mtd_conv > 0 else None

        # Latest snapshot metrics for header meta
        latest_m = snaps[-1]['m']
        status = latest_m.get('campaign_status', 'UNKNOWN').lower()
        bid_strategy = latest_m.get('bid_strategy_type', '')
        daily_budget = latest_m.get('budget_amount', 0)

        # Role
        role_row = con.execute(
            "SELECT role FROM act_v2_campaign_roles WHERE client_id=? AND google_ads_campaign_id=?",
            [client_id, campaign_id]
        ).fetchone()
        role = role_row[0] if role_row else None

        # Deviation threshold
        dev_row = con.execute(
            "SELECT setting_value FROM act_v2_client_settings WHERE client_id=? AND setting_key='deviation_threshold_pct'",
            [client_id]
        ).fetchone()
        deviation = int(dev_row[0]) if dev_row and dev_row[0] else 10

        # CPA zone
        cpa_zone = None
        cpa_detail = None
        if cpa_mtd and target_cpa:
            pct = round(abs(cpa_mtd - target_cpa) / target_cpa * 100)
            if cpa_mtd < target_cpa * (1 - deviation / 100):
                cpa_zone, cpa_detail = 'outperforming', f'{pct}% below'
            elif cpa_mtd > target_cpa * (1 + deviation / 100):
                cpa_zone, cpa_detail = 'underperforming', f'{pct}% above'
            else:
                cpa_zone, cpa_detail = 'ontarget', 'On target'

        # Projection
        days_in_month = monthrange(latest.year, latest.month)[1]
        days_elapsed = (latest - mtd_start).days + 1
        projected_conv = round(mtd_conv / days_elapsed * days_in_month) if days_elapsed > 0 and mtd_conv > 0 else None

        # Health section
        health = {
            'cost_mtd': round(mtd_cost, 2),
            'cpa': round(cpa_mtd, 2) if cpa_mtd else None,
            'cpa_zone': cpa_zone,
            'cpa_detail': cpa_detail,
            'target_cpa': target_cpa,
            'conversions_mtd': round(mtd_conv, 1),
            'projected_conv': projected_conv,
            'qs_avg': None,  # QS per-campaign aggregation TBD; placeholder for now
        }

        # Score breakdown — same math as AccountLevelEngine (lead_gen persona only for now)
        w7 = 0.5; w14 = 0.3; w30 = 0.2
        for key, wt in (('performance_scoring_weight_7d', None), ('performance_scoring_weight_14d', None), ('performance_scoring_weight_30d', None)):
            row = con.execute("SELECT setting_value FROM act_v2_client_settings WHERE client_id=? AND setting_key=?", [client_id, key]).fetchone()
            if row and row[0]:
                v = int(row[0]) / 100.0
                if key.endswith('7d'): w7 = v
                elif key.endswith('14d'): w14 = v
                elif key.endswith('30d'): w30 = v

        def window_score(days_back):
            cost, conv, _ = window_agg(days_back)
            if persona == 'lead_gen_cpa' and target_cpa:
                if conv > 0:
                    cpa = cost / conv
                    return round((target_cpa - cpa) / target_cpa * 100, 1), round(cpa, 2)
                elif cost > 0:
                    return -100.0, None
                return 0.0, None
            elif persona == 'ecommerce_roas' and target_roas:
                cost, _, cv = window_agg(days_back)
                if cost > 0:
                    roas = cv / cost
                    return round((roas - target_roas) / target_roas * 100, 1), round(roas, 2)
                return 0.0, None
            return 0.0, None

        s7, m7 = window_score(7)
        s14, m14 = window_score(14)
        s30, m30 = window_score(30)
        final = round(s7 * w7 + s14 * w14 + s30 * w30, 1)
        metric_label = 'CPA' if persona == 'lead_gen_cpa' else 'ROAS'
        metric_unit = '£' if persona == 'lead_gen_cpa' else 'x'
        score = {
            'current': final,
            'breakdown': [
                {'label': f'7-day {metric_label} vs target', 'points': s7, 'weight_pct': round(w7 * 100), 'metric': m7, 'metric_unit': metric_unit},
                {'label': f'14-day {metric_label} vs target', 'points': s14, 'weight_pct': round(w14 * 100), 'metric': m14, 'metric_unit': metric_unit},
                {'label': f'30-day {metric_label} vs target', 'points': s30, 'weight_pct': round(w30 * 100), 'metric': m30, 'metric_unit': metric_unit},
            ],
            'interpretation': (
                'Outperforming — eligible for budget increase.' if final > 20 else
                'Underperforming — candidate for budget reduction.' if final < -20 else
                'On track.'
            ),
        }

        # Budget position
        band = None
        if role:
            min_row = con.execute("SELECT setting_value FROM act_v2_client_settings WHERE client_id=? AND setting_key=?", [client_id, f'budget_band_{role.lower()}_min_pct']).fetchone()
            max_row = con.execute("SELECT setting_value FROM act_v2_client_settings WHERE client_id=? AND setting_key=?", [client_id, f'budget_band_{role.lower()}_max_pct']).fetchone()
            if min_row and max_row:
                band_min = int(min_row[0])
                band_max = int(max_row[0])
                band_min_abs = round(monthly_budget * band_min / 100, 0)
                band_max_abs = round(monthly_budget * band_max / 100, 0)
                current_pct = round(mtd_cost / (monthly_budget * days_elapsed / days_in_month) * 100, 1) if monthly_budget else 0
                if current_pct < band_min:
                    band_status = 'under_band'
                elif current_pct > band_max:
                    band_status = 'over_band'
                else:
                    band_status = 'in_band'
                band = {
                    'role': role, 'role_label': ROLE_LABEL.get(role, role),
                    'band_min_pct': band_min, 'band_max_pct': band_max,
                    'monthly_budget_total': monthly_budget,
                    'band_min_abs': band_min_abs, 'band_max_abs': band_max_abs,
                    'current_pct': current_pct,
                    'current_mtd': round(mtd_cost, 0),
                    'status': band_status,
                }

        # Pending shift recommendation for this campaign (as primary entity OR as
        # a counterparty in a budget-shift current_value/proposed_value pair).
        pending_shift = None
        prow = con.execute(
            """SELECT summary FROM act_v2_recommendations
               WHERE client_id=? AND status='pending' AND entity_id=?""",
            [client_id, campaign_id]
        ).fetchone()
        if prow:
            pending_shift = prow[0]

        # 8-week trend — aggregate by ISO week
        from collections import defaultdict
        weekly = defaultdict(lambda: {'cost': 0, 'conv': 0})
        for s in snaps:
            d = _dt.strptime(s['date'], '%Y-%m-%d').date()
            week_start = d - _td(days=d.weekday())
            if (latest - week_start).days > 56:
                continue
            weekly[week_start]['cost'] += s['m'].get('cost', 0)
            weekly[week_start]['conv'] += s['m'].get('conversions', 0)
        weeks_sorted = sorted(weekly.keys())
        trend = {
            'labels': [w.strftime('%d %b') for w in weeks_sorted],
            'cost': [round(weekly[w]['cost'], 2) for w in weeks_sorted],
            'conversions': [round(weekly[w]['conv'], 1) for w in weeks_sorted],
            'cpa': [round(weekly[w]['cost'] / weekly[w]['conv'], 2) if weekly[w]['conv'] > 0 else 0 for w in weeks_sorted],
        }

        # Awaiting approval / executed / monitoring / alerts — filter to this campaign (entity_id)
        def fetch_recs(query, extra=[]):
            return con.execute(query, [client_id, campaign_id] + extra).fetchall()

        # All pending recs for this client — filter in Python to include
        # counterparty shifts (campaign name appears in current_value_json keys).
        all_pending = con.execute("""
            SELECT recommendation_id, entity_id, entity_name, action_category, risk_level,
                   summary, recommendation_text, estimated_impact,
                   current_value_json, proposed_value_json, decision_tree_json
            FROM act_v2_recommendations
            WHERE client_id=? AND status='pending'
            ORDER BY identified_at DESC
        """, [client_id]).fetchall()
        awaiting = []
        budget_proposed = None
        for r in all_pending:
            rid, ent_id, ent_name, cat, risk, summary, rec_txt, impact, cv_raw, pv_raw, dt_raw = r
            cv = _parse_metrics(cv_raw) if cv_raw else {}
            pv = _parse_metrics(pv_raw) if pv_raw else {}
            is_primary = (ent_id == campaign_id)
            involved_as_name = campaign_name in cv or campaign_name in pv
            if not is_primary and not involved_as_name:
                continue
            # Build perspective from the campaign's own view (works for both
            # primary entity and counterparty when a budget shift is involved).
            perspective = None
            this_cv_d = cv.get(campaign_name) if isinstance(cv.get(campaign_name), dict) else None
            this_pv_d = pv.get(campaign_name) if isinstance(pv.get(campaign_name), dict) else None
            if this_cv_d and this_pv_d and 'daily_budget' in this_cv_d and 'daily_budget' in this_pv_d:
                delta = this_pv_d['daily_budget'] - this_cv_d['daily_budget']
                if delta != 0:
                    sign = '+' if delta > 0 else '\u2212'
                    direction = 'incoming from' if delta > 0 else 'outgoing to'
                    # Counterparty = the OTHER key in cv/pv
                    others = [k for k in set(list(cv.keys()) + list(pv.keys())) if k != campaign_name]
                    counterparty = others[0] if others else ent_name
                    perspective = f"{sign}\u00a3{abs(delta):.0f}/day {direction} {counterparty}"
            awaiting.append({
                'id': rid, 'action_category': cat, 'risk_level': risk,
                'summary': summary, 'recommendation_text': rec_txt, 'estimated_impact': impact,
                'perspective': perspective,
                'entity_name': ent_name, 'level': 'account',
                'decision_tree': _parse_metrics(dt_raw) if dt_raw else {},
                'current_value': cv, 'proposed_value': pv,
            })
            # If this campaign is referenced in the shift, compute projected Budget Position
            this_cv = cv.get(campaign_name) if isinstance(cv.get(campaign_name), dict) else None
            this_pv = pv.get(campaign_name) if isinstance(pv.get(campaign_name), dict) else None
            if budget_proposed is None and band and this_pv and 'daily_budget' in this_pv:
                prop_daily = this_pv['daily_budget']
                curr_daily = this_cv.get('daily_budget') if this_cv else daily_budget
                # Projected MTD = current MTD + (proposed - current) * days_elapsed
                delta_daily = prop_daily - curr_daily
                proj_mtd = mtd_cost + delta_daily * days_elapsed
                mtd_baseline = monthly_budget * days_elapsed / days_in_month if monthly_budget else 0
                proj_pct = round(proj_mtd / mtd_baseline * 100, 1) if mtd_baseline > 0 else 0
                if proj_pct < band['band_min_pct']:
                    proj_status = 'under_band'
                elif proj_pct > band['band_max_pct']:
                    proj_status = 'over_band'
                else:
                    proj_status = 'in_band'
                budget_proposed = {'mtd': round(proj_mtd, 0), 'pct': proj_pct, 'status': proj_status}

        # Prefer the perspective-framed line for the Budget Position "Pending:"
        # text whenever any awaiting rec has a perspective for this campaign
        # (covers both primary entity and counterparty).
        if awaiting:
            first = awaiting[0]
            pending_shift = first.get('perspective') or pending_shift or first.get('summary')

        executed_rows = fetch_recs("""
            SELECT action_id, action_type, reason, executed_at
            FROM act_v2_executed_actions
            WHERE client_id=? AND entity_id=? AND execution_status='success'
            AND executed_at >= CURRENT_TIMESTAMP - INTERVAL 24 HOUR
            ORDER BY executed_at DESC
        """)
        executed = [{'id': r[0], 'action_type': r[1], 'reason': r[2], 'executed_at': str(r[3]) if r[3] else ''} for r in executed_rows]

        monitoring_rows = fetch_recs("""
            SELECT monitoring_id, monitoring_type, started_at, ends_at, health_status
            FROM act_v2_monitoring WHERE client_id=? AND entity_id=? AND resolved_at IS NULL
        """)
        monitoring = [{'id': r[0], 'type': r[1], 'started_at': str(r[2]) if r[2] else '',
                       'ends_at': str(r[3]) if r[3] else '', 'health': r[4]} for r in monitoring_rows]

        alerts_rows = fetch_recs("""
            SELECT alert_id, title, description, severity, raised_at, resolution
            FROM act_v2_alerts WHERE client_id=? AND entity_id=?
            AND raised_at >= CURRENT_TIMESTAMP - INTERVAL 7 DAY
            ORDER BY raised_at DESC
        """)
        alerts = [{'id': r[0], 'title': r[1], 'description': r[2], 'severity': r[3],
                   'raised_at': str(r[4]) if r[4] else '', 'resolution': r[5]} for r in alerts_rows]

        # Universal Levers — read the caps from client settings
        def s(key, default=None):
            row = con.execute("SELECT setting_value FROM act_v2_client_settings WHERE client_id=? AND setting_key=?", [client_id, key]).fetchone()
            return row[0] if row and row[0] else default

        # Last 30 days of segment data for this campaign, aggregated per segment_value
        seg_cutoff = str(latest - _td(days=30))
        seg_rows = con.execute("""
            SELECT segment_type, segment_value,
                   SUM(cost) as cost, SUM(conversions) as conv,
                   SUM(clicks) as clicks, SUM(impressions) as impr
            FROM act_v2_campaign_segments
            WHERE client_id=? AND campaign_id=? AND snapshot_date >= CAST(? AS DATE)
            GROUP BY segment_type, segment_value
            ORDER BY segment_type, cost DESC
        """, [client_id, campaign_id, seg_cutoff]).fetchall()
        dev_rows, geo_rows, sched_rows = [], [], []
        for st, sv, cost, conv, clicks, impr in seg_rows:
            cpa = float(cost) / float(conv) if conv and conv > 0 else None
            ctr = round(float(clicks) / float(impr) * 100, 2) if impr and impr > 0 else 0
            if st == 'device':
                dev_rows.append({'device': sv.title(), 'cost': round(float(cost), 2),
                                 'cpa': round(cpa, 2) if cpa else None, 'conv': int(conv or 0), 'ctr': ctr})
            elif st == 'geo':
                geo_rows.append({'location': sv, 'cost': round(float(cost), 2),
                                 'cpa': round(cpa, 2) if cpa else None, 'conv': int(conv or 0)})
            elif st == 'ad_schedule':
                sched_rows.append({'slot': sv.replace('_h', ' h'), 'cost': round(float(cost), 2),
                                   'cpa': round(cpa, 2) if cpa else None, 'conv': int(conv or 0)})
        # Cap geo/schedule lists (they can be huge)
        geo_rows = geo_rows[:10]
        sched_rows = sched_rows[:10]

        # Negative keyword lists (client-level)
        neg_rows = con.execute(
            "SELECT COUNT(*), COALESCE(SUM(keyword_count), 0) FROM act_v2_negative_keyword_lists WHERE client_id=?",
            [client_id]
        ).fetchone()
        negatives = {'lists': neg_rows[0] or 0, 'total': int(neg_rows[1] or 0)}

        # Match-type distribution — approximate via search_terms for this campaign (last 30d)
        mt_rows = con.execute("""
            SELECT match_type, COUNT(*)
            FROM act_v2_search_terms
            WHERE client_id=? AND campaign_id=? AND snapshot_date >= CAST(? AS DATE)
            AND match_type IS NOT NULL
            GROUP BY match_type
        """, [client_id, campaign_id, seg_cutoff]).fetchall()
        match_dist = {mt: cnt for mt, cnt in mt_rows}

        levers = {
            'device': {'rows': dev_rows},
            'geo': {'rows': geo_rows},
            'schedule': {'rows': sched_rows},
            'device_caps': {'min': s('device_mod_min_pct'), 'max': s('device_mod_max_pct'), 'cooldown': s('device_bid_cooldown_days')},
            'geo_caps': {'min': s('geo_mod_min_pct'), 'max': s('geo_mod_max_pct'), 'cooldown': s('geo_bid_cooldown_days')},
            'schedule_caps': {'min': s('schedule_mod_min_pct'), 'max': s('schedule_mod_max_pct'), 'cooldown': s('schedule_bid_cooldown_days')},
            'negatives': negatives,
            'match_dist': match_dist,
        }

        # Bid Strategy formatted
        strat_target = bid_strategy.replace('_', ' ').title() if bid_strategy else 'Unknown'
        if target_cpa and 'TARGET_CPA' in bid_strategy:
            strat_target = f'tCPA £{target_cpa:.0f}'
        elif target_roas and 'TARGET_ROAS' in bid_strategy:
            strat_target = f'tROAS {target_roas:.1f}x'

        return jsonify({
            'success': True,
            'campaign': {
                'id': campaign_id, 'name': campaign_name, 'status': status,
                'bid_strategy': strat_target, 'role': role,
                'daily_budget': daily_budget,
            },
            'health': health,
            'score': score,
            'budget_position': band,
            'budget_proposed': budget_proposed,
            'pending_shift': pending_shift,
            'trend': trend,
            'awaiting': awaiting,
            'executed': executed,
            'monitoring': monitoring,
            'alerts': alerts,
            'levers': levers,
        })
    finally:
        con.close()
