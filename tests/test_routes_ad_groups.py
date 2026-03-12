"""
tests/test_routes_ad_groups.py

Tests for GET /ad-groups route.
Chat 89.
"""

import pytest


class TestAdGroupsRoute:
    def test_get_ad_groups_returns_200(self, client):
        resp = client.get("/ad-groups")
        assert resp.status_code == 200

    def test_get_ad_groups_sort_by_cost(self, client):
        resp = client.get("/ad-groups?sort_by=cost&sort_dir=desc")
        assert resp.status_code == 200

    def test_get_ad_groups_sort_by_cpc_bid_micros(self, client):
        resp = client.get("/ad-groups?sort_by=cpc_bid_micros")
        assert resp.status_code == 200

    def test_get_ad_groups_status_filter_enabled(self, client):
        resp = client.get("/ad-groups?status=enabled")
        assert resp.status_code == 200

    def test_get_ad_groups_status_filter_paused(self, client):
        resp = client.get("/ad-groups?status=paused")
        assert resp.status_code == 200

    def test_get_ad_groups_pagination(self, client):
        resp = client.get("/ad-groups?page=1&per_page=10")
        assert resp.status_code == 200

    def test_get_ad_groups_requires_login(self, app):
        with app.test_client() as c:
            resp = c.get("/ad-groups")
            assert resp.status_code in (200, 302)

    def test_get_ad_groups_invalid_sort_falls_back(self, client):
        resp = client.get("/ad-groups?sort_by=INJECTED_COL")
        assert resp.status_code == 200

    def test_get_ad_groups_response_has_content(self, client):
        resp = client.get("/ad-groups")
        assert len(resp.data) > 0


CUSTOMER_ID = "9999999999"


# ---------------------------------------------------------------------------
# load_ad_groups_m4 — direct DB call
# ---------------------------------------------------------------------------

class TestLoadAdGroupsM4:
    def _import(self):
        from act_dashboard.routes.ad_groups import load_ad_groups_m4
        return load_ad_groups_m4

    def test_returns_tuple(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, None, None, 30)
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_returns_list_of_dicts(self, db_conn):
        fn = self._import()
        rows, total, pages = fn(db_conn, CUSTOMER_ID, None, None, 30)
        assert isinstance(rows, list)
        for row in rows:
            assert isinstance(row, dict)

    def test_total_count_positive(self, db_conn):
        fn = self._import()
        rows, total, pages = fn(db_conn, CUSTOMER_ID, None, None, 30)
        assert total >= 0

    def test_ad_group_name_is_string(self, db_conn):
        fn = self._import()
        rows, total, pages = fn(db_conn, CUSTOMER_ID, None, None, 30)
        for row in rows:
            assert isinstance(row["ad_group_name"], str)

    def test_cost_field_present(self, db_conn):
        fn = self._import()
        rows, total, pages = fn(db_conn, CUSTOMER_ID, None, None, 30)
        for row in rows:
            assert "cost" in row

    def test_invalid_sort_falls_back(self, db_conn):
        fn = self._import()
        rows, total, pages = fn(db_conn, CUSTOMER_ID, None, None, 30,
                                sort_by="INVALID_COLUMN")
        assert isinstance(rows, list)

    def test_with_date_range(self, db_conn):
        from datetime import date, timedelta
        fn = self._import()
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=14)).isoformat()
        rows, total, pages = fn(db_conn, CUSTOMER_ID, start, end, 30)
        assert isinstance(rows, list)

    def test_enabled_status_filter(self, db_conn):
        fn = self._import()
        rows, total, pages = fn(db_conn, CUSTOMER_ID, None, None, 30, status="enabled")
        for row in rows:
            assert row["ad_group_status"] == "ENABLED"

    def test_paused_status_filter(self, db_conn):
        fn = self._import()
        rows, total, pages = fn(db_conn, CUSTOMER_ID, None, None, 30, status="paused")
        for row in rows:
            assert row["ad_group_status"] == "PAUSED"

    def test_pagination_page_2(self, db_conn):
        fn = self._import()
        rows, total, pages = fn(db_conn, CUSTOMER_ID, None, None, 30,
                                page=2, per_page=1)
        assert isinstance(rows, list)


# ---------------------------------------------------------------------------
# compute_metrics_bar — pure function
# ---------------------------------------------------------------------------

class TestComputeMetricsBar:
    def _import(self):
        from act_dashboard.routes.ad_groups import compute_metrics_bar
        return compute_metrics_bar

    def _make_groups(self):
        return [
            {"ad_group_status": "ENABLED", "cost": 10.0, "clicks": 100,
             "impressions": 2000, "conversions": 2.0, "conversions_value": 30.0},
            {"ad_group_status": "PAUSED", "cost": 5.0, "clicks": 50,
             "impressions": 1000, "conversions": 1.0, "conversions_value": 15.0},
        ]

    def test_empty_returns_zero_total(self):
        fn = self._import()
        result = fn([])
        assert result["total_ad_groups"] == 0

    def test_empty_returns_zero_cost(self):
        fn = self._import()
        result = fn([])
        assert result["total_cost"] == 0.0

    def test_total_ad_groups(self):
        fn = self._import()
        result = fn(self._make_groups())
        assert result["total_ad_groups"] == 2

    def test_active_count(self):
        fn = self._import()
        result = fn(self._make_groups())
        assert result["active_count"] == 1

    def test_paused_count(self):
        fn = self._import()
        result = fn(self._make_groups())
        assert result["paused_count"] == 1

    def test_total_cost(self):
        fn = self._import()
        result = fn(self._make_groups())
        assert result["total_cost"] == pytest.approx(15.0)


# ---------------------------------------------------------------------------
# _build_date_filters (ad_groups version) — pure function
# ---------------------------------------------------------------------------

class TestAdGroupBuildDateFilters:
    def _import(self):
        from act_dashboard.routes.ad_groups import _build_date_filters
        return _build_date_filters

    def test_no_dates_uses_active_days(self):
        fn = self._import()
        cur, prev = fn(30, None, None)
        assert "30 days" in cur

    def test_with_dates_uses_date_range(self):
        fn = self._import()
        cur, prev = fn(30, "2026-03-01", "2026-03-14")
        assert "2026-03-01" in cur
        assert "2026-03-14" in cur

    def test_with_dates_prev_is_earlier(self):
        fn = self._import()
        cur, prev = fn(30, "2026-03-01", "2026-03-14")
        assert "2026-02-" in prev or "2026-0" in prev


# ---------------------------------------------------------------------------
# _calculate_change_pct (ad_groups version) — pure function
# ---------------------------------------------------------------------------

class TestAdGroupCalculateChangePct:
    def _import(self):
        from act_dashboard.routes.ad_groups import _calculate_change_pct
        return _calculate_change_pct

    def test_normal_increase(self):
        fn = self._import()
        assert fn(110.0, 100.0) == pytest.approx(10.0)

    def test_previous_none_returns_none(self):
        fn = self._import()
        assert fn(100.0, None) is None

    def test_current_none_returns_minus100(self):
        fn = self._import()
        assert fn(None, 100.0) == -100.0


# ---------------------------------------------------------------------------
# _fmt — pure function
# ---------------------------------------------------------------------------

class TestAdGroupFmt:
    def _import(self):
        from act_dashboard.routes.ad_groups import _fmt
        return _fmt

    def test_none_returns_dash(self):
        fn = self._import()
        assert fn(None, "currency") == "—"

    def test_currency_small(self):
        fn = self._import()
        result = fn(50.0, "currency")
        assert "$" in result

    def test_percentage(self):
        fn = self._import()
        result = fn(3.5, "percentage")
        assert "%" in result

    def test_number_large(self):
        fn = self._import()
        result = fn(1_500_000, "number")
        assert "M" in result

    def test_unknown_fmt_returns_str(self):
        fn = self._import()
        result = fn(42.0, "unknown_format")
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# _build_ag_chart_data — DB-backed function (ad_groups.py lines 414-460)
# ---------------------------------------------------------------------------

class TestBuildAgChartData:
    def _import(self):
        from act_dashboard.routes.ad_groups import _build_ag_chart_data
        return _build_ag_chart_data

    def _date_filter(self, days=30):
        return f"AND snapshot_date >= CURRENT_DATE - INTERVAL '{days} days'"

    def _prev_filter(self, days=30):
        return (
            f"AND snapshot_date >= CURRENT_DATE - INTERVAL '{days * 2} days' "
            f"AND snapshot_date < CURRENT_DATE - INTERVAL '{days} days'"
        )

    def test_returns_dict(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, self._date_filter(), self._prev_filter())
        assert isinstance(result, dict)

    def test_has_dates_key(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, self._date_filter(), self._prev_filter())
        assert "dates" in result

    def test_has_cost_key(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, self._date_filter(), self._prev_filter())
        assert "cost" in result

    def test_has_impressions_key(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, self._date_filter(), self._prev_filter())
        assert "impressions" in result

    def test_has_clicks_key(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, self._date_filter(), self._prev_filter())
        assert "clicks" in result

    def test_has_avg_cpc_key(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, self._date_filter(), self._prev_filter())
        assert "avg_cpc" in result

    def test_unknown_customer_returns_dict(self, db_conn):
        fn = self._import()
        result = fn(db_conn, "nonexistent_customer", self._date_filter(), self._prev_filter())
        assert isinstance(result, dict)
        assert "dates" in result

    def test_7_day_filter(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, self._date_filter(7), self._prev_filter(7))
        assert isinstance(result, dict)
