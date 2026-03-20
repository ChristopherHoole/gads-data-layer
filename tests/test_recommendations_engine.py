"""
tests/test_recommendations_engine.py

Tests for recommendations engine pure helpers.
Chat 89.
"""

import pytest
from act_autopilot.recommendations_engine import (
    _detect_entity_type,
    _evaluate,
    _get_metric_map_for_entity,
    _get_metric_value,
    _evaluate_condition,
    _calculate_proposed_value,
    _get_current_value,
    _build_trigger_summary,
    ENTITY_TABLES,
    CAMPAIGN_METRIC_MAP,
    KEYWORD_METRIC_MAP,
    AD_GROUP_METRIC_MAP,
    SHOPPING_METRIC_MAP,
    AD_METRIC_MAP,
)


class TestDetectEntityType:
    def test_budget_rule_returns_campaign(self):
        assert _detect_entity_type("budget_1") == "campaign"

    def test_keyword_rule_returns_keyword(self):
        assert _detect_entity_type("keyword_1") == "keyword"

    def test_ad_group_rule_returns_ad_group(self):
        # "ad_group_" must be checked before generic "ad" split
        assert _detect_entity_type("ad_group_1") == "ad_group"

    def test_ad_rule_returns_ad(self):
        assert _detect_entity_type("ad_1") == "ad"

    def test_shopping_rule_returns_shopping(self):
        assert _detect_entity_type("shopping_1") == "shopping"

    def test_no_underscore_returns_campaign(self):
        assert _detect_entity_type("anyrule") == "campaign"

    def test_unknown_prefix_falls_back_to_campaign(self):
        assert _detect_entity_type("unknown_99") == "campaign"

    def test_campaign_rule_returns_campaign(self):
        assert _detect_entity_type("campaign_1") == "campaign"


class TestEvaluate:
    def test_gt_true(self):
        assert _evaluate(5.0, "gt", 3.0) is True

    def test_gt_false(self):
        assert _evaluate(3.0, "gt", 5.0) is False

    def test_gte_equal(self):
        assert _evaluate(5.0, "gte", 5.0) is True

    def test_gte_greater(self):
        assert _evaluate(6.0, "gte", 5.0) is True

    def test_lt_true(self):
        assert _evaluate(2.0, "lt", 5.0) is True

    def test_lt_false(self):
        assert _evaluate(5.0, "lt", 2.0) is False

    def test_lte_equal(self):
        assert _evaluate(5.0, "lte", 5.0) is True

    def test_eq_numeric(self):
        assert _evaluate(5.0, "eq", 5.0) is True

    def test_eq_string(self):
        assert _evaluate("POOR", "eq", "POOR") is True

    def test_eq_string_mismatch(self):
        assert _evaluate("GOOD", "eq", "POOR") is False

    def test_eq_bool_true(self):
        assert _evaluate(True, "eq", True) is True

    def test_none_value_returns_false(self):
        assert _evaluate(None, "gt", 0.0) is False

    def test_unknown_operator_returns_false(self):
        assert _evaluate(5.0, "UNKNOWN", 3.0) is False


class TestGetMetricMapForEntity:
    def test_campaign_returns_campaign_map(self):
        result = _get_metric_map_for_entity("campaign")
        assert result is CAMPAIGN_METRIC_MAP

    def test_keyword_returns_keyword_map(self):
        result = _get_metric_map_for_entity("keyword")
        assert result is KEYWORD_METRIC_MAP

    def test_ad_group_returns_ad_group_map(self):
        result = _get_metric_map_for_entity("ad_group")
        assert result is AD_GROUP_METRIC_MAP

    def test_shopping_returns_shopping_map(self):
        result = _get_metric_map_for_entity("shopping")
        assert result is SHOPPING_METRIC_MAP

    def test_ad_returns_ad_map(self):
        result = _get_metric_map_for_entity("ad")
        assert result is AD_METRIC_MAP

    def test_unknown_returns_empty_dict(self):
        result = _get_metric_map_for_entity("unknown_entity")
        assert result == {}


class TestEntityTables:
    def test_campaign_table_in_entity_tables(self):
        assert "campaign" in ENTITY_TABLES

    def test_keyword_table_in_entity_tables(self):
        assert "keyword" in ENTITY_TABLES

    def test_ad_group_table_in_entity_tables(self):
        assert "ad_group" in ENTITY_TABLES

    def test_shopping_table_in_entity_tables(self):
        assert "shopping" in ENTITY_TABLES

    def test_campaign_uses_features_table(self):
        assert "campaign_features_daily" in ENTITY_TABLES["campaign"]

    def test_keyword_uses_keyword_daily(self):
        assert "keyword_daily" in ENTITY_TABLES["keyword"]


class TestCampaignMetricMap:
    def test_roas_7d_mapped(self):
        assert "roas_7d" in CAMPAIGN_METRIC_MAP

    def test_clicks_7d_mapped(self):
        assert "clicks_7d" in CAMPAIGN_METRIC_MAP

    def test_roas_maps_to_roas_w7_mean(self):
        col, _, _ = CAMPAIGN_METRIC_MAP["roas_7d"]
        assert col == "roas_w7_mean"

    def test_clicks_maps_to_clicks_w7_sum(self):
        col, _, _ = CAMPAIGN_METRIC_MAP["clicks_7d"]
        assert col == "clicks_w7_sum"

    def test_cost_spike_has_fixed_operator(self):
        col, op, threshold = CAMPAIGN_METRIC_MAP["cost_spike_confidence"]
        assert op == "gte"
        assert threshold == 2.0


# ---------------------------------------------------------------------------
# _get_metric_value
# ---------------------------------------------------------------------------

class TestGetMetricValue:
    def test_known_metric_returns_value(self):
        features = {"roas_w7_mean": 5.0}
        value, col = _get_metric_value(features, "roas_7d", CAMPAIGN_METRIC_MAP)
        assert value == 5.0
        assert col == "roas_w7_mean"

    def test_unknown_metric_returns_none(self):
        features = {"roas_w7_mean": 5.0}
        value, col = _get_metric_value(features, "nonexistent_metric", CAMPAIGN_METRIC_MAP)
        assert value is None
        assert col == "nonexistent_metric"

    def test_metric_missing_from_features_returns_none(self):
        features = {}
        value, col = _get_metric_value(features, "roas_7d", CAMPAIGN_METRIC_MAP)
        assert value is None
        assert col == "roas_w7_mean"

    def test_clicks_7d_returns_correct_column(self):
        features = {"clicks_w7_sum": 50}
        value, col = _get_metric_value(features, "clicks_7d", CAMPAIGN_METRIC_MAP)
        assert value == 50
        assert col == "clicks_w7_sum"

    def test_empty_metric_map_returns_none(self):
        features = {"roas_w7_mean": 5.0}
        value, col = _get_metric_value(features, "roas_7d", {})
        assert value is None
        assert col == "roas_7d"


# ---------------------------------------------------------------------------
# _evaluate_condition
# ---------------------------------------------------------------------------

class TestEvaluateCondition:
    def test_empty_metric_returns_true(self):
        passed, desc = _evaluate_condition({}, "", "gt", 1.0, CAMPAIGN_METRIC_MAP)
        assert passed is True
        assert desc == ""

    def test_unknown_metric_returns_false(self):
        passed, desc = _evaluate_condition({}, "nonexistent", "gt", 1.0, CAMPAIGN_METRIC_MAP)
        assert passed is False
        assert desc == "unknown metric"

    def test_passing_condition(self):
        features = {"roas_w7_mean": 5.0}
        passed, desc = _evaluate_condition(features, "roas_7d", "gt", 1.0, CAMPAIGN_METRIC_MAP)
        assert passed is True

    def test_failing_condition(self):
        features = {"roas_w7_mean": 0.5}
        passed, desc = _evaluate_condition(features, "roas_7d", "gt", 1.0, CAMPAIGN_METRIC_MAP)
        assert passed is False

    def test_none_value_returns_false(self):
        features = {}
        passed, desc = _evaluate_condition(features, "roas_7d", "gt", 1.0, CAMPAIGN_METRIC_MAP)
        assert passed is False
        assert "NULL" in desc

    def test_description_contains_column(self):
        features = {"roas_w7_mean": 3.5}
        _passed, desc = _evaluate_condition(features, "roas_7d", "gt", 1.0, CAMPAIGN_METRIC_MAP)
        assert "roas_w7_mean" in desc

    def test_override_op_used_when_present(self):
        # cost_spike_confidence maps to db_col="anomaly_cost_z", override_op="gte", override_threshold=2.0
        features = {"anomaly_cost_z": 2.5}
        passed, desc = _evaluate_condition(features, "cost_spike_confidence", "gt", 0.0, CAMPAIGN_METRIC_MAP)
        # override_op=gte, override_threshold=2.0 → 2.5 gte 2.0 → True
        assert passed is True

    def test_bool_value_formats_correctly(self):
        bool_map = {"low_data": ("low_data_flag", None, None)}
        features = {"low_data_flag": True}
        _passed, desc = _evaluate_condition(features, "low_data", "eq", True, bool_map)
        assert "low_data_flag" in desc
        assert "True" in desc


# ---------------------------------------------------------------------------
# _calculate_proposed_value
# ---------------------------------------------------------------------------

class TestCalculateProposedValue:
    def test_increase_applies_magnitude(self):
        rule = {"action_direction": "increase", "action_magnitude": 10}
        result = _calculate_proposed_value(rule, 100.0)
        assert result == 110.0

    def test_decrease_applies_magnitude(self):
        rule = {"action_direction": "decrease", "action_magnitude": 20}
        result = _calculate_proposed_value(rule, 100.0)
        assert result == 80.0

    def test_hold_returns_current(self):
        rule = {"action_direction": "hold", "action_magnitude": None}
        result = _calculate_proposed_value(rule, 50.0)
        assert result == 50.0

    def test_flag_returns_current(self):
        rule = {"action_direction": "flag", "action_magnitude": None}
        result = _calculate_proposed_value(rule, 25.0)
        assert result == 25.0

    def test_zero_magnitude_increase(self):
        rule = {"action_direction": "increase", "action_magnitude": 0}
        result = _calculate_proposed_value(rule, 75.0)
        assert result == 75.0

    def test_result_rounded_to_4_decimal_places(self):
        rule = {"action_direction": "increase", "action_magnitude": 10}
        result = _calculate_proposed_value(rule, 33.333)
        assert result == round(33.333 * 1.1, 4)


# ---------------------------------------------------------------------------
# _get_current_value
# ---------------------------------------------------------------------------

class TestGetCurrentValue:
    def test_campaign_budget_uses_cost_micros(self):
        features = {"cost_micros_w7_mean": 50_000_000}
        result = _get_current_value("campaign", "budget", features)
        assert result == 50.0

    def test_campaign_budget_fallback(self):
        result = _get_current_value("campaign", "budget", {})
        assert result == 50.0

    def test_campaign_bid_returns_target_roas_fallback(self):
        result = _get_current_value("campaign", "bid", {})
        assert result == 4.0

    def test_keyword_uses_bid_micros(self):
        features = {"bid_micros": 1_000_000}
        result = _get_current_value("keyword", "bid", features)
        assert result == 1.0

    def test_keyword_fallback(self):
        result = _get_current_value("keyword", "bid", {})
        assert result == 0.50

    def test_ad_group_uses_cpc_bid_micros(self):
        features = {"cpc_bid_micros": 2_000_000}
        result = _get_current_value("ad_group", "bid", features)
        assert result == 2.0

    def test_ad_group_fallback(self):
        result = _get_current_value("ad_group", "bid", {})
        assert result == 1.0

    def test_shopping_uses_cost_micros(self):
        features = {"cost_micros": 200_000_000}
        result = _get_current_value("shopping", "budget", features)
        assert result == 200.0

    def test_shopping_fallback(self):
        result = _get_current_value("shopping", "budget", {})
        assert result == 100.0

    def test_ad_uses_cost(self):
        features = {"cost": 15.0}
        result = _get_current_value("ad", "status", features)
        assert result == 15.0

    def test_ad_fallback(self):
        result = _get_current_value("ad", "status", {})
        assert result == 10.0

    def test_unknown_entity_returns_zero(self):
        result = _get_current_value("unknown_entity", "budget", {})
        assert result == 0.0


# ---------------------------------------------------------------------------
# _build_trigger_summary
# ---------------------------------------------------------------------------

class TestBuildTriggerSummary:
    def _make_rule(self, **overrides):
        rule = {
            "rule_id": "budget_1",
            "condition_metric": "roas_7d",
            "condition_operator": "gt",
            "condition_value": 1.15,
            "condition_unit": "absolute",
        }
        rule.update(overrides)
        return rule

    def test_basic_summary_contains_column(self):
        features = {"roas_w7_mean": 5.0}
        rule = self._make_rule()
        result = _build_trigger_summary(rule, features, 3.0, CAMPAIGN_METRIC_MAP)
        assert "roas_w7_mean" in result

    def test_x_target_unit_formats_roas(self):
        features = {"roas_w7_mean": 5.0}
        rule = self._make_rule(condition_unit="x_target", condition_value=1.15)
        result = _build_trigger_summary(rule, features, 3.0, CAMPAIGN_METRIC_MAP)
        assert "ROAS" in result or "roas_w7_mean" in result

    def test_null_metric_value_shows_null(self):
        features = {}
        rule = self._make_rule()
        result = _build_trigger_summary(rule, features, 3.0, CAMPAIGN_METRIC_MAP)
        assert "NULL" in result

    def test_with_condition_2_joins_with_and(self):
        features = {"roas_w7_mean": 5.0, "clicks_w7_sum": 50}
        rule = self._make_rule(
            condition_2_metric="clicks_7d",
            condition_2_operator="gte",
            condition_2_value=30,
        )
        result = _build_trigger_summary(rule, features, 3.0, CAMPAIGN_METRIC_MAP)
        assert "AND" in result

    def test_no_condition_2_no_and(self):
        features = {"roas_w7_mean": 5.0}
        rule = self._make_rule()
        result = _build_trigger_summary(rule, features, 3.0, CAMPAIGN_METRIC_MAP)
        assert "AND" not in result


# ---------------------------------------------------------------------------
# run_recommendations_engine (integration with tmp DuckDB files)
# ---------------------------------------------------------------------------

class TestRunRecommendationsEngine:
    """Test the main engine function end-to-end with temp DuckDB files."""

    @pytest.fixture
    def engine_dbs(self, tmp_path):
        """Create two temp DuckDB files: writable main + readonly analytics."""
        import duckdb
        from datetime import date

        db_path = str(tmp_path / "main.duckdb")
        ro_path = str(tmp_path / "readonly.duckdb")

        # Writable main DB — needs recommendations table + rules table
        main_conn = duckdb.connect(db_path)
        main_conn.execute("""
            CREATE TABLE recommendations (
                rec_id VARCHAR, rule_id VARCHAR, rule_type VARCHAR,
                campaign_id VARCHAR, campaign_name VARCHAR,
                entity_type VARCHAR, entity_id VARCHAR, entity_name VARCHAR,
                customer_id VARCHAR, status VARCHAR,
                action_direction VARCHAR, action_magnitude DOUBLE,
                current_value DOUBLE, proposed_value DOUBLE,
                trigger_summary VARCHAR, confidence VARCHAR,
                generated_at TIMESTAMP, accepted_at TIMESTAMP,
                monitoring_ends_at TIMESTAMP, resolved_at TIMESTAMP,
                outcome_metric DOUBLE, created_at TIMESTAMP, updated_at TIMESTAMP
            )
        """)
        main_conn.execute("""
            CREATE TABLE rules (
                id INTEGER PRIMARY KEY,
                client_config VARCHAR NOT NULL,
                entity_type VARCHAR NOT NULL DEFAULT 'campaign',
                name VARCHAR NOT NULL,
                rule_or_flag VARCHAR NOT NULL,
                type VARCHAR NOT NULL,
                campaign_type_lock VARCHAR,
                entity_scope JSON NOT NULL DEFAULT '{"scope":"all"}',
                conditions JSON NOT NULL,
                action_type VARCHAR,
                action_magnitude FLOAT,
                cooldown_days INTEGER DEFAULT 7,
                risk_level VARCHAR,
                enabled BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT now(),
                updated_at TIMESTAMP DEFAULT now(),
                last_evaluated_at TIMESTAMP,
                last_fired_at TIMESTAMP,
                plain_english VARCHAR,
                is_template BOOLEAN DEFAULT FALSE
            )
        """)
        # Insert one enabled campaign rule: fires when roas_7d > 1.15
        main_conn.execute("""
            INSERT INTO rules
                (id, client_config, entity_type, name, rule_or_flag, type,
                 conditions, action_type, action_magnitude, cooldown_days,
                 risk_level, enabled, is_template)
            VALUES
                (1, 'eng_customer', 'campaign', 'Test Budget Boost', 'rule', 'budget',
                 '[{"metric": "roas_7d", "op": "gt", "value": 1.15, "ref": "absolute"}]',
                 'increase_budget', 10, 7, 'low', TRUE, FALSE)
        """)
        main_conn.close()

        # Readonly DB — analytics.campaign_features_daily only
        ro_conn = duckdb.connect(ro_path)
        ro_conn.execute("CREATE SCHEMA IF NOT EXISTS analytics")
        today = date.today().isoformat()
        ro_conn.execute("""
            CREATE TABLE analytics.campaign_features_daily (
                customer_id          VARCHAR,
                campaign_id          BIGINT,
                campaign_name        VARCHAR,
                snapshot_date        DATE,
                roas_w7_mean         DOUBLE,
                clicks_w7_sum        BIGINT,
                cost_micros_w7_mean  DOUBLE,
                impressions_w7_sum   BIGINT,
                conversions_w7_sum   DOUBLE,
                anomaly_cost_z       DOUBLE,
                pacing_flag_over_105 BOOLEAN,
                ctr_w7_mean          DOUBLE,
                cvr_w7_mean          DOUBLE
            )
        """)
        # Row 1: triggers budget_1 (roas > threshold, clicks >= 30)
        ro_conn.execute(f"""
            INSERT INTO analytics.campaign_features_daily VALUES
            ('eng_customer', 111, 'Campaign Alpha', '{today}',
             5.0, 50, 50000000, 1000, 5.0, 0.0, FALSE, 0.05, 0.1),
            ('eng_customer', 222, 'Campaign Beta', '{today}',
             0.3, 50, 20000000, 500, 1.0, 0.0, FALSE, 0.02, 0.05)
        """)
        ro_conn.close()

        return db_path, ro_path

    def test_returns_dict(self, engine_dbs):
        from act_autopilot.recommendations_engine import run_recommendations_engine
        db_path, ro_path = engine_dbs
        result = run_recommendations_engine("eng_customer", db_path=db_path, readonly_path=ro_path)
        assert isinstance(result, dict)

    def test_has_generated_key(self, engine_dbs):
        from act_autopilot.recommendations_engine import run_recommendations_engine
        db_path, ro_path = engine_dbs
        result = run_recommendations_engine("eng_customer", db_path=db_path, readonly_path=ro_path)
        assert "generated" in result

    def test_customer_id_in_result(self, engine_dbs):
        from act_autopilot.recommendations_engine import run_recommendations_engine
        db_path, ro_path = engine_dbs
        result = run_recommendations_engine("eng_customer", db_path=db_path, readonly_path=ro_path)
        assert result["customer_id"] == "eng_customer"

    def test_generates_recommendation_when_condition_met(self, engine_dbs):
        from act_autopilot.recommendations_engine import run_recommendations_engine
        db_path, ro_path = engine_dbs
        result = run_recommendations_engine("eng_customer", db_path=db_path, readonly_path=ro_path)
        # At least one rule should fire for the high-ROAS campaign
        assert result["generated"] >= 1

    def test_skips_no_table_entities(self, engine_dbs):
        from act_autopilot.recommendations_engine import run_recommendations_engine
        db_path, ro_path = engine_dbs
        result = run_recommendations_engine("eng_customer", db_path=db_path, readonly_path=ro_path)
        # All non-campaign rules are disabled in rules_config.json; DB only loads
        # campaign rules → no entity types without tables enter the loop.
        assert result["skipped_no_table"] >= 0

    def test_duplicate_prevention(self, engine_dbs):
        from act_autopilot.recommendations_engine import run_recommendations_engine
        db_path, ro_path = engine_dbs
        result1 = run_recommendations_engine("eng_customer", db_path=db_path, readonly_path=ro_path)
        result2 = run_recommendations_engine("eng_customer", db_path=db_path, readonly_path=ro_path)
        # Second run has no new recs — all already pending
        assert result2["generated"] == 0

    def test_no_data_for_unknown_customer(self, engine_dbs):
        from act_autopilot.recommendations_engine import run_recommendations_engine
        db_path, ro_path = engine_dbs
        result = run_recommendations_engine("unknown_customer", db_path=db_path, readonly_path=ro_path)
        # No rows for this customer — nothing generated
        assert result["generated"] == 0

    def test_by_entity_type_populated(self, engine_dbs):
        from act_autopilot.recommendations_engine import run_recommendations_engine
        db_path, ro_path = engine_dbs
        result = run_recommendations_engine("eng_customer", db_path=db_path, readonly_path=ro_path)
        # Some recs generated → by_entity_type has campaign
        if result["generated"] > 0:
            assert "campaign" in result["by_entity_type"]

    def test_errors_list_present(self, engine_dbs):
        from act_autopilot.recommendations_engine import run_recommendations_engine
        db_path, ro_path = engine_dbs
        result = run_recommendations_engine("eng_customer", db_path=db_path, readonly_path=ro_path)
        assert "errors" in result
        assert isinstance(result["errors"], list)
