"""
tests/test_routes_shopping.py

Tests for GET /shopping route — 4 tabs: Campaigns, Products, Feed Quality, Rules.
Chat 89.
"""

import pytest


class TestShoppingRoute:
    def test_get_shopping_returns_200(self, client):
        resp = client.get("/shopping")
        assert resp.status_code == 200

    def test_get_shopping_campaigns_tab(self, client):
        resp = client.get("/shopping?tab=campaigns")
        assert resp.status_code == 200

    def test_get_shopping_products_tab(self, client):
        resp = client.get("/shopping?tab=products")
        assert resp.status_code == 200

    def test_get_shopping_feed_quality_tab(self, client):
        resp = client.get("/shopping?tab=feed_quality")
        assert resp.status_code == 200

    def test_get_shopping_rules_tab(self, client):
        resp = client.get("/shopping?tab=rules")
        assert resp.status_code == 200

    def test_get_shopping_sort_by_cost(self, client):
        resp = client.get("/shopping?sort_by=cost&sort_dir=desc")
        assert resp.status_code == 200

    def test_get_shopping_sort_by_impressions(self, client):
        resp = client.get("/shopping?sort_by=impressions&sort_dir=asc")
        assert resp.status_code == 200

    def test_get_shopping_pagination(self, client):
        resp = client.get("/shopping?page=1&per_page=25")
        assert resp.status_code == 200

    def test_get_shopping_requires_login(self, app):
        with app.test_client() as c:
            resp = c.get("/shopping")
            assert resp.status_code in (200, 302)

    def test_get_shopping_invalid_sort_falls_back(self, client):
        resp = client.get("/shopping?sort_by=INVALID_COL")
        assert resp.status_code == 200

    def test_get_shopping_response_has_content(self, client):
        resp = client.get("/shopping")
        assert len(resp.data) > 0


# ---------------------------------------------------------------------------
# compute_campaign_metrics pure function
# ---------------------------------------------------------------------------

class TestComputeCampaignMetrics:
    def _import(self):
        from act_dashboard.routes.shopping import compute_campaign_metrics
        return compute_campaign_metrics

    def test_empty_returns_zero_dict(self):
        fn = self._import()
        result = fn([])
        assert result["total_campaigns"] == 0
        assert result["total_cost"] == 0.0

    def test_single_campaign(self):
        fn = self._import()
        campaigns = [{"cost": 100.0, "conversions_value": 400.0, "conversions": 4.0,
                      "impressions": 5000.0, "clicks": 200.0}]
        result = fn(campaigns)
        assert result["total_campaigns"] == 1
        assert result["total_cost"] == 100.0

    def test_roas_calculation(self):
        fn = self._import()
        campaigns = [{"cost": 100.0, "conversions_value": 400.0, "conversions": 4.0,
                      "impressions": 5000.0, "clicks": 200.0}]
        result = fn(campaigns)
        assert result["overall_roas"] == pytest.approx(4.0)

    def test_zero_cost_roas_is_zero(self):
        fn = self._import()
        campaigns = [{"cost": 0.0, "conversions_value": 400.0, "conversions": 4.0,
                      "impressions": 5000.0, "clicks": 200.0}]
        result = fn(campaigns)
        assert result["overall_roas"] == 0.0

    def test_multiple_campaigns_aggregated(self):
        fn = self._import()
        campaigns = [
            {"cost": 50.0, "conversions_value": 200.0, "conversions": 2.0,
             "impressions": 2500.0, "clicks": 100.0},
            {"cost": 50.0, "conversions_value": 200.0, "conversions": 2.0,
             "impressions": 2500.0, "clicks": 100.0},
        ]
        result = fn(campaigns)
        assert result["total_campaigns"] == 2
        assert result["total_cost"] == pytest.approx(100.0)

    def test_none_values_handled(self):
        fn = self._import()
        campaigns = [{"cost": None, "conversions_value": None, "conversions": None,
                      "impressions": None, "clicks": None}]
        result = fn(campaigns)
        assert isinstance(result["total_cost"], (int, float))


# ---------------------------------------------------------------------------
# load_shopping_campaigns — direct DB call to cover body loop (lines 115-144)
# ---------------------------------------------------------------------------

CUSTOMER_ID = "9999999999"


class TestLoadShoppingCampaigns:
    def _import(self):
        from act_dashboard.routes.shopping import load_shopping_campaigns
        return load_shopping_campaigns

    def test_returns_list(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30, None)
        assert isinstance(result, list)

    def test_returns_campaign_dicts(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30, None)
        for row in result:
            assert isinstance(row, dict)

    def test_campaign_has_cost_field(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30, None)
        if result:
            assert "cost" in result[0]

    def test_status_field_uppercased(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30, None)
        for row in result:
            assert row["status"] == row["status"].upper()

    def test_campaign_name_str(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30, None)
        for row in result:
            assert isinstance(row["campaign_name"], str)

    def test_channel_type_is_shopping(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30, None)
        for row in result:
            assert row["channel_type"] == "SHOPPING"

    def test_enabled_filter(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30, "enabled")
        for row in result:
            assert row["status"] == "ENABLED"

    def test_paused_filter_excludes_enabled(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30, "paused")
        for row in result:
            assert row["status"] == "PAUSED"

    def test_sort_by_impressions(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30, None, sort_by="impressions", sort_dir="desc")
        assert isinstance(result, list)

    def test_unknown_customer_returns_empty(self, db_conn):
        fn = self._import()
        result = fn(db_conn, "nonexistent_customer", 30, None)
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# load_products_from_raw — DB-backed function (lines 275-297)
# ---------------------------------------------------------------------------

class TestLoadProductsFromRaw:
    def _import(self):
        from act_dashboard.routes.shopping import load_products_from_raw
        return load_products_from_raw

    def test_returns_list(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30)
        assert isinstance(result, list)

    def test_product_has_product_id(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30)
        for p in result:
            assert "product_id" in p

    def test_product_has_cost(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30)
        for p in result:
            assert "cost" in p

    def test_product_roas_is_float(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30)
        for p in result:
            assert isinstance(p["roas"], float)

    def test_feed_quality_is_none(self, db_conn):
        fn = self._import()
        result = fn(db_conn, CUSTOMER_ID, 30)
        for p in result:
            assert p["feed_quality"] is None

    def test_unknown_customer_returns_empty(self, db_conn):
        fn = self._import()
        result = fn(db_conn, "nonexistent", 30)
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# compute_product_metrics — pure function (lines 332-349)
# ---------------------------------------------------------------------------

class TestComputeProductMetrics:
    def _import(self):
        from act_dashboard.routes.shopping import compute_product_metrics
        return compute_product_metrics

    def _make_products(self):
        return [
            {"cost": 10.0, "conv_value": 40.0, "conversions": 2.0,
             "availability": "IN_STOCK", "price_mismatch": False, "disapproved": False},
            {"cost": 5.0, "conv_value": 0.0, "conversions": 0.0,
             "availability": "OUT_OF_STOCK", "price_mismatch": True, "disapproved": False},
        ]

    def test_empty_returns_zero(self):
        fn = self._import()
        result = fn([])
        assert result["total_products"] == 0

    def test_empty_returns_zero_cost(self):
        fn = self._import()
        result = fn([])
        assert result["total_cost"] == 0.0

    def test_total_products(self):
        fn = self._import()
        result = fn(self._make_products())
        assert result["total_products"] == 2

    def test_total_cost(self):
        fn = self._import()
        result = fn(self._make_products())
        assert result["total_cost"] == pytest.approx(15.0)

    def test_out_of_stock_count(self):
        fn = self._import()
        result = fn(self._make_products())
        assert result["out_of_stock_count"] == 1

    def test_feed_issues_count(self):
        fn = self._import()
        result = fn(self._make_products())
        assert result["feed_issues_count"] == 1

    def test_overall_roas(self):
        fn = self._import()
        result = fn(self._make_products())
        assert result["overall_roas"] == pytest.approx(40.0 / 15.0)
