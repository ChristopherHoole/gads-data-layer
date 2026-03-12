"""
tests/test_rule_helpers.py

Tests for act_dashboard/routes/rule_helpers.py pure functions.
Chat 89.
"""

import pytest


# ---------------------------------------------------------------------------
# parse_rule_docstring — pure function (lines 5-96)
# ---------------------------------------------------------------------------

class TestParseRuleDocstring:
    def _import(self):
        from act_dashboard.routes.rule_helpers import parse_rule_docstring
        return parse_rule_docstring

    def test_empty_docstring_returns_defaults(self):
        fn = self._import()
        result = fn("")
        assert result["description"] == ""
        assert result["risk_tier"] == "unknown"
        assert result["thresholds"] == []

    def test_none_docstring_returns_defaults(self):
        fn = self._import()
        result = fn(None)
        assert result["risk_tier"] == "unknown"

    def test_real_docstring_parsed(self):
        fn = self._import()
        doc = """Increase budget for high-ROAS campaigns.

Trigger: ROAS > 4.0 for last 30 days.
Action: Increase budget by 15%.
Risk: low
"""
        result = fn(doc)
        assert isinstance(result, dict)
        assert "description" in result


# ---------------------------------------------------------------------------
# format_rule_metadata — tests for edge-case branches (lines 99-148)
# ---------------------------------------------------------------------------

class TestFormatRuleMetadata:
    def _import(self):
        from act_dashboard.routes.rule_helpers import format_rule_metadata
        return format_rule_metadata

    def test_function_without_number_in_name(self):
        """Covers line 125: rule_id fallback when no _NNN_ pattern."""
        fn = self._import()

        def my_rule_fn():
            """No description here."""
            pass

        result = fn(my_rule_fn, "BUDGET")
        assert "BUDGET" in result["rule_id"]

    def test_function_with_no_description(self):
        """Covers lines 131-134: humanize function name when description empty."""
        fn = self._import()

        def increase_low_ctr():
            pass  # no docstring

        result = fn(increase_low_ctr, "KEYWORD")
        assert isinstance(result["name"], str)
        assert len(result["name"]) > 0

    def test_standard_numbered_function(self):
        fn = self._import()

        def budget_001_increase_high_roas():
            """Increase budget for high-ROAS campaigns.

Action: Increase budget by 15%.
Risk: low
"""
            pass

        result = fn(budget_001_increase_high_roas, "BUDGET")
        assert result["rule_id"] == "BUDGET-001"


# ---------------------------------------------------------------------------
# get_rules_for_page — line 233: unknown page_type warning
# ---------------------------------------------------------------------------

class TestGetRulesForPage:
    def _import(self):
        from act_dashboard.routes.rule_helpers import get_rules_for_page
        return get_rules_for_page

    def test_unknown_page_type_returns_empty(self):
        """Covers line 233: unknown page_type logs warning and returns []."""
        fn = self._import()
        result = fn("nonexistent_page_type")
        assert isinstance(result, list)

    def test_campaign_page_returns_list(self):
        fn = self._import()
        result = fn("campaign")
        assert isinstance(result, list)

    def test_ad_page_returns_list(self):
        fn = self._import()
        result = fn("ad")
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# get_enabled_rules — line 268
# ---------------------------------------------------------------------------

class TestGetEnabledRules:
    def _import(self):
        from act_dashboard.routes.rule_helpers import get_enabled_rules
        return get_enabled_rules

    def test_filters_to_enabled_only(self):
        """Covers line 268."""
        fn = self._import()
        rules = [
            {"rule_id": "A", "enabled": True},
            {"rule_id": "B", "enabled": False},
            {"rule_id": "C", "enabled": True},
        ]
        result = fn(rules)
        assert len(result) == 2
        assert all(r["enabled"] for r in result)

    def test_empty_list_returns_empty(self):
        fn = self._import()
        assert fn([]) == []

    def test_all_disabled_returns_empty(self):
        fn = self._import()
        rules = [{"rule_id": "A", "enabled": False}]
        assert fn(rules) == []


# ---------------------------------------------------------------------------
# group_rules_by_category — lines 281-287
# ---------------------------------------------------------------------------

class TestGroupRulesByCategory:
    def _import(self):
        from act_dashboard.routes.rule_helpers import group_rules_by_category
        return group_rules_by_category

    def test_groups_by_category(self):
        """Covers lines 281-287."""
        fn = self._import()
        rules = [
            {"rule_id": "A", "category": "BUDGET"},
            {"rule_id": "B", "category": "BID"},
            {"rule_id": "C", "category": "BUDGET"},
        ]
        result = fn(rules)
        assert "BUDGET" in result
        assert "BID" in result
        assert len(result["BUDGET"]) == 2
        assert len(result["BID"]) == 1

    def test_empty_list_returns_empty_dict(self):
        fn = self._import()
        assert fn([]) == {}

    def test_no_category_field_uses_other(self):
        fn = self._import()
        rules = [{"rule_id": "X"}]
        result = fn(rules)
        assert "OTHER" in result
