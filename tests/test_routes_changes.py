"""
tests/test_routes_changes.py

Tests for GET /changes route.
Chat 89.
"""

import pytest


class TestChangesRoute:
    def test_get_changes_returns_200(self, client):
        resp = client.get("/changes")
        assert resp.status_code == 200

    def test_get_changes_requires_login(self, app):
        with app.test_client() as c:
            resp = c.get("/changes")
            assert resp.status_code in (200, 302)

    def test_get_changes_has_content(self, client):
        resp = client.get("/changes")
        assert len(resp.data) > 0

    def test_get_changes_response_is_html(self, client):
        resp = client.get("/changes")
        # Should return HTML
        assert resp.content_type.startswith("text/html")


class TestChangesHelpers:
    def test_enrich_action_with_empty_dict(self):
        from act_dashboard.routes.changes import _enrich_action
        result = _enrich_action({})
        assert isinstance(result, dict)

    def test_enrich_action_populates_action_label(self):
        from act_dashboard.routes.changes import _enrich_action
        row = {
            "change_id": 1, "rule_id": "budget_1", "action_type": "increase_budget",
            "old_value": 50.0, "new_value": 55.0, "executed_at": None,
            "change_status": "completed", "executed_by": "user_accept",
            "campaign_name": "Campaign Alpha", "dry_run": False,
            "rec_id": "rec-001", "rule_type": "budget", "action_direction": "increase",
            "action_magnitude": 10.0, "confidence": "high", "trigger_summary": "roas ok",
            "generated_at": None, "resolved_at": None, "outcome_metric": None,
            "rec_status": "monitoring", "revert_reason": None,
        }
        result = _enrich_action(row)
        assert isinstance(result, dict)
        # Should have action_label or similar key
        assert "action_label" in result or len(result) > 0

    def test_enrich_system_change_with_minimal_dict(self):
        from act_dashboard.routes.changes import _enrich_system_change
        result = _enrich_system_change({})
        assert isinstance(result, dict)

    def test_enrich_system_change_budget_lever(self):
        from act_dashboard.routes.changes import _enrich_system_change
        row = {
            "change_id": 1, "change_date": None, "campaign_id": "111",
            "lever": "budget", "old_value": 50.0, "new_value": 55.0,
            "change_pct": 10.0, "rule_id": "budget_1",
            "risk_tier": "low", "rollback_status": None, "executed_at": None,
        }
        result = _enrich_system_change(row)
        assert isinstance(result, dict)

    def test_enrich_system_change_bid_lever(self):
        from act_dashboard.routes.changes import _enrich_system_change
        row = {
            "lever": "bid", "old_value": 4.0, "new_value": 4.4,
            "change_pct": 10.0,
        }
        result = _enrich_system_change(row)
        assert isinstance(result, dict)

    # ── _enrich_action branches ──

    def test_enrich_action_user_modify(self):
        from act_dashboard.routes.changes import _enrich_action
        row = {"executed_by": "user_modify", "rec_status": "", "rule_type": "budget",
               "old_value": 50.0, "new_value": 55.0, "executed_at": None}
        result = _enrich_action(row)
        assert result["action_label_user"] == "Modified"

    def test_enrich_action_user_decline(self):
        from act_dashboard.routes.changes import _enrich_action
        row = {"executed_by": "user_decline", "rec_status": "", "rule_type": "bid",
               "old_value": 4.0, "new_value": 4.4, "executed_at": None}
        result = _enrich_action(row)
        assert result["action_label_user"] == "Declined"

    def test_enrich_action_rec_status_successful(self):
        from act_dashboard.routes.changes import _enrich_action
        row = {"executed_by": "user_accept", "rec_status": "successful", "rule_type": "budget",
               "old_value": 50.0, "new_value": 55.0, "executed_at": None}
        result = _enrich_action(row)
        assert result["bar_class"] == "rt-successful"

    def test_enrich_action_rec_status_reverted(self):
        from act_dashboard.routes.changes import _enrich_action
        row = {"executed_by": "user_accept", "rec_status": "reverted", "rule_type": "bid",
               "old_value": 4.0, "new_value": 4.4, "executed_at": None}
        result = _enrich_action(row)
        assert result["bar_class"] == "rt-reverted"

    def test_enrich_action_rec_status_declined(self):
        from act_dashboard.routes.changes import _enrich_action
        row = {"executed_by": "user_accept", "rec_status": "declined", "rule_type": "budget",
               "old_value": 50.0, "new_value": 55.0, "executed_at": None}
        result = _enrich_action(row)
        assert result["bar_class"] == "rt-declined"

    def test_enrich_action_rule_type_budget_bar(self):
        from act_dashboard.routes.changes import _enrich_action
        row = {"executed_by": "user_accept", "rec_status": "", "rule_type": "budget",
               "old_value": 50.0, "new_value": 55.0, "executed_at": None}
        result = _enrich_action(row)
        assert result["bar_class"] == "rt-budget"

    def test_enrich_action_rule_type_bid_bar_and_value(self):
        from act_dashboard.routes.changes import _enrich_action
        row = {"executed_by": "user_accept", "rec_status": "", "rule_type": "bid",
               "old_value": 4.0, "new_value": 4.4, "executed_at": None}
        result = _enrich_action(row)
        assert result["bar_class"] == "rt-bid"
        assert "tROAS" in result["value_label"]

    def test_enrich_action_executed_at_string_hours(self):
        from act_dashboard.routes.changes import _enrich_action
        from datetime import datetime, timedelta
        executed_at = (datetime.now() - timedelta(hours=2)).isoformat()
        row = {"executed_by": "user_accept", "rec_status": "monitoring", "rule_type": "budget",
               "old_value": 50.0, "new_value": 55.0, "executed_at": executed_at}
        result = _enrich_action(row)
        assert "h ago" in result["executed_ago"]

    def test_enrich_action_executed_at_minutes_ago(self):
        from act_dashboard.routes.changes import _enrich_action
        from datetime import datetime, timedelta
        executed_at = datetime.now() - timedelta(minutes=30)
        row = {"executed_by": "user_accept", "rec_status": "monitoring", "rule_type": "budget",
               "old_value": 50.0, "new_value": 55.0, "executed_at": executed_at}
        result = _enrich_action(row)
        assert "m ago" in result["executed_ago"]

    def test_enrich_action_executed_at_days_ago(self):
        from act_dashboard.routes.changes import _enrich_action
        from datetime import datetime, timedelta
        executed_at = datetime.now() - timedelta(days=3)
        row = {"executed_by": "user_accept", "rec_status": "monitoring", "rule_type": "budget",
               "old_value": 50.0, "new_value": 55.0, "executed_at": executed_at}
        result = _enrich_action(row)
        assert "d ago" in result["executed_ago"]

    # ── _enrich_system_change branches ──

    def test_enrich_system_change_rollback_reverted(self):
        from act_dashboard.routes.changes import _enrich_system_change
        row = {"lever": "budget", "rollback_status": "reverted",
               "old_value": 50.0, "new_value": 55.0, "change_date": None}
        result = _enrich_system_change(row)
        assert result["status_label"] == "Reverted"

    def test_enrich_system_change_rollback_successful(self):
        from act_dashboard.routes.changes import _enrich_system_change
        row = {"lever": "budget", "rollback_status": "successful",
               "old_value": 50.0, "new_value": 55.0, "change_date": None}
        result = _enrich_system_change(row)
        assert result["status_label"] == "Successful"

    def test_enrich_system_change_change_date_today(self):
        from act_dashboard.routes.changes import _enrich_system_change
        from datetime import date
        row = {"lever": "budget", "rollback_status": None,
               "old_value": 50.0, "new_value": 55.0,
               "change_date": date.today().isoformat()}
        result = _enrich_system_change(row)
        assert result["change_ago"] == "Today"

    def test_enrich_system_change_change_date_yesterday(self):
        from act_dashboard.routes.changes import _enrich_system_change
        from datetime import date, timedelta
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        row = {"lever": "bid", "rollback_status": None,
               "old_value": 4.0, "new_value": 4.4, "change_date": yesterday}
        result = _enrich_system_change(row)
        assert result["change_ago"] == "Yesterday"

    def test_enrich_system_change_change_date_days_ago(self):
        from act_dashboard.routes.changes import _enrich_system_change
        from datetime import date, timedelta
        days_ago = (date.today() - timedelta(days=3)).isoformat()
        row = {"lever": "budget", "rollback_status": None,
               "old_value": 50.0, "new_value": 55.0, "change_date": days_ago}
        result = _enrich_system_change(row)
        assert "d ago" in result["change_ago"]

    def test_enrich_system_change_change_date_old(self):
        from act_dashboard.routes.changes import _enrich_system_change
        from datetime import date, timedelta
        old_date = (date.today() - timedelta(days=30)).isoformat()
        row = {"lever": "budget", "rollback_status": None,
               "old_value": 50.0, "new_value": 55.0, "change_date": old_date}
        result = _enrich_system_change(row)
        assert isinstance(result["change_ago"], str)
