"""
ACT v2 Account Level Page Route

Blueprint: v2_account_bp, URL prefix: /v2
Page: /v2/account — Account Level dashboard
"""

import json
import os
from datetime import datetime, timedelta

import duckdb
from flask import Blueprint, render_template, request

v2_account_bp = Blueprint('v2_account', __name__, url_prefix='/v2')

_WAREHOUSE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "warehouse.duckdb")
)


def _get_db():
    return duckdb.connect(_WAREHOUSE_PATH)


def _parse_metrics(metrics_json):
    """Parse metrics_json from DuckDB (may be str or dict)."""
    if isinstance(metrics_json, str):
        return json.loads(metrics_json)
    return metrics_json if metrics_json else {}


def _safe_div(num, den):
    if not den:
        return 0.0
    return num / den


@v2_account_bp.route('/account')
def account_level():
    """Render the Account Level page."""
    client_id = request.args.get('client', 'oe001')
    days = int(request.args.get('days', '30'))

    con = _get_db()
    try:
        # 1. Client info
        client_row = con.execute(
            """SELECT client_id, client_name, google_ads_customer_id, persona,
                      monthly_budget, target_cpa, target_roas, active
               FROM act_v2_clients WHERE client_id = ?""",
            [client_id]
        ).fetchone()
        if not client_row:
            return f"Client '{client_id}' not found", 404

        client = {
            'id': client_row[0], 'name': client_row[1], 'customer_id': client_row[2],
            'persona': client_row[3],
            'monthly_budget': float(client_row[4]) if client_row[4] else 0,
            'target_cpa': float(client_row[5]) if client_row[5] else None,
            'target_roas': float(client_row[6]) if client_row[6] else None,
        }

        # Client list for switcher
        clients = [{'id': r[0], 'name': r[1]} for r in
                   con.execute("SELECT client_id, client_name FROM act_v2_clients ORDER BY client_name").fetchall()]

        # Settings
        deviation_threshold = 10
        setting_row = con.execute(
            "SELECT setting_value FROM act_v2_client_settings WHERE client_id = ? AND setting_key = 'deviation_threshold_pct'",
            [client_id]
        ).fetchone()
        if setting_row and setting_row[0]:
            deviation_threshold = int(setting_row[0])

        # 2. Determine date range
        # Find the latest snapshot date
        latest_row = con.execute(
            "SELECT MAX(snapshot_date) FROM act_v2_snapshots WHERE client_id = ? AND level = 'campaign'",
            [client_id]
        ).fetchone()
        if latest_row and latest_row[0]:
            end_date = latest_row[0]
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = datetime.now().date() - timedelta(days=1)

        start_date = end_date - timedelta(days=days)
        end_str = str(end_date)
        start_str = str(start_date)

        # MTD dates
        mtd_start = end_date.replace(day=1)

        # 3. Campaign snapshots for date range
        campaign_snaps = con.execute(
            """SELECT snapshot_date, entity_id, entity_name, metrics_json
               FROM act_v2_snapshots
               WHERE client_id = ? AND level = 'campaign'
               AND snapshot_date BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
               ORDER BY snapshot_date""",
            [client_id, start_str, end_str]
        ).fetchall()

        # Parse all snapshots
        all_snaps = []
        for row in campaign_snaps:
            m = _parse_metrics(row[3])
            all_snaps.append({
                'date': str(row[0]),
                'entity_id': str(row[1]),
                'entity_name': row[2],
                'metrics': m,
            })

        # 4. Build campaigns table data (aggregate over date range)
        campaign_ids = set(s['entity_id'] for s in all_snaps)
        campaigns_table = []
        for cid in campaign_ids:
            camp_snaps = [s for s in all_snaps if s['entity_id'] == cid]
            if not camp_snaps:
                continue
            name = camp_snaps[0]['entity_name']
            status = camp_snaps[-1]['metrics'].get('campaign_status', 'UNKNOWN')
            budget = camp_snaps[-1]['metrics'].get('budget_amount', 0)
            bid_strategy = camp_snaps[-1]['metrics'].get('bid_strategy_type', '')

            total_cost = sum(s['metrics'].get('cost', 0) for s in camp_snaps)
            total_impr = sum(s['metrics'].get('impressions', 0) for s in camp_snaps)
            total_clicks = sum(s['metrics'].get('clicks', 0) for s in camp_snaps)
            total_conv = sum(s['metrics'].get('conversions', 0) for s in camp_snaps)
            total_conv_value = sum(s['metrics'].get('conversion_value', 0) for s in camp_snaps)

            avg_cpc = _safe_div(total_cost, total_clicks)
            ctr = _safe_div(total_clicks, total_impr) * 100
            cost_per_conv = _safe_div(total_cost, total_conv) if total_conv > 0 else None
            conv_rate = _safe_div(total_conv, total_clicks) * 100

            campaigns_table.append({
                'entity_id': cid, 'name': name, 'status': status.lower(),
                'budget': budget, 'bid_strategy': bid_strategy,
                'cost': round(total_cost, 2), 'impressions': total_impr,
                'clicks': total_clicks, 'avg_cpc': round(avg_cpc, 2),
                'ctr': round(ctr, 2), 'conversions': round(total_conv, 1),
                'cost_per_conv': round(cost_per_conv, 2) if cost_per_conv else None,
                'conv_rate': round(conv_rate, 2), 'conversion_value': round(total_conv_value, 2),
            })

        # Get campaign roles
        role_rows = con.execute(
            "SELECT google_ads_campaign_id, role FROM act_v2_campaign_roles WHERE client_id = ?",
            [client_id]
        ).fetchall()
        campaign_roles = {str(r[0]): r[1] for r in role_rows}

        # Add roles to campaigns
        total_budget = sum(c['budget'] for c in campaigns_table)
        for c in campaigns_table:
            c['role'] = campaign_roles.get(c['entity_id'], '')
            c['share'] = round(_safe_div(c['budget'], total_budget) * 100, 1) if total_budget > 0 else 0

        # Sort: enabled first, then by cost desc
        campaigns_table.sort(key=lambda c: (0 if c['status'] == 'enabled' else 1, -c['cost']))

        # 4b. Score campaigns using engine logic
        from act_dashboard.engine.account_level import AccountLevelEngine
        engine = AccountLevelEngine(client_id)
        try:
            engine_campaigns = [
                {'entity_id': c['entity_id'], 'name': c['name'], 'metrics': c}
                for c in campaigns_table if c['status'] == 'enabled'
            ]
            if engine_campaigns:
                scored = engine._score_campaigns(engine_campaigns, end_str)
                score_map = {s['entity_id']: s for s in scored}
                for c in campaigns_table:
                    sc = score_map.get(c['entity_id'])
                    if sc:
                        c['score'] = round(sc['score'])
                        c['score_7d'] = round(sc.get('score_7d', 0))
                        c['score_14d'] = round(sc.get('score_14d', 0))
                        c['score_30d'] = round(sc.get('score_30d', 0))
                        c['cpa_7d'] = round(sc.get('cpa_7d', 0), 2) if sc.get('cpa_7d') != float('inf') else None
                        c['cpa_14d'] = round(sc.get('cpa_14d', 0), 2) if sc.get('cpa_14d') != float('inf') else None
                        c['cpa_30d'] = round(sc.get('cpa_30d', 0), 2) if sc.get('cpa_30d') != float('inf') else None
        finally:
            engine.close()

        # 5. Summary totals
        enabled_camps = [c for c in campaigns_table if c['status'] == 'enabled']
        summary = {
            'cost': sum(c['cost'] for c in campaigns_table),
            'impressions': sum(c['impressions'] for c in campaigns_table),
            'clicks': sum(c['clicks'] for c in campaigns_table),
            'conversions': sum(c['conversions'] for c in campaigns_table),
            'avg_cpc': round(_safe_div(sum(c['cost'] for c in campaigns_table),
                                       sum(c['clicks'] for c in campaigns_table)), 2),
            'ctr': round(_safe_div(sum(c['clicks'] for c in campaigns_table),
                                   sum(c['impressions'] for c in campaigns_table)) * 100, 2),
            'cost_per_conv': None,
            'conv_rate': round(_safe_div(sum(c['conversions'] for c in campaigns_table),
                                        sum(c['clicks'] for c in campaigns_table)) * 100, 2),
        }
        total_conv = summary['conversions']
        if total_conv > 0:
            summary['cost_per_conv'] = round(summary['cost'] / total_conv, 2)

        # 5b. Previous period comparison for change indicators
        prev_start = start_date - timedelta(days=days)
        prev_end = start_date - timedelta(days=1)
        prev_snaps = con.execute(
            """SELECT entity_id, metrics_json FROM act_v2_snapshots
               WHERE client_id = ? AND level = 'campaign'
               AND snapshot_date BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)""",
            [client_id, str(prev_start), str(prev_end)]
        ).fetchall()

        if prev_snaps:
            prev_cost = sum(_parse_metrics(r[1]).get('cost', 0) for r in prev_snaps)
            prev_impr = sum(_parse_metrics(r[1]).get('impressions', 0) for r in prev_snaps)
            prev_clicks = sum(_parse_metrics(r[1]).get('clicks', 0) for r in prev_snaps)
            prev_conv = sum(_parse_metrics(r[1]).get('conversions', 0) for r in prev_snaps)

            def _pct_change(curr, prev):
                if not prev:
                    return None
                return round((curr - prev) / prev * 100)

            summary['cost_change'] = _pct_change(summary['cost'], prev_cost)
            summary['impressions_change'] = _pct_change(summary['impressions'], prev_impr)
            summary['clicks_change'] = _pct_change(summary['clicks'], prev_clicks)
            summary['ctr_change'] = _pct_change(summary['ctr'],
                                                round(_safe_div(prev_clicks, prev_impr) * 100, 2)) if prev_impr else None
            summary['avg_cpc_change'] = _pct_change(summary['avg_cpc'],
                                                    round(_safe_div(prev_cost, prev_clicks), 2)) if prev_clicks else None
            summary['conversions_change'] = _pct_change(summary['conversions'], prev_conv)
            prev_cpa = _safe_div(prev_cost, prev_conv) if prev_conv > 0 else None
            summary['cpa_change'] = _pct_change(summary['cost_per_conv'], prev_cpa) if summary['cost_per_conv'] and prev_cpa else None
            prev_cvr = _safe_div(prev_conv, prev_clicks) * 100 if prev_clicks else None
            summary['conv_rate_change'] = _pct_change(summary['conv_rate'], prev_cvr) if prev_cvr else None
        else:
            for k in ['cost_change', 'impressions_change', 'clicks_change', 'ctr_change',
                       'avg_cpc_change', 'conversions_change', 'cpa_change', 'conv_rate_change']:
                summary[k] = None

        # 6. Health cards — MTD data (always full month, independent of date range)
        mtd_snaps_rows = con.execute(
            """SELECT metrics_json FROM act_v2_snapshots
               WHERE client_id = ? AND level = 'campaign'
               AND snapshot_date >= CAST(? AS DATE) AND snapshot_date <= CAST(? AS DATE)""",
            [client_id, str(mtd_start), end_str]
        ).fetchall()
        mtd_cost = sum(_parse_metrics(r[0]).get('cost', 0) for r in mtd_snaps_rows)
        mtd_conv = sum(_parse_metrics(r[0]).get('conversions', 0) for r in mtd_snaps_rows)

        # Current CPA from MTD aggregate (not single-day snapshot)
        current_cpa = None
        if mtd_conv > 0:
            current_cpa = mtd_cost / mtd_conv

        # CPA zone
        cpa_zone = None
        cpa_deviation_pct = None
        if current_cpa and current_cpa > 0 and client['target_cpa']:
            target = client['target_cpa']
            dev = deviation_threshold / 100
            cpa_deviation_pct = round(abs(current_cpa - target) / target * 100, 0)
            if current_cpa < target * (1 - dev):
                cpa_zone = 'outperforming'
            elif current_cpa > target * (1 + dev):
                cpa_zone = 'underperforming'
            else:
                cpa_zone = 'ontarget'

        # Projection: (conversions so far / days elapsed) * days in month
        from calendar import monthrange
        days_in_month = monthrange(end_date.year, end_date.month)[1]
        days_elapsed = (end_date - mtd_start).days + 1
        projected_conv = round(mtd_conv / days_elapsed * days_in_month) if days_elapsed > 0 and mtd_conv > 0 else None

        health = {
            'monthly_budget': client['monthly_budget'],
            'daily_budget': round(client['monthly_budget'] / 30, 2),
            'current_cpa': round(current_cpa, 2) if current_cpa else None,
            'cpa_zone': cpa_zone,
            'cpa_deviation_pct': cpa_deviation_pct,
            'mtd_cost': round(mtd_cost, 2),
            'mtd_budget_pct': round(_safe_div(mtd_cost, client['monthly_budget']) * 100, 1),
            'mtd_conversions': round(mtd_conv, 1),
            'projected_conv': projected_conv,
        }

        # 7. Chart data — daily account-level metrics
        account_snaps = con.execute(
            """SELECT snapshot_date, metrics_json FROM act_v2_snapshots
               WHERE client_id = ? AND level = 'account'
               AND snapshot_date BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
               ORDER BY snapshot_date""",
            [client_id, start_str, end_str]
        ).fetchall()

        chart_labels = []
        chart_metrics = {
            'cost': [], 'impressions': [], 'clicks': [], 'avgCpc': [],
            'ctr': [], 'conversions': [], 'cpa': [], 'convRate': [],
            'score': [], 'budgetUtil': [],
        }

        if days <= 30:
            # Daily points
            for row in account_snaps:
                d = row[0]
                if isinstance(d, str):
                    d = datetime.strptime(d, '%Y-%m-%d').date()
                chart_labels.append(d.strftime('%d %b'))
                m = _parse_metrics(row[1])
                chart_metrics['cost'].append(round(m.get('cost', 0), 2))
                chart_metrics['impressions'].append(m.get('impressions', 0))
                chart_metrics['clicks'].append(m.get('clicks', 0))
                chart_metrics['avgCpc'].append(round(m.get('avg_cpc', 0), 2))
                chart_metrics['ctr'].append(round(m.get('ctr', 0) * 100, 2))
                chart_metrics['conversions'].append(round(m.get('conversions', 0), 1))
                cpa_val = round(m.get('cost_per_conversion', 0), 2) if m.get('conversions', 0) > 0 else 0
                chart_metrics['cpa'].append(cpa_val)
                chart_metrics['convRate'].append(round(m.get('conversion_rate', 0) * 100, 2))
                chart_metrics['score'].append(0)
                chart_metrics['budgetUtil'].append(0)
        else:
            # 90d: weekly aggregates (13 weeks)
            weekly_data = {}
            for row in account_snaps:
                d = row[0]
                if isinstance(d, str):
                    d = datetime.strptime(d, '%Y-%m-%d').date()
                week_start = d - timedelta(days=d.weekday())
                if week_start not in weekly_data:
                    weekly_data[week_start] = []
                weekly_data[week_start].append(_parse_metrics(row[1]))

            for week_start in sorted(weekly_data.keys()):
                week_metrics = weekly_data[week_start]
                chart_labels.append(week_start.strftime('%d %b'))
                chart_metrics['cost'].append(round(sum(m.get('cost', 0) for m in week_metrics), 2))
                chart_metrics['impressions'].append(sum(m.get('impressions', 0) for m in week_metrics))
                chart_metrics['clicks'].append(sum(m.get('clicks', 0) for m in week_metrics))
                n = len(week_metrics)
                chart_metrics['avgCpc'].append(round(sum(m.get('avg_cpc', 0) for m in week_metrics) / n, 2))
                chart_metrics['ctr'].append(round(sum(m.get('ctr', 0) for m in week_metrics) / n * 100, 2))
                chart_metrics['conversions'].append(round(sum(m.get('conversions', 0) for m in week_metrics), 1))
                total_c = sum(m.get('cost', 0) for m in week_metrics)
                total_cv = sum(m.get('conversions', 0) for m in week_metrics)
                chart_metrics['cpa'].append(round(_safe_div(total_c, total_cv), 2) if total_cv > 0 else 0)
                chart_metrics['convRate'].append(round(sum(m.get('conversion_rate', 0) for m in week_metrics) / n * 100, 2))
                chart_metrics['score'].append(0)
                chart_metrics['budgetUtil'].append(0)

        chart_data = {'labels': chart_labels, 'metrics': chart_metrics}

        # 8. Review sections
        pending_recs = con.execute(
            """SELECT recommendation_id, entity_name, action_category, risk_level,
                      summary, recommendation_text, estimated_impact,
                      decision_tree_json, current_value_json, proposed_value_json,
                      mode, identified_at
               FROM act_v2_recommendations
               WHERE client_id = ? AND level = 'account' AND status = 'pending'
               ORDER BY identified_at DESC""",
            [client_id]
        ).fetchall()
        awaiting_approval = []
        for r in pending_recs:
            awaiting_approval.append({
                'id': r[0], 'entity_name': r[1], 'action_category': r[2],
                'risk_level': r[3], 'summary': r[4], 'recommendation_text': r[5],
                'estimated_impact': r[6],
                'decision_tree': json.loads(r[7]) if r[7] and isinstance(r[7], str) else r[7],
                'current_value': json.loads(r[8]) if r[8] and isinstance(r[8], str) else r[8],
                'proposed_value': json.loads(r[9]) if r[9] and isinstance(r[9], str) else r[9],
                'mode': r[10], 'identified_at': str(r[11]) if r[11] else '',
            })

        executed_actions = con.execute(
            """SELECT action_id, entity_name, action_type, before_value_json,
                      after_value_json, reason, executed_at
               FROM act_v2_executed_actions
               WHERE client_id = ? AND level = 'account' AND execution_status = 'success'
               ORDER BY executed_at DESC LIMIT 10""",
            [client_id]
        ).fetchall()
        actions_list = [{'id': r[0], 'entity_name': r[1], 'action_type': r[2],
                         'before': json.loads(r[3]) if r[3] and isinstance(r[3], str) else r[3],
                         'after': json.loads(r[4]) if r[4] and isinstance(r[4], str) else r[4],
                         'reason': r[5], 'executed_at': str(r[6]) if r[6] else ''}
                        for r in executed_actions]

        monitoring = con.execute(
            """SELECT monitoring_id, entity_id, monitoring_type, started_at,
                      ends_at, health_status, consecutive_days_stable
               FROM act_v2_monitoring
               WHERE client_id = ? AND level = 'account' AND resolved_at IS NULL
               ORDER BY started_at DESC""",
            [client_id]
        ).fetchall()
        monitoring_list = [{'id': r[0], 'entity_id': r[1], 'type': r[2],
                            'started_at': str(r[3]) if r[3] else '',
                            'ends_at': str(r[4]) if r[4] else '',
                            'health': r[5], 'stable_days': r[6]}
                           for r in monitoring]

        alerts = con.execute(
            """SELECT alert_id, alert_type, severity, title, description,
                      entity_id, raised_at, resolved_at, resolution
               FROM act_v2_alerts
               WHERE client_id = ? AND level = 'account'
               AND raised_at >= CAST(? AS DATE)
               ORDER BY raised_at DESC""",
            [client_id, str(end_date - timedelta(days=7))]
        ).fetchall()
        alerts_list = [{'id': r[0], 'type': r[1], 'severity': r[2], 'title': r[3],
                        'description': r[4], 'entity_id': r[5],
                        'raised_at': str(r[6]) if r[6] else '',
                        'resolved_at': str(r[7]) if r[7] else '',
                        'resolution': r[8]}
                       for r in alerts]

        # 9. Signal decomposition — CPC/CVR trends per campaign
        signals = []
        for c in [c for c in campaigns_table if c['status'] == 'enabled']:
            cid = c['entity_id']
            # Get 7d and 14d data
            snaps_7d = [s for s in all_snaps if s['entity_id'] == cid
                        and s['date'] > str(end_date - timedelta(days=7))]
            snaps_14d = [s for s in all_snaps if s['entity_id'] == cid
                         and s['date'] > str(end_date - timedelta(days=14))]

            cpc_7d = _safe_div(
                sum(s['metrics'].get('cost', 0) for s in snaps_7d),
                sum(s['metrics'].get('clicks', 0) for s in snaps_7d)
            )
            cvr_14d = _safe_div(
                sum(s['metrics'].get('conversions', 0) for s in snaps_14d),
                sum(s['metrics'].get('clicks', 0) for s in snaps_14d)
            ) * 100

            cost_total = sum(s['metrics'].get('cost', 0) for s in snaps_14d)
            conv_total = sum(s['metrics'].get('conversions', 0) for s in snaps_14d)
            cpa = _safe_div(cost_total, conv_total) if conv_total > 0 else None

            # Zone
            zone = None
            if cpa and client['target_cpa']:
                target = client['target_cpa']
                dev = deviation_threshold / 100
                if cpa < target * (1 - dev):
                    zone = 'outperforming'
                elif cpa > target * (1 + dev):
                    zone = 'underperforming'
                else:
                    zone = 'ontarget'

            signals.append({
                'name': c['name'], 'cpc_7d': round(cpc_7d, 2),
                'cvr_14d': round(cvr_14d, 2),
                'cpa': round(cpa, 2) if cpa else None,
                'zone': zone,
            })

        # 10. Guardrails from settings
        guardrails_keys = [
            ('max_overnight_budget_move_pct', 'Max Overnight Budget Move', '%'),
            ('budget_shift_cooldown_hours', 'Budget Shift Cooldown', ' hours'),
            ('deviation_threshold_pct', 'Deviation Threshold', '%'),
        ]
        guardrails = []
        for key, label, suffix in guardrails_keys:
            val_row = con.execute(
                "SELECT setting_value FROM act_v2_client_settings WHERE client_id = ? AND setting_key = ?",
                [client_id, key]
            ).fetchone()
            guardrails.append({
                'label': label,
                'value': (val_row[0] if val_row else '—') + suffix,
            })

        # ACT last ran
        last_ran_row = con.execute(
            """SELECT MAX(identified_at) FROM act_v2_recommendations WHERE client_id = ?""",
            [client_id]
        ).fetchone()
        last_ran = None
        if last_ran_row and last_ran_row[0]:
            lr = last_ran_row[0]
            if isinstance(lr, datetime):
                last_ran = lr.strftime('%d %b %Y, %H:%M')
            else:
                last_ran = str(lr)

    finally:
        con.close()

    return render_template('v2/account_level.html',
                           client=client, clients=clients,
                           campaigns=campaigns_table,
                           campaign_roles=campaign_roles,
                           summary=summary,
                           health=health,
                           chart_data=chart_data,
                           awaiting_approval=awaiting_approval,
                           executed_actions=actions_list,
                           monitoring=monitoring_list,
                           alerts=alerts_list,
                           signals=signals,
                           guardrails=guardrails,
                           last_ran=last_ran,
                           days=days,
                           active_page='account')
