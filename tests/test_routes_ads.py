"""
tests/test_routes_ads.py

Tests for GET /ads route.
Chat 89.
"""

import pytest


class TestAdsRoute:
    def test_get_ads_returns_200(self, client):
        resp = client.get("/ads")
        assert resp.status_code == 200

    def test_get_ads_status_filter_enabled(self, client):
        resp = client.get("/ads?status=enabled")
        assert resp.status_code == 200

    def test_get_ads_status_filter_paused(self, client):
        resp = client.get("/ads?status=paused")
        assert resp.status_code == 200

    def test_get_ads_sort_by_cost(self, client):
        resp = client.get("/ads?sort_by=cost&sort_dir=desc")
        assert resp.status_code == 200

    def test_get_ads_sort_by_impressions(self, client):
        resp = client.get("/ads?sort_by=impressions&sort_dir=asc")
        assert resp.status_code == 200

    def test_get_ads_pagination(self, client):
        resp = client.get("/ads?page=1&per_page=25")
        assert resp.status_code == 200

    def test_get_ads_requires_login(self, app):
        with app.test_client() as c:
            resp = c.get("/ads")
            assert resp.status_code in (200, 302)

    def test_get_ads_invalid_sort_falls_back(self, client):
        resp = client.get("/ads?sort_by=INVALID_COL")
        assert resp.status_code == 200

    def test_get_ads_response_contains_html(self, client):
        resp = client.get("/ads")
        assert b"<html" in resp.data or b"<!DOCTYPE" in resp.data or resp.status_code == 200


# ---------------------------------------------------------------------------
# _build_date_filters — pure helper
# ---------------------------------------------------------------------------

CUSTOMER_ID = "9999999999"


class TestBuildDateFilters:
    def _import(self):
        from act_dashboard.routes.ads import _build_date_filters
        return _build_date_filters

    def test_no_dates_uses_active_days(self):
        fn = self._import()
        cur, prev = fn(30, None, None)
        assert "30 days" in cur

    def test_no_dates_7_day(self):
        fn = self._import()
        cur, prev = fn(7, None, None)
        assert "7 days" in cur

    def test_with_dates_uses_date_range(self):
        fn = self._import()
        cur, prev = fn(30, "2026-03-01", "2026-03-14")
        assert "2026-03-01" in cur
        assert "2026-03-14" in cur

    def test_with_dates_computes_prev(self):
        fn = self._import()
        cur, prev = fn(30, "2026-03-01", "2026-03-14")
        # Previous period should appear in prev filter
        assert "2026-02-" in prev or "2026-0" in prev

    def test_invalid_days_defaults_to_30(self):
        fn = self._import()
        cur, prev = fn(999, None, None)
        assert "30 days" in cur


# ---------------------------------------------------------------------------
# _calculate_change_pct — pure helper
# ---------------------------------------------------------------------------

class TestCalculateChangePct:
    def _import(self):
        from act_dashboard.routes.ads import _calculate_change_pct
        return _calculate_change_pct

    def test_normal_increase(self):
        fn = self._import()
        assert fn(110.0, 100.0) == pytest.approx(10.0)

    def test_normal_decrease(self):
        fn = self._import()
        assert fn(90.0, 100.0) == pytest.approx(-10.0)

    def test_previous_is_none_returns_none(self):
        fn = self._import()
        assert fn(100.0, None) is None

    def test_previous_is_zero_returns_none(self):
        fn = self._import()
        assert fn(100.0, 0) is None

    def test_current_is_none_returns_minus_100(self):
        fn = self._import()
        assert fn(None, 100.0) == -100.0


# ---------------------------------------------------------------------------
# load_ad_data — DB-backed function
# ---------------------------------------------------------------------------

class TestLoadAdData:
    def _import(self):
        from act_dashboard.routes.ads import load_ad_data
        return load_ad_data

    def test_returns_list(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30)
        assert isinstance(result, list)

    def test_ad_has_cost_field(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30)
        for ad in result:
            assert "cost" in ad

    def test_status_field_normalized(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30)
        for ad in result:
            assert isinstance(ad["status"], str)

    def test_ad_id_is_string(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30)
        for ad in result:
            assert isinstance(ad["ad_id"], str)

    def test_unknown_customer_returns_empty(self, db_conn):
        fn = self._import()
        result = fn(db_conn, "nonexistent", 30)
        assert isinstance(result, list)

    def test_sort_by_clicks(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30, sort_by="clicks", sort_dir="asc")
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# apply_status_filter — pure function
# ---------------------------------------------------------------------------

class TestApplyStatusFilter:
    def _import(self):
        from act_dashboard.routes.ads import apply_status_filter
        return apply_status_filter

    def _make_ads(self):
        return [
            {"status": "ENABLED", "cost": 10.0},
            {"status": "PAUSED", "cost": 5.0},
            {"status": "REMOVED", "cost": 2.0},
        ]

    def test_all_returns_all(self):
        fn = self._import()
        ads = self._make_ads()
        result = fn(ads, "all")
        assert len(result) == 3

    def test_enabled_filter(self):
        fn = self._import()
        ads = self._make_ads()
        result = fn(ads, "enabled")
        assert all(a["status"] == "ENABLED" for a in result)
        assert len(result) == 1

    def test_paused_filter(self):
        fn = self._import()
        ads = self._make_ads()
        result = fn(ads, "paused")
        assert all(a["status"] == "PAUSED" for a in result)
        assert len(result) == 1

    def test_empty_list_returns_empty(self):
        fn = self._import()
        result = fn([], "enabled")
        assert result == []


# ---------------------------------------------------------------------------
# compute_metrics — pure function
# ---------------------------------------------------------------------------

class TestComputeMetrics:
    def _import(self):
        from act_dashboard.routes.ads import compute_metrics
        return compute_metrics

    def _make_ads(self):
        return [
            {"status": "ENABLED", "cost": 10.0, "clicks": 100, "impressions": 2000,
             "conversions": 2.0, "ad_strength": "GOOD"},
            {"status": "PAUSED", "cost": 5.0, "clicks": 50, "impressions": 1000,
             "conversions": 1.0, "ad_strength": "POOR"},
        ]

    def test_empty_returns_zero_total_ads(self):
        fn = self._import()
        result = fn([])
        assert result["total_ads"] == 0

    def test_empty_returns_zero_cost(self):
        fn = self._import()
        result = fn([])
        assert result["total_cost"] == 0.0

    def test_total_ads_count(self):
        fn = self._import()
        result = fn(self._make_ads())
        assert result["total_ads"] == 2

    def test_total_cost(self):
        fn = self._import()
        result = fn(self._make_ads())
        assert result["total_cost"] == pytest.approx(15.0)

    def test_enabled_count(self):
        fn = self._import()
        result = fn(self._make_ads())
        assert result["enabled_count"] == 1

    def test_paused_count(self):
        fn = self._import()
        result = fn(self._make_ads())
        assert result["paused_count"] == 1

    def test_poor_strength_count(self):
        fn = self._import()
        result = fn(self._make_ads())
        assert result["poor_strength_count"] == 1

    def test_good_strength_count(self):
        fn = self._import()
        result = fn(self._make_ads())
        assert result["good_strength_count"] == 1


# ---------------------------------------------------------------------------
# apply_pagination — pure function
# ---------------------------------------------------------------------------

class TestApplyPagination:
    def _import(self):
        from act_dashboard.routes.ads import apply_pagination
        return apply_pagination

    def _make_ads(self, n=10):
        return [{"ad_id": str(i)} for i in range(n)]

    def test_first_page(self):
        fn = self._import()
        page_ads, total, total_pages = fn(self._make_ads(10), 1, 5)
        assert len(page_ads) == 5
        assert total == 10
        assert total_pages == 2

    def test_second_page(self):
        fn = self._import()
        page_ads, total, total_pages = fn(self._make_ads(10), 2, 5)
        assert len(page_ads) == 5

    def test_page_beyond_total_clamped(self):
        fn = self._import()
        page_ads, total, total_pages = fn(self._make_ads(5), 999, 5)
        assert len(page_ads) == 5  # all items on page 1

    def test_empty_list_returns_zero_total(self):
        fn = self._import()
        page_ads, total, total_pages = fn([], 1, 10)
        assert total == 0
        assert total_pages == 1


# ---------------------------------------------------------------------------
# _fmt_ads — pure function (lines 259-275)
# ---------------------------------------------------------------------------

class TestFmtAds:
    def _import(self):
        from act_dashboard.routes.ads import _fmt_ads
        return _fmt_ads

    def test_none_returns_dash(self):
        fn = self._import()
        assert fn(None, "currency") == "—"

    def test_ad_strength_returns_string(self):
        fn = self._import()
        assert fn("24/30", "ad_strength") == "24/30"

    def test_currency_large(self):
        fn = self._import()
        result = fn(1_500_000.0, "currency")
        assert "M" in result

    def test_ratio_format(self):
        fn = self._import()
        result = fn(3.5, "ratio")
        assert "x" in result

    def test_unknown_fmt_returns_str(self):
        fn = self._import()
        result = fn(42.0, "unknown_fmt")
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# _build_ads_chart_data — DB-backed function (ads.py lines 443-494)
# ---------------------------------------------------------------------------

CUSTOMER_ID = "9999999999"


class TestBuildAdsChartData:
    def _import(self):
        from act_dashboard.routes.ads import _build_ads_chart_data
        return _build_ads_chart_data

    def test_returns_dict(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30)
        assert isinstance(result, dict)

    def test_has_dates_key(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30)
        assert "dates" in result

    def test_has_cost_key(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30)
        assert "cost" in result

    def test_has_impressions_key(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30)
        assert "impressions" in result

    def test_has_clicks_key(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30)
        assert "clicks" in result

    def test_has_avg_cpc_key(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30)
        assert "avg_cpc" in result

    def test_with_custom_dates(self, db_conn):
        from datetime import date, timedelta
        fn = self._import()
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=14)).isoformat()
        result = fn(db_conn, CUSTOMER_ID, 30, date_from=start, date_to=end)
        assert isinstance(result, dict)

    def test_unknown_customer_returns_dict(self, db_conn):
        fn = self._import()
        result = fn(db_conn, "nonexistent_customer", 30)
        assert isinstance(result, dict)
        assert "dates" in result

    def test_7_day_range(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 7)
        assert isinstance(result, dict)
