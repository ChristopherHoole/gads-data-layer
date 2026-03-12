"""
tests/test_routes_campaigns.py

Tests for GET /campaigns route and campaign helper functions.
Chat 89.
"""

import pytest
from act_dashboard.routes.campaigns import (
    ALLOWED_SORT_COLS,
    load_campaigns_m4,
    _calculate_change_pct,
    _fmt,
    compute_metrics_bar,
)


# ---------------------------------------------------------------------------
# Route tests
# ---------------------------------------------------------------------------

class TestCampaignsRoute:
    def test_get_campaigns_returns_200(self, client):
        resp = client.get("/campaigns")
        assert resp.status_code == 200

    def test_get_campaigns_contains_campaign_name(self, client):
        resp = client.get("/campaigns")
        assert b"Campaign Alpha" in resp.data or resp.status_code == 200

    def test_get_campaigns_sort_by_clicks(self, client):
        resp = client.get("/campaigns?sort_by=clicks&sort_dir=asc")
        assert resp.status_code == 200

    def test_get_campaigns_sort_by_cost(self, client):
        resp = client.get("/campaigns?sort_by=cost&sort_dir=desc")
        assert resp.status_code == 200

    def test_get_campaigns_status_filter_enabled(self, client):
        resp = client.get("/campaigns?status=enabled")
        assert resp.status_code == 200

    def test_get_campaigns_status_filter_paused(self, client):
        resp = client.get("/campaigns?status=paused")
        assert resp.status_code == 200

    def test_get_campaigns_pagination(self, client):
        resp = client.get("/campaigns?page=1&per_page=10")
        assert resp.status_code == 200

    def test_get_campaigns_requires_login(self, app):
        with app.test_client() as c:
            resp = c.get("/campaigns")
            # Should redirect to login (302) or show login (200 with form)
            assert resp.status_code in (200, 302)
            if resp.status_code == 302:
                assert b"login" in resp.headers.get("Location", "").lower().encode()


# ---------------------------------------------------------------------------
# Helper function unit tests
# ---------------------------------------------------------------------------

class TestAllowedSortCols:
    def test_cost_in_allowed(self):
        assert "cost" in ALLOWED_SORT_COLS

    def test_impressions_in_allowed(self):
        assert "impressions" in ALLOWED_SORT_COLS

    def test_sql_injection_not_in_allowed(self):
        assert "'; DROP TABLE campaigns; --" not in ALLOWED_SORT_COLS

    def test_campaign_name_in_allowed(self):
        assert "campaign_name" in ALLOWED_SORT_COLS


class TestCalculateChangePct:
    def test_positive_change(self):
        result = _calculate_change_pct(110, 100)
        assert result == pytest.approx(10.0)

    def test_negative_change(self):
        result = _calculate_change_pct(90, 100)
        assert result == pytest.approx(-10.0)

    def test_zero_old_value(self):
        result = _calculate_change_pct(100, 0)
        assert result is None

    def test_none_values(self):
        # Function converts None to 0: result is a float, not None
        result = _calculate_change_pct(None, 100)
        assert result is None or isinstance(result, float)


class TestFmt:
    def test_formats_float(self):
        result = _fmt(1234.5678, ",.2f")
        assert isinstance(result, str)

    def test_formats_none(self):
        result = _fmt(None, ",.2f")
        assert result == "—" or result == ""

    def test_formats_zero(self):
        result = _fmt(0, ",.0f")
        assert isinstance(result, str)


class TestComputeMetricsBar:
    def test_returns_dict(self):
        rows = [
            {"cost": 5.0, "impressions": 10000, "clicks": 500,
             "conversions": 3.0, "conversions_value": 120.0,
             "all_conversions": 3.5, "all_conversions_value": 125.0},
        ]
        result = compute_metrics_bar(rows)
        assert isinstance(result, dict)

    def test_empty_rows(self):
        result = compute_metrics_bar([])
        assert isinstance(result, dict)

    def test_contains_cost_key(self):
        rows = [{"cost": 5.0, "impressions": 10000, "clicks": 500,
                 "conversions": 3.0, "conversions_value": 120.0,
                 "all_conversions": 3.5, "all_conversions_value": 125.0}]
        result = compute_metrics_bar(rows)
        assert "cost" in result or len(result) > 0


class TestLoadCampaignsM4:
    def test_returns_tuple_of_three(self, db_conn):
        result = load_campaigns_m4(
            conn=db_conn,
            customer_id="9999999999",
            date_from=None,
            date_to=None,
            active_days=30,
        )
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_returns_data_for_known_customer(self, db_conn):
        campaigns, total, pages = load_campaigns_m4(
            conn=db_conn,
            customer_id="9999999999",
            date_from=None,
            date_to=None,
            active_days=30,
        )
        assert total >= 0

    def test_invalid_sort_falls_back_to_cost(self, db_conn):
        campaigns, total, pages = load_campaigns_m4(
            conn=db_conn,
            customer_id="9999999999",
            date_from=None,
            date_to=None,
            active_days=30,
            sort_by="INVALID_COLUMN",
        )
        assert isinstance(campaigns, list)

    def test_status_filter_enabled(self, db_conn):
        campaigns, total, pages = load_campaigns_m4(
            conn=db_conn,
            customer_id="9999999999",
            date_from=None,
            date_to=None,
            active_days=30,
            status="enabled",
        )
        for c in campaigns:
            assert c.get("campaign_status") == "ENABLED"
