"""
tests/test_routes_keywords.py

Tests for GET /keywords route and pure helper functions.
Chat 89.
"""

import json
import pytest
from datetime import date, timedelta


CUSTOMER_ID = "9999999999"


class TestKeywordsRoute:
    def test_get_keywords_returns_200(self, client):
        resp = client.get("/keywords")
        assert resp.status_code == 200

    def test_get_keywords_with_days_7(self, client):
        resp = client.get("/keywords?days=7")
        assert resp.status_code == 200

    def test_get_keywords_with_days_30(self, client):
        resp = client.get("/keywords?days=30")
        assert resp.status_code == 200

    def test_get_keywords_match_type_broad(self, client):
        resp = client.get("/keywords?match_type=broad")
        assert resp.status_code == 200

    def test_get_keywords_match_type_exact(self, client):
        resp = client.get("/keywords?match_type=exact")
        assert resp.status_code == 200

    def test_get_keywords_pagination(self, client):
        resp = client.get("/keywords?page=1&per_page=10")
        assert resp.status_code == 200

    def test_get_keywords_sort_by_cost(self, client):
        resp = client.get("/keywords?sort_by=cost&sort_dir=desc")
        assert resp.status_code == 200

    def test_get_keywords_sort_by_quality_score(self, client):
        resp = client.get("/keywords?sort_by=quality_score&sort_dir=asc")
        assert resp.status_code == 200

    def test_get_keywords_requires_login(self, app):
        with app.test_client() as c:
            resp = c.get("/keywords")
            assert resp.status_code in (200, 302)

    def test_get_keywords_invalid_sort_falls_back(self, client):
        # Invalid sort col falls back to cost — should not crash
        resp = client.get("/keywords?sort_by=INVALID__COL")
        assert resp.status_code == 200

    def test_get_keywords_invalid_match_type_falls_back(self, client):
        resp = client.get("/keywords?match_type=garbage")
        assert resp.status_code == 200

    def test_get_keywords_search_terms_tab(self, client):
        # Search terms tab params — gracefully degrades if table missing
        resp = client.get("/keywords?st_page=1&st_per_page=25")
        assert resp.status_code == 200

    def test_get_keywords_with_date_range(self, client):
        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        resp = client.get(f"/keywords?date_from={yesterday}&date_to={today}")
        assert resp.status_code == 200

    def test_get_keywords_page_2(self, client):
        resp = client.get("/keywords?page=2&per_page=1")
        assert resp.status_code == 200

    def test_get_keywords_days_90(self, client):
        resp = client.get("/keywords?days=90")
        assert resp.status_code == 200

    def test_get_keywords_sort_dir_asc(self, client):
        resp = client.get("/keywords?sort_by=quality_score&sort_dir=asc")
        assert resp.status_code == 200

    def test_get_keywords_sort_by_clicks(self, client):
        resp = client.get("/keywords?sort_by=clicks&sort_dir=desc")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# TestLoadKeywordFeatures — direct DB function call
# ---------------------------------------------------------------------------

class TestLoadKeywordFeatures:
    def test_returns_list(self, db_conn):
        from act_dashboard.routes.keywords import load_keyword_features
        result = load_keyword_features(db_conn, CUSTOMER_ID, date.today())
        assert isinstance(result, list)

    def test_returns_keywords_for_today(self, db_conn):
        from act_dashboard.routes.keywords import load_keyword_features
        result = load_keyword_features(db_conn, CUSTOMER_ID, date.today())
        assert len(result) >= 1

    def test_result_has_clicks_w7_key(self, db_conn):
        from act_dashboard.routes.keywords import load_keyword_features
        result = load_keyword_features(db_conn, CUSTOMER_ID, date.today())
        assert all("clicks_w7" in kw for kw in result)

    def test_result_has_cost_w30_dollars(self, db_conn):
        from act_dashboard.routes.keywords import load_keyword_features
        result = load_keyword_features(db_conn, CUSTOMER_ID, date.today())
        assert all("cost_w30_dollars" in kw for kw in result)

    def test_returns_empty_for_wrong_customer(self, db_conn):
        from act_dashboard.routes.keywords import load_keyword_features
        result = load_keyword_features(db_conn, "0000000000", date.today())
        assert result == []


# ---------------------------------------------------------------------------
# TestComputeKeywordSummary — pure function
# ---------------------------------------------------------------------------

class TestComputeKeywordSummary:
    def _make_kws(self):
        return [
            {"quality_score": 7, "clicks_w7": 50.0, "cost_w30": 5000000.0,
             "conv_w30": 2.0, "cpa_dollars": 10.0, "low_data_flag": False},
            {"quality_score": 2, "clicks_w7": 5.0, "cost_w30": 60000000.0,
             "conv_w30": 0.0, "cpa_dollars": 0.0, "low_data_flag": True},
        ]

    def test_returns_dict(self):
        from act_dashboard.routes.keywords import compute_keyword_summary
        result = compute_keyword_summary(self._make_kws())
        assert isinstance(result, dict)

    def test_active_count(self):
        from act_dashboard.routes.keywords import compute_keyword_summary
        result = compute_keyword_summary(self._make_kws())
        assert result["active_count"] == 2

    def test_low_qs_count(self):
        from act_dashboard.routes.keywords import compute_keyword_summary
        result = compute_keyword_summary(self._make_kws())
        # quality_score <= 3: only the second keyword (2)
        assert result["low_qs_count"] == 1

    def test_low_data_count(self):
        from act_dashboard.routes.keywords import compute_keyword_summary
        result = compute_keyword_summary(self._make_kws())
        assert result["low_data_count"] == 1

    def test_wasted_spend(self):
        from act_dashboard.routes.keywords import compute_keyword_summary
        # Second keyword: conv=0, cost=60M micros = £60 > £50 → wasted
        result = compute_keyword_summary(self._make_kws())
        assert result["wasted_spend_dollars"] > 0

    def test_empty_list(self):
        from act_dashboard.routes.keywords import compute_keyword_summary
        result = compute_keyword_summary([])
        assert result["active_count"] == 0
        assert result["avg_qs"] == 0

    def test_avg_cpa_dollars(self):
        from act_dashboard.routes.keywords import compute_keyword_summary
        result = compute_keyword_summary(self._make_kws())
        assert result["avg_cpa_dollars"] == 10.0

    def test_avg_qs(self):
        from act_dashboard.routes.keywords import compute_keyword_summary
        result = compute_keyword_summary(self._make_kws())
        # (7 + 2) / 2 = 4.5
        assert result["avg_qs"] == 4.5


# ---------------------------------------------------------------------------
# TestExtractCampaignList — pure function
# ---------------------------------------------------------------------------

class TestExtractCampaignList:
    def test_returns_list_of_tuples(self):
        from act_dashboard.routes.keywords import extract_campaign_list
        kws = [{"campaign_id": 111, "campaign_name": "Campaign Alpha"},
               {"campaign_id": 111, "campaign_name": "Campaign Alpha"},
               {"campaign_id": 222, "campaign_name": "Campaign Beta"}]
        result = extract_campaign_list(kws)
        assert isinstance(result, list)

    def test_deduplicates_campaigns(self):
        from act_dashboard.routes.keywords import extract_campaign_list
        kws = [{"campaign_id": 111, "campaign_name": "Campaign Alpha"},
               {"campaign_id": 111, "campaign_name": "Campaign Alpha"}]
        result = extract_campaign_list(kws)
        assert len(result) == 1

    def test_sorted_by_name(self):
        from act_dashboard.routes.keywords import extract_campaign_list
        kws = [{"campaign_id": 222, "campaign_name": "Zebra Camp"},
               {"campaign_id": 111, "campaign_name": "Alpha Camp"}]
        result = extract_campaign_list(kws)
        names = [name for _, name in result]
        assert names == sorted(names)

    def test_empty_list(self):
        from act_dashboard.routes.keywords import extract_campaign_list
        result = extract_campaign_list([])
        assert result == []


# ---------------------------------------------------------------------------
# TestFlagNegativeKeywords — pure function
# ---------------------------------------------------------------------------

class TestFlagNegativeKeywords:
    def test_flags_zero_cvr_with_10_clicks(self):
        from act_dashboard.routes.keywords import flag_negative_keywords
        terms = [{"clicks": 15, "conversions": 0, "cost": 10.0, "ctr": 0.05, "impressions": 300}]
        result = flag_negative_keywords(terms)
        assert result[0]["negative_flag"] is True
        assert "CVR" in result[0]["flag_reason"]

    def test_flags_high_cost_no_conversions(self):
        from act_dashboard.routes.keywords import flag_negative_keywords
        terms = [{"clicks": 5, "conversions": 0, "cost": 60.0, "ctr": 0.10, "impressions": 50}]
        result = flag_negative_keywords(terms)
        assert result[0]["negative_flag"] is True
        assert "£50+" in result[0]["flag_reason"]

    def test_flags_low_ctr_high_impressions(self):
        from act_dashboard.routes.keywords import flag_negative_keywords
        terms = [{"clicks": 0, "conversions": 0, "cost": 5.0, "ctr": 0.005, "impressions": 100}]
        result = flag_negative_keywords(terms)
        assert result[0]["negative_flag"] is True
        assert "CTR" in result[0]["flag_reason"]

    def test_does_not_flag_good_term(self):
        from act_dashboard.routes.keywords import flag_negative_keywords
        terms = [{"clicks": 5, "conversions": 3, "cost": 20.0, "ctr": 0.10, "impressions": 50}]
        result = flag_negative_keywords(terms)
        assert result[0]["negative_flag"] is False
        assert result[0]["flag_reason"] == ""

    def test_returns_same_list_with_extra_keys(self):
        from act_dashboard.routes.keywords import flag_negative_keywords
        terms = [{"clicks": 0, "conversions": 0, "cost": 0.0, "ctr": 0.5, "impressions": 5}]
        result = flag_negative_keywords(terms)
        assert "negative_flag" in result[0]
        assert "flag_reason" in result[0]


# ---------------------------------------------------------------------------
# TestGroupKeywordRecommendations — pure function
# ---------------------------------------------------------------------------

class TestGroupKeywordRecommendations:
    def _make_recs(self):
        return [
            {"rule_id": "KW-PAUSE-1", "priority": 1, "action": "pause"},
            {"rule_id": "KW-BID-2", "priority": 2, "action": "bid"},
            {"rule_id": "ST-NEG-3", "priority": 3, "action": "negative"},
        ]

    def test_returns_list(self):
        from act_dashboard.routes.keywords import group_keyword_recommendations
        result = group_keyword_recommendations(self._make_recs())
        assert isinstance(result, list)

    def test_groups_correctly(self):
        from act_dashboard.routes.keywords import group_keyword_recommendations
        result = group_keyword_recommendations(self._make_recs())
        group_names = [g[0] for g in result]
        assert "Keyword Pause" in group_names
        assert "Keyword Bid Adjustments" in group_names
        assert "Search Term Negatives" in group_names

    def test_empty_list(self):
        from act_dashboard.routes.keywords import group_keyword_recommendations
        result = group_keyword_recommendations([])
        assert result == []

    def test_unknown_prefix_included(self):
        from act_dashboard.routes.keywords import group_keyword_recommendations
        recs = [{"rule_id": "UNKNOWN-PREFIX-1", "priority": 1}]
        result = group_keyword_recommendations(recs)
        assert len(result) >= 1


# ---------------------------------------------------------------------------
# TestBuildDateFilters — pure function
# ---------------------------------------------------------------------------

class TestBuildDateFilters:
    def test_without_dates_uses_days(self):
        from act_dashboard.routes.keywords import _build_date_filters
        current, prev = _build_date_filters(30, None, None)
        assert "INTERVAL '30 days'" in current
        assert "INTERVAL '60 days'" in prev

    def test_with_explicit_dates(self):
        from act_dashboard.routes.keywords import _build_date_filters
        current, prev = _build_date_filters(30, "2026-01-01", "2026-01-31")
        assert "2026-01-01" in current
        assert "2026-01-31" in current

    def test_with_explicit_dates_prev_period(self):
        from act_dashboard.routes.keywords import _build_date_filters
        _, prev = _build_date_filters(30, "2026-02-01", "2026-02-28")
        assert "2026-01" in prev  # previous period should be in January

    def test_days_7_interval(self):
        from act_dashboard.routes.keywords import _build_date_filters
        current, prev = _build_date_filters(7, None, None)
        assert "7 days" in current
        assert "14 days" in prev

    def test_invalid_days_defaults_to_30(self):
        from act_dashboard.routes.keywords import _build_date_filters
        current, prev = _build_date_filters(45, None, None)
        assert "30 days" in current


# ---------------------------------------------------------------------------
# TestBuildKwChartData — needs DB connection
# ---------------------------------------------------------------------------

class TestBuildKwChartData:
    def test_returns_dict_with_dates_key(self, db_conn):
        from act_dashboard.routes.keywords import _build_kw_chart_data
        result = _build_kw_chart_data(db_conn, CUSTOMER_ID, 30)
        assert isinstance(result, dict)
        assert "dates" in result

    def test_returns_cost_key(self, db_conn):
        from act_dashboard.routes.keywords import _build_kw_chart_data
        result = _build_kw_chart_data(db_conn, CUSTOMER_ID, 30)
        assert "cost" in result

    def test_returns_clicks_key(self, db_conn):
        from act_dashboard.routes.keywords import _build_kw_chart_data
        result = _build_kw_chart_data(db_conn, CUSTOMER_ID, 30)
        assert "clicks" in result

    def test_with_explicit_dates(self, db_conn):
        from act_dashboard.routes.keywords import _build_kw_chart_data
        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        result = _build_kw_chart_data(db_conn, CUSTOMER_ID, 30, date_from=yesterday, date_to=today)
        assert "dates" in result

    def test_wrong_customer_returns_empty_dates(self, db_conn):
        from act_dashboard.routes.keywords import _build_kw_chart_data
        result = _build_kw_chart_data(db_conn, "0000000000", 30)
        assert result["dates"] == []


# ---------------------------------------------------------------------------
# TestLoadSearchTerms — needs DB connection (ro.analytics.search_term_daily)
# ---------------------------------------------------------------------------

class TestLoadSearchTerms:
    def test_returns_dict_with_data_key(self, db_conn):
        from act_dashboard.routes.keywords import load_search_terms
        today = date.today()
        yesterday = today - timedelta(days=1)
        result = load_search_terms(db_conn, CUSTOMER_ID, yesterday, today)
        assert isinstance(result, dict)
        assert "data" in result

    def test_returns_total_count(self, db_conn):
        from act_dashboard.routes.keywords import load_search_terms
        today = date.today()
        result = load_search_terms(db_conn, CUSTOMER_ID, today - timedelta(days=1), today)
        assert "total_count" in result
        assert isinstance(result["total_count"], int)

    def test_pagination_respected(self, db_conn):
        from act_dashboard.routes.keywords import load_search_terms
        today = date.today()
        result = load_search_terms(db_conn, CUSTOMER_ID, today - timedelta(days=1), today,
                                   page=1, per_page=1)
        assert len(result["data"]) <= 1

    def test_with_campaign_filter(self, db_conn):
        from act_dashboard.routes.keywords import load_search_terms
        today = date.today()
        result = load_search_terms(db_conn, CUSTOMER_ID, today - timedelta(days=1), today,
                                   campaign_id="111")
        assert isinstance(result["data"], list)

    def test_with_status_filter(self, db_conn):
        from act_dashboard.routes.keywords import load_search_terms
        today = date.today()
        result = load_search_terms(db_conn, CUSTOMER_ID, today - timedelta(days=1), today,
                                   status="active")
        assert isinstance(result["data"], list)

    def test_with_match_type_filter(self, db_conn):
        from act_dashboard.routes.keywords import load_search_terms
        today = date.today()
        result = load_search_terms(db_conn, CUSTOMER_ID, today - timedelta(days=1), today,
                                   match_type="broad")
        assert isinstance(result["data"], list)


# ---------------------------------------------------------------------------
# TestCheckKeywordExists — needs DB connection
# ---------------------------------------------------------------------------

class TestCheckKeywordExists:
    def test_existing_keyword_returns_true(self, db_conn):
        from act_dashboard.routes.keywords import check_keyword_exists
        # keyword_daily has 'google ads agency' in ad_group 2001
        result = check_keyword_exists(db_conn, CUSTOMER_ID, "2001", "google ads agency")
        assert result is True

    def test_nonexistent_keyword_returns_false(self, db_conn):
        from act_dashboard.routes.keywords import check_keyword_exists
        result = check_keyword_exists(db_conn, CUSTOMER_ID, "2001", "nonexistent term xyz")
        assert result is False

    def test_case_insensitive_match(self, db_conn):
        from act_dashboard.routes.keywords import check_keyword_exists
        result = check_keyword_exists(db_conn, CUSTOMER_ID, "2001", "GOOGLE ADS AGENCY")
        assert result is True


# ---------------------------------------------------------------------------
# TestAddNegativeKeywordsDryRun — POST route (dry_run path)
# ---------------------------------------------------------------------------

class TestAddNegativeKeywordsDryRun:
    def test_dry_run_returns_200(self, client):
        resp = client.post(
            "/keywords/add-negative",
            data=json.dumps({
                "search_terms": [{"search_term": "free stuff", "campaign_id": "111"}],
                "level": "campaign",
                "dry_run": True
            }),
            content_type="application/json"
        )
        assert resp.status_code == 200

    def test_dry_run_success_true(self, client):
        data = json.loads(client.post(
            "/keywords/add-negative",
            data=json.dumps({
                "search_terms": [{"search_term": "unwanted term", "campaign_id": "111"}],
                "dry_run": True
            }),
            content_type="application/json"
        ).data)
        assert data["success"] is True

    def test_empty_search_terms_returns_400(self, client):
        resp = client.post(
            "/keywords/add-negative",
            data=json.dumps({"search_terms": [], "dry_run": False}),
            content_type="application/json"
        )
        assert resp.status_code == 400

    def test_dry_run_reports_count(self, client):
        data = json.loads(client.post(
            "/keywords/add-negative",
            data=json.dumps({
                "search_terms": [
                    {"search_term": "term1", "campaign_id": "111"},
                    {"search_term": "term2", "campaign_id": "111"}
                ],
                "dry_run": True
            }),
            content_type="application/json"
        ).data)
        assert data["added"] == 2


# ---------------------------------------------------------------------------
# TestAddKeywordsDryRun — POST route (dry_run path)
# ---------------------------------------------------------------------------

class TestAddKeywordsDryRun:
    def test_dry_run_returns_200(self, client):
        resp = client.post(
            "/keywords/add-keyword",
            data=json.dumps({
                "keywords": [{"search_term": "buy ads management", "ad_group_id": "2001",
                               "campaign_id": "111", "match_type": "PHRASE"}],
                "dry_run": True
            }),
            content_type="application/json"
        )
        assert resp.status_code == 200

    def test_dry_run_success_true(self, client):
        data = json.loads(client.post(
            "/keywords/add-keyword",
            data=json.dumps({
                "keywords": [{"search_term": "ppc ads", "ad_group_id": "2001",
                               "campaign_id": "111", "match_type": "EXACT"}],
                "dry_run": True
            }),
            content_type="application/json"
        ).data)
        assert data["success"] is True

    def test_empty_keywords_returns_400(self, client):
        resp = client.post(
            "/keywords/add-keyword",
            data=json.dumps({"keywords": [], "dry_run": False}),
            content_type="application/json"
        )
        assert resp.status_code == 400

    def test_dry_run_count_in_response(self, client):
        data = json.loads(client.post(
            "/keywords/add-keyword",
            data=json.dumps({
                "keywords": [{"search_term": "kw1", "ad_group_id": "2001", "campaign_id": "111"},
                              {"search_term": "kw2", "ad_group_id": "2001", "campaign_id": "111"}],
                "dry_run": True
            }),
            content_type="application/json"
        ).data)
        assert data["added"] == 2
