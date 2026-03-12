"""
tests/test_rules_engine.py

Tests for rules config schema and rule evaluation logic.
Chat 89.
"""

import json
from pathlib import Path
import pytest
from act_autopilot.recommendations_engine import _evaluate, _detect_entity_type


RULES_CONFIG_PATH = Path(__file__).parent.parent / "act_autopilot" / "rules_config.json"

REQUIRED_RULE_KEYS = {
    "rule_id", "rule_type", "action_direction", "action_magnitude", "enabled",
}


class TestRulesConfigSchema:
    @pytest.fixture(scope="class")
    def rules(self):
        with open(RULES_CONFIG_PATH, "r") as f:
            return json.load(f)

    def test_loads_without_error(self, rules):
        assert isinstance(rules, list)
        assert len(rules) > 0

    def test_all_rules_have_required_keys(self, rules):
        for rule in rules:
            for key in REQUIRED_RULE_KEYS:
                assert key in rule, f"Rule {rule.get('rule_id')} missing key: {key}"

    def test_rule_ids_are_strings(self, rules):
        for rule in rules:
            assert isinstance(rule["rule_id"], str)
            assert len(rule["rule_id"]) > 0

    def test_action_magnitude_is_numeric_or_null(self, rules):
        for rule in rules:
            mag = rule.get("action_magnitude")
            assert mag is None or isinstance(mag, (int, float)), \
                f"Rule {rule['rule_id']} action_magnitude must be numeric or null: {mag}"

    def test_action_direction_valid_values(self, rules):
        valid = {
            "increase", "decrease", "pause", "enable", "flag", "hold",
            "increase_bid", "decrease_bid", "increase_budget", "decrease_budget",
        }
        for rule in rules:
            assert rule["action_direction"] in valid, \
                f"Rule {rule['rule_id']} invalid action_direction: {rule['action_direction']}"

    def test_enabled_is_boolean(self, rules):
        for rule in rules:
            assert isinstance(rule["enabled"], bool)

    def test_budget_1_rule_exists(self, rules):
        ids = [r["rule_id"] for r in rules]
        assert "budget_1" in ids

    def test_budget_2_rule_exists(self, rules):
        ids = [r["rule_id"] for r in rules]
        assert "budget_2" in ids

    def test_budget_1_is_enabled(self, rules):
        rule = next(r for r in rules if r["rule_id"] == "budget_1")
        assert rule["enabled"] is True

    def test_budget_1_direction_is_increase(self, rules):
        rule = next(r for r in rules if r["rule_id"] == "budget_1")
        assert rule["action_direction"] == "increase"

    def test_budget_2_direction_is_decrease(self, rules):
        rule = next(r for r in rules if r["rule_id"] == "budget_2")
        assert rule["action_direction"] == "decrease"

    def test_budget_1_condition_metric_is_roas_7d(self, rules):
        rule = next(r for r in rules if r["rule_id"] == "budget_1")
        assert rule["condition_metric"] == "roas_7d"

    def test_budget_1_operator_is_gt(self, rules):
        rule = next(r for r in rules if r["rule_id"] == "budget_1")
        assert rule["condition_operator"] == "gt"


class TestRuleEvaluationBudget1:
    """budget_1: roas_7d > 1.15 × target AND clicks_7d >= 30 → increase budget."""

    @pytest.fixture(scope="class")
    def budget_1(self):
        with open(RULES_CONFIG_PATH) as f:
            rules = json.load(f)
        return next(r for r in rules if r["rule_id"] == "budget_1")

    def test_fires_when_roas_above_threshold(self, budget_1):
        # roas_7d = 5.0 > 1.15 condition_value (the x_target is evaluated via proxy)
        # We test the raw _evaluate helper
        result = _evaluate(5.0, budget_1["condition_operator"], budget_1["condition_value"])
        assert result is True

    def test_does_not_fire_when_roas_below_threshold(self, budget_1):
        result = _evaluate(1.0, budget_1["condition_operator"], budget_1["condition_value"])
        assert result is False

    def test_fires_when_clicks_above_threshold(self, budget_1):
        result = _evaluate(50, budget_1["condition_2_operator"], budget_1["condition_2_value"])
        assert result is True

    def test_does_not_fire_when_clicks_below_threshold(self, budget_1):
        result = _evaluate(5, budget_1["condition_2_operator"], budget_1["condition_2_value"])
        assert result is False

    def test_entity_type_from_budget_rule_id(self, budget_1):
        # budget_1 → fallback to "campaign"
        entity = _detect_entity_type(budget_1["rule_id"])
        assert entity == "campaign"


class TestRuleEvaluationBudget2:
    """budget_2: roas_7d < 0.75 AND clicks_7d >= 30 → decrease budget."""

    @pytest.fixture(scope="class")
    def budget_2(self):
        with open(RULES_CONFIG_PATH) as f:
            rules = json.load(f)
        return next(r for r in rules if r["rule_id"] == "budget_2")

    def test_fires_when_roas_below_threshold(self, budget_2):
        result = _evaluate(0.5, budget_2["condition_operator"], budget_2["condition_value"])
        assert result is True

    def test_does_not_fire_when_roas_above_threshold(self, budget_2):
        result = _evaluate(1.2, budget_2["condition_operator"], budget_2["condition_value"])
        assert result is False

    def test_action_direction_is_decrease(self, budget_2):
        assert budget_2["action_direction"] == "decrease"


class TestEvaluateBoundaries:
    """Edge cases for the _evaluate operator function."""

    def test_gt_boundary_equal_is_false(self):
        assert _evaluate(5.0, "gt", 5.0) is False

    def test_gte_boundary_equal_is_true(self):
        assert _evaluate(5.0, "gte", 5.0) is True

    def test_lt_boundary_equal_is_false(self):
        assert _evaluate(5.0, "lt", 5.0) is False

    def test_lte_boundary_equal_is_true(self):
        assert _evaluate(5.0, "lte", 5.0) is True

    def test_integer_vs_float(self):
        assert _evaluate(30, "gte", 30.0) is True

    def test_string_eq_case_sensitive(self):
        assert _evaluate("poor", "eq", "POOR") is False
