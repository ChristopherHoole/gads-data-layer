"""
Dashboard Routes
All URL endpoints for the web interface.
"""

from flask import render_template, request, redirect, url_for, session, jsonify, flash
from act_dashboard.auth import login_required, check_credentials
import duckdb
import json
from pathlib import Path
from datetime import datetime, date, timedelta


def init_routes(app):
    """
    Initialize all routes for the Flask app.
    
    Args:
        app: Flask application instance
    """
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page."""
        if request.method == 'POST':
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            
            if check_credentials(username, password):
                session['logged_in'] = True
                session.permanent = True
                
                # Redirect to next page or dashboard
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            else:
                flash('Invalid credentials', 'error')
        
        return render_template('login.html')
    
    
    @app.route('/logout')
    def logout():
        """Logout and clear session."""
        session.clear()
        return redirect(url_for('login'))
    
    
    @app.route('/')
    @login_required
    def dashboard():
        """Dashboard home page with overview stats."""
        config = app.config['DASHBOARD_CONFIG']
        
        # Connect to database
        conn = duckdb.connect(config.db_path, read_only=True)
        
        # Get account summary (last 7 days)
        summary_query = """
        SELECT 
            COUNT(DISTINCT campaign_id) as campaign_count,
            SUM(cost_micros) / 1000000 as total_spend,
            SUM(conversions) as total_conversions,
            SUM(conversions_value) / NULLIF(SUM(cost_micros), 0) as avg_roas
        FROM analytics.campaign_daily
        WHERE customer_id = ?
          AND snapshot_date >= CURRENT_DATE - INTERVAL '7 days'
        """
        summary = conn.execute(summary_query, [config.customer_id]).fetchone()
        
        # Get pending recommendations count (today)
        today = date.today().isoformat()
        suggestions_path = config.get_suggestions_path(today)
        pending_count = 0
        if suggestions_path.exists():
            with open(suggestions_path, 'r') as f:
                suggestions = json.load(f)
                pending_count = len([r for r in suggestions['recommendations'] if not r.get('blocked', False)])
        
        # Get recent changes (last 7 days)
        changes_query = """
        SELECT 
            change_date,
            campaign_id,
            lever,
            old_value / 1000000 as old_value,
            new_value / 1000000 as new_value,
            change_pct,
            rule_id,
            rollback_status
        FROM analytics.change_log
        WHERE customer_id = ?
          AND change_date >= CURRENT_DATE - INTERVAL '7 days'
        ORDER BY change_date DESC, executed_at DESC
        LIMIT 5
        """
        recent_changes = conn.execute(changes_query, [config.customer_id]).fetchall()
        
        # Get performance trend (last 30 days)
        trend_query = """
        SELECT 
            snapshot_date,
            SUM(cost_micros) / 1000000 as spend,
            SUM(conversions) as conversions,
            SUM(conversions_value) / NULLIF(SUM(cost_micros), 0) as roas
        FROM analytics.campaign_daily
        WHERE customer_id = ?
          AND snapshot_date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY snapshot_date
        ORDER BY snapshot_date
        """
        trend_data = conn.execute(trend_query, [config.customer_id]).fetchall()
        
        conn.close()
        
        # Prepare data for template
        return render_template('dashboard.html',
            client_name=config.client_name,
            campaign_count=summary[0] or 0,
            total_spend=summary[1] or 0,
            total_conversions=summary[2] or 0,
            avg_roas=summary[3] or 0,
            pending_count=pending_count,
            recent_changes=recent_changes,
            trend_data=trend_data
        )
    
    
    @app.route('/recommendations')
    @app.route('/recommendations/<date_str>')
    @login_required
    def recommendations(date_str=None):
        """Recommendations page for viewing and approving suggestions."""
        config = app.config['DASHBOARD_CONFIG']
        
        # Use today's date if not specified
        if date_str is None:
            date_str = date.today().isoformat()
        
        # Load suggestions
        suggestions_path = config.get_suggestions_path(date_str)
        
        if not suggestions_path.exists():
            return render_template('recommendations.html',
                client_name=config.client_name,
                date=date_str,
                recommendations=None,
                error=f"No suggestions found for {date_str}"
            )
        
        with open(suggestions_path, 'r') as f:
            suggestions_data = json.load(f)
        
        # Load existing approvals if any
        approvals_path = config.get_approvals_path(date_str)
        approved_ids = set()
        rejected_ids = set()
        
        if approvals_path.exists():
            with open(approvals_path, 'r') as f:
                approvals = json.load(f)
                for decision in approvals.get('decisions', []):
                    key = f"{decision['rule_id']}_{decision['entity_id']}"
                    if decision['decision'] == 'approved':
                        approved_ids.add(key)
                    elif decision['decision'] == 'rejected':
                        rejected_ids.add(key)
        
        # Group recommendations by risk tier
        low_risk = []
        medium_risk = []
        high_risk = []
        
        for rec in suggestions_data['recommendations']:
            if rec.get('blocked', False):
                continue  # Skip blocked recommendations
            
            # Add approval status
            key = f"{rec['rule_id']}_{rec['entity_id']}"
            rec['approved'] = key in approved_ids
            rec['rejected'] = key in rejected_ids
            
            # Group by risk
            risk = rec.get('risk_tier', 'low')
            if risk == 'low':
                low_risk.append(rec)
            elif risk in ['med', 'medium']:
                medium_risk.append(rec)
            else:
                high_risk.append(rec)
        
        return render_template('recommendations.html',
            client_name=config.client_name,
            date=date_str,
            summary=suggestions_data.get('summary', {}),
            low_risk=low_risk,
            medium_risk=medium_risk,
            high_risk=high_risk
        )
    
    
    @app.route('/api/approve', methods=['POST'])
    @login_required
    def approve_recommendation():
        """API endpoint to approve a recommendation."""
        data = request.json
        date_str = data.get('date')
        rule_id = data.get('rule_id')
        entity_id = data.get('entity_id')
        campaign_name = data.get('campaign_name', 'N/A')
        action_type = data.get('action_type')
        
        config = app.config['DASHBOARD_CONFIG']
        approvals_path = config.get_approvals_path(date_str)
        
        # Load or create approvals file
        if approvals_path.exists():
            with open(approvals_path, 'r') as f:
                approvals = json.load(f)
        else:
            approvals = {
                'snapshot_date': date_str,
                'client_name': config.client_name,
                'reviewed_at': None,
                'total_reviewed': 0,
                'approved': 0,
                'rejected': 0,
                'skipped': 0,
                'decisions': []
            }
            approvals_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove any existing decision for this recommendation
        approvals['decisions'] = [
            d for d in approvals['decisions']
            if not (d['rule_id'] == rule_id and d['entity_id'] == entity_id)
        ]
        
        # Add new approval
        approvals['decisions'].append({
            'rule_id': rule_id,
            'entity_id': entity_id,
            'campaign_name': campaign_name,
            'action_type': action_type,
            'decision': 'approved',
            'reviewed_at': datetime.utcnow().isoformat() + 'Z'
        })
        
        # Update counts
        approvals['total_reviewed'] = len(approvals['decisions'])
        approvals['approved'] = len([d for d in approvals['decisions'] if d['decision'] == 'approved'])
        approvals['rejected'] = len([d for d in approvals['decisions'] if d['decision'] == 'rejected'])
        approvals['reviewed_at'] = datetime.utcnow().isoformat() + 'Z'
        
        # Save
        with open(approvals_path, 'w') as f:
            json.dump(approvals, f, indent=2)
        
        return jsonify({'success': True})
    
    
    @app.route('/api/reject', methods=['POST'])
    @login_required
    def reject_recommendation():
        """API endpoint to reject a recommendation."""
        data = request.json
        date_str = data.get('date')
        rule_id = data.get('rule_id')
        entity_id = data.get('entity_id')
        campaign_name = data.get('campaign_name', 'N/A')
        action_type = data.get('action_type')
        
        config = app.config['DASHBOARD_CONFIG']
        approvals_path = config.get_approvals_path(date_str)
        
        # Load or create approvals file
        if approvals_path.exists():
            with open(approvals_path, 'r') as f:
                approvals = json.load(f)
        else:
            approvals = {
                'snapshot_date': date_str,
                'client_name': config.client_name,
                'reviewed_at': None,
                'total_reviewed': 0,
                'approved': 0,
                'rejected': 0,
                'skipped': 0,
                'decisions': []
            }
            approvals_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove any existing decision for this recommendation
        approvals['decisions'] = [
            d for d in approvals['decisions']
            if not (d['rule_id'] == rule_id and d['entity_id'] == entity_id)
        ]
        
        # Add rejection
        approvals['decisions'].append({
            'rule_id': rule_id,
            'entity_id': entity_id,
            'campaign_name': campaign_name,
            'action_type': action_type,
            'decision': 'rejected',
            'reviewed_at': datetime.utcnow().isoformat() + 'Z'
        })
        
        # Update counts
        approvals['total_reviewed'] = len(approvals['decisions'])
        approvals['approved'] = len([d for d in approvals['decisions'] if d['decision'] == 'approved'])
        approvals['rejected'] = len([d for d in approvals['decisions'] if d['decision'] == 'rejected'])
        approvals['reviewed_at'] = datetime.utcnow().isoformat() + 'Z'
        
        # Save
        with open(approvals_path, 'w') as f:
            json.dump(approvals, f, indent=2)
        
        return jsonify({'success': True})
    
    
    @app.route('/changes')
    @login_required
    def changes():
        """Change history page showing all executed changes."""
        config = app.config['DASHBOARD_CONFIG']
        
        # Get filter parameters
        search = request.args.get('search', '')
        status_filter = request.args.get('status', 'all')
        lever_filter = request.args.get('lever', 'all')
        
        # Connect to database
        conn = duckdb.connect(config.db_path, read_only=True)
        
        # Build query with filters
        query = """
        SELECT 
            change_id,
            change_date,
            campaign_id,
            lever,
            old_value / 1000000 as old_value,
            new_value / 1000000 as new_value,
            change_pct,
            rule_id,
            risk_tier,
            rollback_status,
            executed_at
        FROM analytics.change_log
        WHERE customer_id = ?
        """
        params = [config.customer_id]
        
        if status_filter != 'all':
            if status_filter == 'active':
                query += " AND (rollback_status IS NULL OR rollback_status = 'monitoring')"
            else:
                query += " AND rollback_status = ?"
                params.append(status_filter)
        
        if lever_filter != 'all':
            query += " AND lever = ?"
            params.append(lever_filter)
        
        if search:
            query += " AND campaign_id LIKE ?"
            params.append(f"%{search}%")
        
        query += " ORDER BY change_date DESC, executed_at DESC LIMIT 100"
        
        changes_data = conn.execute(query, params).fetchall()
        conn.close()
        
        return render_template('changes.html',
            client_name=config.client_name,
            changes=changes_data,
            search=search,
            status_filter=status_filter,
            lever_filter=lever_filter
        )
    
    
    @app.route('/settings', methods=['GET', 'POST'])
    @login_required
    def settings():
        """Settings page for editing client configuration."""
        config = app.config['DASHBOARD_CONFIG']
        
        if request.method == 'POST':
            # Update configuration from form
            config.client_name = request.form.get('client_name', config.client_name)
            config.client_type = request.form.get('client_type', config.client_type)
            config.primary_kpi = request.form.get('primary_kpi', config.primary_kpi)
            config.automation_mode = request.form.get('automation_mode', config.automation_mode)
            config.risk_tolerance = request.form.get('risk_tolerance', config.risk_tolerance)
            
            # Update targets
            target_roas = request.form.get('target_roas', '')
            config.target_roas = float(target_roas) if target_roas else None
            
            target_cpa = request.form.get('target_cpa', '')
            config.target_cpa = float(target_cpa) if target_cpa else None
            
            # Update spend caps
            daily_cap = request.form.get('daily_cap', '')
            config.daily_cap = float(daily_cap) if daily_cap else 0
            
            monthly_cap = request.form.get('monthly_cap', '')
            config.monthly_cap = float(monthly_cap) if monthly_cap else 0
            
            # Update protected entities
            config.brand_protected = request.form.get('brand_protected') == 'on'
            
            # Save to YAML
            config.save()
            
            flash('Settings saved successfully', 'success')
            return redirect(url_for('settings'))
        
        return render_template('settings.html',
            client_name=config.client_name,
            config=config
        )
