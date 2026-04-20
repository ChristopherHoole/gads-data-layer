"""
ACT v2 Client Configuration Routes

Blueprint: v2_config_bp, URL prefix: /v2
Pages: /v2/config
API: /v2/config/save, /v2/config/reset
"""

import os
from datetime import datetime

import duckdb
from flask import Blueprint, render_template, request, jsonify

v2_config_bp = Blueprint('v2_config', __name__, url_prefix='/v2')

_WAREHOUSE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "warehouse.duckdb")
)


def _get_db():
    return duckdb.connect(_WAREHOUSE_PATH)


@v2_config_bp.route('/config')
def client_config():
    """Render the Client Configuration page."""
    client_id = request.args.get('client', 'oe001')
    con = _get_db()

    try:
        # Get client
        client_row = con.execute(
            """SELECT client_id, client_name, google_ads_customer_id, persona,
                      monthly_budget, target_cpa, target_roas, active, created_at, updated_at,
                      services_all, services_advertised, service_locations, client_brand_terms
               FROM act_v2_clients WHERE client_id = ?""",
            [client_id]
        ).fetchone()

        if not client_row:
            return f"Client '{client_id}' not found", 404

        client = {
            'id': client_row[0],
            'name': client_row[1],
            'customer_id': client_row[2],
            'persona': client_row[3],
            'monthly_budget': float(client_row[4]) if client_row[4] else 0,
            'target_cpa': float(client_row[5]) if client_row[5] else None,
            'target_roas': float(client_row[6]) if client_row[6] else None,
            'active': client_row[7],
            # N1a — client profile fields (lowercase, comma-separated)
            'services_all': client_row[10] or '',
            'services_advertised': client_row[11] or '',
            'service_locations': client_row[12] or '',
            'client_brand_terms': client_row[13] or '',
        }

        # Get all clients for switcher
        clients = con.execute(
            "SELECT client_id, client_name FROM act_v2_clients ORDER BY client_name"
        ).fetchall()
        clients_list = [{'id': r[0], 'name': r[1]} for r in clients]

        # Get level states
        level_rows = con.execute(
            "SELECT level, state FROM act_v2_client_level_state WHERE client_id = ?",
            [client_id]
        ).fetchall()
        level_states = {r[0]: r[1] for r in level_rows}

        # Get settings
        setting_rows = con.execute(
            "SELECT setting_key, setting_value, setting_type, level FROM act_v2_client_settings WHERE client_id = ?",
            [client_id]
        ).fetchall()
        settings = {}
        for r in setting_rows:
            settings[r[0]] = {'value': r[1], 'type': r[2], 'level': r[3]}

        # Get campaign roles (existing assignments)
        role_rows = con.execute(
            "SELECT google_ads_campaign_id, campaign_name, role FROM act_v2_campaign_roles WHERE client_id = ?",
            [client_id]
        ).fetchall()
        campaign_roles = [{'campaign_id': r[0], 'campaign_name': r[1], 'role': r[2]} for r in role_rows]
        roles_by_id = {r['campaign_id']: r['role'] for r in campaign_roles}

        # Get ALL campaigns from latest snapshot (for the role assignment form)
        campaign_rows = con.execute(
            """SELECT DISTINCT entity_id, entity_name
               FROM act_v2_snapshots
               WHERE client_id = ? AND level = 'campaign'
                 AND snapshot_date = (
                   SELECT MAX(snapshot_date) FROM act_v2_snapshots
                   WHERE client_id = ? AND level = 'campaign'
                 )
               ORDER BY entity_name""",
            [client_id, client_id]
        ).fetchall()
        all_campaigns = [
            {'campaign_id': r[0], 'campaign_name': r[1], 'role': roles_by_id.get(r[0], '')}
            for r in campaign_rows
        ]

        # Get negative keyword lists
        nkl_rows = con.execute(
            "SELECT list_id, list_name, word_count, match_type, keyword_count FROM act_v2_negative_keyword_lists WHERE client_id = ? ORDER BY word_count, match_type",
            [client_id]
        ).fetchall()
        neg_keyword_lists = [{'list_id': r[0], 'list_name': r[1], 'word_count': r[2], 'match_type': r[3], 'keyword_count': r[4]} for r in nkl_rows]

        # Last saved timestamp
        last_saved_row = con.execute(
            "SELECT MAX(updated_at) FROM act_v2_client_settings WHERE client_id = ?",
            [client_id]
        ).fetchone()
        last_saved = None
        if last_saved_row and last_saved_row[0]:
            ts = last_saved_row[0]
            if isinstance(ts, datetime):
                last_saved = ts.strftime('%#d %b %Y, %I:%M %p')
            else:
                last_saved = str(ts)

        # Check if API connected (any snapshots exist)
        snap_count = con.execute(
            "SELECT COUNT(*) FROM act_v2_snapshots WHERE client_id = ?",
            [client_id]
        ).fetchone()[0]
        api_connected = snap_count > 0

        # Get active campaign count from snapshots for onboarding
        campaign_count = con.execute(
            """SELECT COUNT(DISTINCT entity_id) FROM act_v2_snapshots
               WHERE client_id = ? AND level = 'campaign'""",
            [client_id]
        ).fetchone()[0]

    finally:
        con.close()

    return render_template('v2/client_config.html',
                           client=client,
                           clients=clients_list,
                           level_states=level_states,
                           settings=settings,
                           campaign_roles=campaign_roles,
                           all_campaigns=all_campaigns,
                           neg_keyword_lists=neg_keyword_lists,
                           last_saved=last_saved,
                           api_connected=api_connected,
                           campaign_count=campaign_count,
                           active_page='config')


@v2_config_bp.route('/config/save', methods=['POST'])
def save_settings():
    """Save all settings for the current client."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    client_id = data.get('client_id')
    if not client_id:
        return jsonify({'success': False, 'error': 'client_id required'}), 400

    con = _get_db()
    try:
        # Update client identity fields
        client_data = data.get('client', {})
        if client_data:
            persona = client_data.get('persona', 'lead_gen_cpa')
            monthly_budget = client_data.get('monthly_budget', 0)
            target_cpa = client_data.get('target_cpa')
            target_roas = client_data.get('target_roas')

            # N1a — 4 profile fields; lowercase + strip on save, empty => NULL
            def _norm(v):
                if v is None:
                    return None
                s = str(v).strip().lower()
                return s if s else None

            services_all = _norm(client_data.get('services_all'))
            services_advertised = _norm(client_data.get('services_advertised'))
            service_locations = _norm(client_data.get('service_locations'))
            client_brand_terms = _norm(client_data.get('client_brand_terms'))

            con.execute("""
                UPDATE act_v2_clients SET
                    persona = ?, monthly_budget = ?, target_cpa = ?, target_roas = ?,
                    services_all = ?, services_advertised = ?,
                    service_locations = ?, client_brand_terms = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE client_id = ?
            """, [persona, monthly_budget, target_cpa, target_roas,
                  services_all, services_advertised, service_locations, client_brand_terms,
                  client_id])

        # Update level states
        level_states = data.get('level_states', {})
        for level, state in level_states.items():
            con.execute("""
                UPDATE act_v2_client_level_state SET
                    state = ?, updated_at = CURRENT_TIMESTAMP, updated_by = 'user'
                WHERE client_id = ? AND level = ?
            """, [state, client_id, level])

        # Update settings
        settings = data.get('settings', {})
        for key, value in settings.items():
            # Get existing setting type and level
            existing = con.execute(
                "SELECT setting_type, level FROM act_v2_client_settings WHERE client_id = ? AND setting_key = ?",
                [client_id, key]
            ).fetchone()
            if existing:
                con.execute("""
                    UPDATE act_v2_client_settings SET
                        setting_value = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE client_id = ? AND setting_key = ?
                """, [value if value != '' else None, client_id, key])

        now = datetime.utcnow().strftime('%#d %b %Y, %I:%M %p')
        return jsonify({'success': True, 'saved_at': now})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        con.close()


@v2_config_bp.route('/config/roles/save', methods=['POST'])
def save_campaign_role():
    """Upsert a single campaign role assignment."""
    data = request.get_json() or {}
    client_id = data.get('client_id')
    campaign_id = data.get('campaign_id')
    campaign_name = data.get('campaign_name')
    role = (data.get('role') or '').strip()

    if not (client_id and campaign_id and campaign_name):
        return jsonify({'success': False, 'error': 'client_id, campaign_id, campaign_name required'}), 400

    valid_roles = {'BD', 'CP', 'RT', 'PR', 'TS'}
    if role and role not in valid_roles:
        return jsonify({'success': False, 'error': f'role must be one of {sorted(valid_roles)} or empty'}), 400

    con = _get_db()
    try:
        # Always delete first (DuckDB-safe upsert pattern)
        con.execute(
            "DELETE FROM act_v2_campaign_roles WHERE client_id = ? AND google_ads_campaign_id = ?",
            [client_id, campaign_id]
        )
        if role:
            con.execute(
                """INSERT INTO act_v2_campaign_roles
                   (client_id, google_ads_campaign_id, campaign_name, role, role_assigned_by, updated_at)
                   VALUES (?, ?, ?, ?, 'user', CURRENT_TIMESTAMP)""",
                [client_id, campaign_id, campaign_name, role]
            )
        return jsonify({'success': True, 'role': role or None})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        con.close()


@v2_config_bp.route('/config/reset', methods=['POST'])
def reset_settings():
    """Reset settings to defaults. Does NOT reset level states."""
    from act_dashboard.db.defaults import DEFAULT_SETTINGS

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    client_id = data.get('client_id')
    if not client_id:
        return jsonify({'success': False, 'error': 'client_id required'}), 400

    con = _get_db()
    try:
        # Delete all settings for this client
        con.execute("DELETE FROM act_v2_client_settings WHERE client_id = ?", [client_id])

        # Re-insert defaults
        for key, value, stype, level in DEFAULT_SETTINGS:
            con.execute("""
                INSERT INTO act_v2_client_settings
                (client_id, setting_key, setting_value, setting_type, level)
                VALUES (?, ?, ?, ?, ?)
            """, [client_id, key, value, stype, level])

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        con.close()
