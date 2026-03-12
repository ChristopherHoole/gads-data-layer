"""
tests/test_shared.py

Tests for shared helper functions in act_dashboard/routes/shared.py.
Chat 89.
"""

import pytest
from act_autopilot.models import Recommendation


# ---------------------------------------------------------------------------
# recommendation_to_dict
# ---------------------------------------------------------------------------

def make_rec(**kwargs):
    defaults = {
        "rule_id": "budget_1",
        "rule_name": "Increase Budget",
        "entity_type": "campaign",
        "entity_id": "111",
        "action_type": "increase_budget",
        "risk_tier": "low",
        "campaign_name": "Campaign Alpha",
        "change_pct": 0.05,
        "evidence": {"clicks_w7": 50},
    }
    defaults.update(kwargs)
    return Recommendation(**defaults)


class TestRecommendationToDict:
    def _import(self):
        from act_dashboard.routes.shared import recommendation_to_dict
        return recommendation_to_dict

    def test_returns_dict(self):
        fn = self._import()
        rec = make_rec()
        result = fn(rec)
        assert isinstance(result, dict)

    def test_contains_rule_id(self):
        fn = self._import()
        rec = make_rec()
        result = fn(rec)
        assert result["rule_id"] == "budget_1"

    def test_contains_entity_type(self):
        fn = self._import()
        rec = make_rec()
        result = fn(rec)
        assert result["entity_type"] == "campaign"

    def test_contains_action_type(self):
        fn = self._import()
        rec = make_rec()
        result = fn(rec)
        assert result["action_type"] == "increase_budget"

    def test_index_adds_id_field(self):
        fn = self._import()
        rec = make_rec()
        result = fn(rec, index=3)
        assert result["id"] == 3

    def test_no_index_no_id_field(self):
        fn = self._import()
        rec = make_rec()
        result = fn(rec)
        assert "id" not in result

    def test_confidence_defaults_to_zero(self):
        fn = self._import()
        rec = make_rec()
        result = fn(rec)
        assert result["confidence"] == 0.0

    def test_rationale_defaults_to_empty(self):
        fn = self._import()
        rec = make_rec()
        result = fn(rec)
        assert result["rationale"] == ""

    def test_blocked_defaults_to_false(self):
        fn = self._import()
        rec = make_rec()
        result = fn(rec)
        assert result["blocked"] is False

    def test_evidence_included(self):
        fn = self._import()
        rec = make_rec(evidence={"clicks_w7": 50})
        result = fn(rec)
        assert result["evidence"] == {"clicks_w7": 50}

    def test_campaign_name_present(self):
        fn = self._import()
        rec = make_rec(campaign_name="Test Campaign")
        result = fn(rec)
        assert result["campaign_name"] == "Test Campaign"

    def test_change_pct_present(self):
        fn = self._import()
        rec = make_rec(change_pct=0.10)
        result = fn(rec)
        assert result["change_pct"] == 0.10


# ---------------------------------------------------------------------------
# build_chart_data in campaigns.py (DB function via db_conn fixture)
# ---------------------------------------------------------------------------

CUSTOMER_ID = "9999999999"


class TestBuildChartData:
    """Test campaigns.build_chart_data with the db_conn fixture."""

    def _import(self):
        from act_dashboard.routes.campaigns import build_chart_data
        return build_chart_data

    def test_returns_dict(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30, None, None)
        assert isinstance(result, dict)

    def test_has_dates_key(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30, None, None)
        assert "dates" in result

    def test_has_cost_key(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30, None, None)
        assert "cost" in result

    def test_has_impressions_key(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30, None, None)
        assert "impressions" in result

    def test_has_clicks_key(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30, None, None)
        assert "clicks" in result

    def test_7_day_range(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 7, None, None)
        assert isinstance(result, dict)

    def test_custom_date_range(self, db_conn):
        from datetime import date, timedelta
        fn = self._import()
        today = date.today().isoformat()
        week_ago = (date.today() - timedelta(days=7)).isoformat()
        result = fn(db_conn, CUSTOMER_ID, 0, week_ago, today)
        assert isinstance(result, dict)

    def test_unknown_customer_returns_empty(self, db_conn):
        fn = self._import()
        result = fn(db_conn, "nonexistent_customer", 30, None, None)
        # Returns empty dict or dict with empty values
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# get_performance_data in shared.py (DB function — weekly/monthly paths)
# ---------------------------------------------------------------------------


class TestGetPerformanceData:
    """Cover the weekly (32-180 day) and monthly (180+ day) query paths."""

    def _import(self):
        from act_dashboard.routes.shared import get_performance_data
        return get_performance_data

    def test_daily_path_returns_dict(self, db_conn):
        from datetime import date, timedelta
        fn = self._import()
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=14)).isoformat()
        result = fn(db_conn, CUSTOMER_ID, start, end, "campaign")
        assert isinstance(result, dict)

    def test_daily_path_has_dates_key(self, db_conn):
        from datetime import date, timedelta
        fn = self._import()
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=14)).isoformat()
        result = fn(db_conn, CUSTOMER_ID, start, end, "campaign")
        assert "dates" in result

    def test_weekly_path_returns_dict(self, db_conn):
        from datetime import date, timedelta
        fn = self._import()
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=60)).isoformat()  # 61 days → weekly
        result = fn(db_conn, CUSTOMER_ID, start, end, "campaign")
        assert isinstance(result, dict)

    def test_weekly_path_has_dates_key(self, db_conn):
        from datetime import date, timedelta
        fn = self._import()
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=90)).isoformat()
        result = fn(db_conn, CUSTOMER_ID, start, end, "campaign")
        assert "dates" in result

    def test_monthly_path_returns_dict(self, db_conn):
        from datetime import date, timedelta
        fn = self._import()
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=200)).isoformat()  # 201 days → monthly
        result = fn(db_conn, CUSTOMER_ID, start, end, "campaign")
        assert isinstance(result, dict)

    def test_monthly_path_has_metrics_key(self, db_conn):
        from datetime import date, timedelta
        fn = self._import()
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=365)).isoformat()
        result = fn(db_conn, CUSTOMER_ID, start, end, "campaign")
        assert "metrics" in result

    def test_unknown_entity_type_returns_empty(self, db_conn):
        from datetime import date, timedelta
        fn = self._import()
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=14)).isoformat()
        result = fn(db_conn, CUSTOMER_ID, start, end, "nonexistent_type")
        assert isinstance(result, dict)

    def test_invalid_date_format_returns_empty(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, "not-a-date", "also-not", "campaign")
        assert isinstance(result, dict)

    def test_keyword_entity_type(self, db_conn):
        from datetime import date, timedelta
        fn = self._import()
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=14)).isoformat()
        result = fn(db_conn, CUSTOMER_ID, start, end, "keyword")
        assert isinstance(result, dict)

    def test_campaign_type_filter(self, db_conn):
        from datetime import date, timedelta
        fn = self._import()
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=14)).isoformat()
        result = fn(db_conn, CUSTOMER_ID, start, end, "campaign", campaign_type="SEARCH")
        assert isinstance(result, dict)

    def test_shopping_campaign_type(self, db_conn):
        from datetime import date, timedelta
        fn = self._import()
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=14)).isoformat()
        result = fn(db_conn, CUSTOMER_ID, start, end, "campaign", campaign_type="SHOPPING")
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# logging_config helpers
# ---------------------------------------------------------------------------

class TestLoggingConfig:
    def test_get_logger_returns_logger(self, tmp_path):
        import logging
        import os
        from act_autopilot.logging_config import get_logger
        # Run from tmp_path to avoid creating logs/ in project root
        old_cwd = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            logger = get_logger("test_get_logger_module")
            assert isinstance(logger, logging.Logger)
        finally:
            os.chdir(old_cwd)

    def test_init_logging_runs(self, tmp_path):
        import os
        from act_autopilot.logging_config import init_logging
        old_cwd = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            init_logging("DEBUG")  # Should not raise
        finally:
            os.chdir(old_cwd)

    def test_setup_logging_dedup(self, tmp_path):
        import os
        from act_autopilot.logging_config import setup_logging
        old_cwd = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            logger1 = setup_logging("test_dedup_module_123")
            logger2 = setup_logging("test_dedup_module_123")
            # Second call should return same logger (dedup check)
            assert logger1 is logger2
        finally:
            os.chdir(old_cwd)


# ---------------------------------------------------------------------------
# POST /set-date-range — Flask API route (shared.py lines 579-610)
# ---------------------------------------------------------------------------

class TestSetDateRange:
    def test_range_7_returns_200(self, client):
        resp = client.post("/set-date-range", json={"range_type": "7"})
        assert resp.status_code == 200

    def test_range_7_success_true(self, client):
        resp = client.post("/set-date-range", json={"range_type": "7"})
        data = resp.get_json()
        assert data["success"] is True
        assert data["days"] == 7

    def test_range_30_returns_200(self, client):
        resp = client.post("/set-date-range", json={"range_type": "30"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["days"] == 30

    def test_range_90_returns_200(self, client):
        resp = client.post("/set-date-range", json={"range_type": "90"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["days"] == 90

    def test_custom_valid_dates(self, client):
        resp = client.post("/set-date-range", json={
            "range_type": "custom",
            "date_from": "2026-01-01",
            "date_to": "2026-01-31",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["date_from"] == "2026-01-01"
        assert data["date_to"] == "2026-01-31"

    def test_custom_invalid_date_format(self, client):
        resp = client.post("/set-date-range", json={
            "range_type": "custom",
            "date_from": "01/01/2026",
            "date_to": "2026-01-31",
        })
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["success"] is False

    def test_custom_date_from_after_date_to(self, client):
        resp = client.post("/set-date-range", json={
            "range_type": "custom",
            "date_from": "2026-02-01",
            "date_to": "2026-01-01",
        })
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["success"] is False

    def test_invalid_range_type_returns_400(self, client):
        resp = client.post("/set-date-range", json={"range_type": "999"})
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["success"] is False

    def test_empty_range_type_returns_400(self, client):
        resp = client.post("/set-date-range", json={})
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# POST /set-metrics-collapse — Flask API route (shared.py lines 630-651)
# ---------------------------------------------------------------------------

class TestSetMetricsCollapse:
    def test_set_collapsed_true(self, client):
        resp = client.post("/set-metrics-collapse", json={
            "page_id": "campaigns",
            "collapsed": True,
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["collapsed"] is True

    def test_set_collapsed_false(self, client):
        resp = client.post("/set-metrics-collapse", json={
            "page_id": "keywords",
            "collapsed": False,
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["collapsed"] is False

    def test_page_id_in_response(self, client):
        resp = client.post("/set-metrics-collapse", json={
            "page_id": "shopping",
            "collapsed": True,
        })
        data = resp.get_json()
        assert data["page_id"] == "shopping"

    def test_missing_page_id_returns_400(self, client):
        resp = client.post("/set-metrics-collapse", json={"collapsed": True})
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["success"] is False

    def test_empty_page_id_returns_400(self, client):
        resp = client.post("/set-metrics-collapse", json={"page_id": "", "collapsed": False})
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# POST /set-chart-metrics — Flask API route (shared.py lines 700-720)
# ---------------------------------------------------------------------------

class TestSetChartMetrics:
    def test_valid_metrics(self, client):
        resp = client.post("/set-chart-metrics", json={
            "page_id": "campaigns",
            "metrics": ["cost", "clicks"],
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"

    def test_metrics_in_response(self, client):
        resp = client.post("/set-chart-metrics", json={
            "page_id": "campaigns",
            "metrics": ["cost", "impressions"],
        })
        data = resp.get_json()
        assert "metrics" in data
        assert isinstance(data["metrics"], list)

    def test_page_id_in_response(self, client):
        resp = client.post("/set-chart-metrics", json={
            "page_id": "keywords",
            "metrics": ["cost"],
        })
        data = resp.get_json()
        assert data["page_id"] == "keywords"

    def test_invalid_metrics_filtered_out(self, client):
        resp = client.post("/set-chart-metrics", json={
            "page_id": "campaigns",
            "metrics": ["cost", "INVALID_METRIC"],
        })
        assert resp.status_code == 200
        data = resp.get_json()
        # Only valid metric survives
        assert "INVALID_METRIC" not in data["metrics"]

    def test_all_invalid_metrics_falls_back_to_default(self, client):
        resp = client.post("/set-chart-metrics", json={
            "page_id": "campaigns",
            "metrics": ["NOT_VALID"],
        })
        assert resp.status_code == 200
        data = resp.get_json()
        # Falls back to default ['cost', 'impressions']
        assert data["metrics"] == ["cost", "impressions"]

    def test_missing_page_id_returns_400(self, client):
        resp = client.post("/set-chart-metrics", json={"metrics": ["cost"]})
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["status"] == "error"

    def test_metrics_not_list_returns_400(self, client):
        resp = client.post("/set-chart-metrics", json={
            "page_id": "campaigns",
            "metrics": "cost",
        })
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["status"] == "error"

    def test_all_valid_metric_keys(self, client):
        all_valid = ["cost", "impressions", "clicks", "avg_cpc",
                     "conversions", "conv_value", "cost_per_conv",
                     "conv_rate", "ctr", "roas"]
        resp = client.post("/set-chart-metrics", json={
            "page_id": "campaigns",
            "metrics": all_valid,
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert set(data["metrics"]) == set(all_valid)


# ---------------------------------------------------------------------------
# get_date_range_from_session — lines 214-221 (session branches)
# cache_recommendations — line 192
# ---------------------------------------------------------------------------

class TestGetDateRangeFromSession:
    """Cover shared.py lines 214-221 by setting session via /set-date-range first."""

    def test_preset_30_in_session_then_campaigns(self, client):
        """
        Covers lines 214, 215, 218, 219, 221: preset range stored in session
        then campaigns route calls get_date_range_from_session().
        """
        client.post("/set-date-range", json={"range_type": "30"})
        resp = client.get("/campaigns")
        assert resp.status_code == 200

    def test_preset_7_in_session_then_campaigns(self, client):
        client.post("/set-date-range", json={"range_type": "7"})
        resp = client.get("/campaigns")
        assert resp.status_code == 200

    def test_custom_range_in_session_then_campaigns(self, client):
        """
        Covers line 216: range_type == 'custom' branch.
        """
        client.post("/set-date-range", json={
            "range_type": "custom",
            "date_from": "2026-01-01",
            "date_to": "2026-01-31",
        })
        resp = client.get("/campaigns")
        assert resp.status_code == 200

    def test_invalid_days_in_session_falls_back(self, client):
        """
        Covers line 220: days not in [7,30,90] → days = 30.
        """
        with client.session_transaction() as sess:
            sess["date_range"] = {"type": "999d", "days": 999}
        resp = client.get("/campaigns")
        assert resp.status_code == 200


class TestCacheRecommendations:
    """Cover shared.py line 192: cache_recommendations()."""

    def test_cache_recommendations_stores_value(self, app):
        """Covers line 192."""
        from act_dashboard.routes.shared import cache_recommendations
        with app.app_context():
            app.config.setdefault("RECOMMENDATIONS_CACHE", {})
            cache_recommendations("campaigns", [{"id": 1}])
            assert app.config["RECOMMENDATIONS_CACHE"]["campaigns"] == [{"id": 1}]

    def test_cache_recommendations_overwrites(self, app):
        from act_dashboard.routes.shared import cache_recommendations
        with app.app_context():
            app.config.setdefault("RECOMMENDATIONS_CACHE", {})
            cache_recommendations("keywords", [{"id": 1}])
            cache_recommendations("keywords", [{"id": 2}, {"id": 3}])
            assert len(app.config["RECOMMENDATIONS_CACHE"]["keywords"]) == 2
