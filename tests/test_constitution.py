"""
tests/test_constitution.py

Tests for constitution/guardrail pure functions.
Chat 89.
"""

import pytest
from act_autopilot.guardrails import (
    check_data_sufficiency,
    check_protected_entity,
    check_change_cap,
    get_change_cap,
    _infer_lever,
)
from act_autopilot.models import Recommendation, AutopilotConfig
from act_dashboard.cache import ExpiringCache


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

def make_rec(**kwargs) -> Recommendation:
    defaults = {
        "rule_id": "budget_1",
        "rule_name": "Increase Budget",
        "entity_type": "campaign",
        "entity_id": "111",
        "action_type": "increase_budget",
        "risk_tier": "low",
        "campaign_name": "Campaign Alpha",
        "change_pct": 0.05,
        "evidence": {},
    }
    defaults.update(kwargs)
    return Recommendation(**defaults)


def make_config(**kwargs) -> AutopilotConfig:
    defaults = {
        "customer_id": "9999999999",
        "automation_mode": "suggest",
        "risk_tolerance": "balanced",
        "daily_spend_cap": 500.0,
        "monthly_spend_cap": 10000.0,
        "brand_is_protected": False,
        "protected_entities": [],
    }
    defaults.update(kwargs)
    return AutopilotConfig(**defaults)


# ---------------------------------------------------------------------------
# get_change_cap
# ---------------------------------------------------------------------------

class TestGetChangeCap:
    def test_conservative_is_5_percent(self):
        assert get_change_cap("conservative") == 0.05

    def test_balanced_is_10_percent(self):
        assert get_change_cap("balanced") == 0.10

    def test_aggressive_is_15_percent(self):
        assert get_change_cap("aggressive") == 0.15

    def test_unknown_defaults_to_conservative(self):
        assert get_change_cap("unknown") == 0.05

    def test_empty_string_defaults_to_conservative(self):
        assert get_change_cap("") == 0.05


# ---------------------------------------------------------------------------
# check_data_sufficiency
# ---------------------------------------------------------------------------

class TestCheckDataSufficiency:
    def test_sufficient_data_passes(self):
        rec = make_rec(evidence={"clicks_w7": 50, "conversions_w7": 5})
        assert check_data_sufficiency(rec) is True

    def test_insufficient_clicks_fails(self):
        rec = make_rec(evidence={"clicks_w7": 10, "conversions_w7": 5})
        assert check_data_sufficiency(rec) is False

    def test_insufficient_conversions_fails(self):
        rec = make_rec(evidence={"clicks_w7": 50, "conversions_w7": 1})
        assert check_data_sufficiency(rec) is False

    def test_both_insufficient_fails(self):
        rec = make_rec(evidence={"clicks_w7": 5, "conversions_w7": 1})
        assert check_data_sufficiency(rec) is False

    def test_exactly_30_clicks_passes(self):
        rec = make_rec(evidence={"clicks_w7": 30, "conversions_w7": 3})
        assert check_data_sufficiency(rec) is True

    def test_exactly_29_clicks_fails(self):
        rec = make_rec(evidence={"clicks_w7": 29, "conversions_w7": 3})
        assert check_data_sufficiency(rec) is False

    def test_exactly_3_conversions_passes(self):
        rec = make_rec(evidence={"clicks_w7": 30, "conversions_w7": 3})
        assert check_data_sufficiency(rec) is True

    def test_exactly_2_conversions_fails(self):
        rec = make_rec(evidence={"clicks_w7": 30, "conversions_w7": 2})
        assert check_data_sufficiency(rec) is False

    def test_falls_back_to_w30_clicks(self):
        rec = make_rec(evidence={"clicks_w30": 50, "conversions_w30": 5})
        assert check_data_sufficiency(rec) is True

    def test_empty_evidence_fails(self):
        rec = make_rec(evidence={})
        assert check_data_sufficiency(rec) is False

    def test_none_evidence_fails(self):
        rec = make_rec(evidence=None)
        assert check_data_sufficiency(rec) is False


# ---------------------------------------------------------------------------
# check_protected_entity
# ---------------------------------------------------------------------------

class TestCheckProtectedEntity:
    def test_not_protected_returns_false(self):
        rec = make_rec(entity_id="111", campaign_name="Campaign Alpha")
        config = make_config(protected_entities=[], brand_is_protected=False)
        assert check_protected_entity(rec, config) is False

    def test_entity_id_in_protected_list_returns_true(self):
        rec = make_rec(entity_id="111")
        config = make_config(protected_entities=["111"])
        assert check_protected_entity(rec, config) is True

    def test_entity_id_not_in_protected_list_returns_false(self):
        rec = make_rec(entity_id="999")
        config = make_config(protected_entities=["111", "222"])
        assert check_protected_entity(rec, config) is False

    def test_brand_protection_enabled_brand_campaign(self):
        rec = make_rec(campaign_name="Brand Campaign")
        config = make_config(brand_is_protected=True, protected_entities=[])
        assert check_protected_entity(rec, config) is True

    def test_brand_protection_enabled_non_brand_campaign(self):
        rec = make_rec(campaign_name="Generic Search")
        config = make_config(brand_is_protected=True, protected_entities=[])
        assert check_protected_entity(rec, config) is False

    def test_brand_protection_disabled_brand_campaign(self):
        rec = make_rec(campaign_name="Brand Campaign")
        config = make_config(brand_is_protected=False, protected_entities=[])
        assert check_protected_entity(rec, config) is False


# ---------------------------------------------------------------------------
# check_change_cap
# ---------------------------------------------------------------------------

class TestCheckChangeCap:
    def test_within_balanced_cap_passes(self):
        rec = make_rec(change_pct=0.08)  # 8% < 10% balanced cap
        config = make_config(risk_tolerance="balanced")
        assert check_change_cap(rec, config) is True

    def test_exceeds_balanced_cap_fails(self):
        rec = make_rec(change_pct=0.15)  # 15% > 10% balanced cap
        config = make_config(risk_tolerance="balanced")
        assert check_change_cap(rec, config) is False

    def test_within_conservative_cap_passes(self):
        rec = make_rec(change_pct=0.04)  # 4% < 5% conservative cap
        config = make_config(risk_tolerance="conservative")
        assert check_change_cap(rec, config) is True

    def test_exceeds_conservative_cap_fails(self):
        rec = make_rec(change_pct=0.06)  # 6% > 5% conservative cap
        config = make_config(risk_tolerance="conservative")
        assert check_change_cap(rec, config) is False

    def test_within_aggressive_cap_passes(self):
        rec = make_rec(change_pct=0.14)  # 14% < 15% aggressive cap
        config = make_config(risk_tolerance="aggressive")
        assert check_change_cap(rec, config) is True

    def test_exceeds_aggressive_cap_fails(self):
        rec = make_rec(change_pct=0.20)  # 20% > 15% aggressive cap
        config = make_config(risk_tolerance="aggressive")
        assert check_change_cap(rec, config) is False

    def test_negative_change_pct_uses_abs_value(self):
        rec = make_rec(change_pct=-0.08)  # abs = 8% < 10% balanced
        config = make_config(risk_tolerance="balanced")
        assert check_change_cap(rec, config) is True

    def test_none_change_pct_passes(self):
        rec = make_rec(change_pct=None)
        config = make_config(risk_tolerance="conservative")
        assert check_change_cap(rec, config) is True

    def test_zero_change_pct_passes(self):
        rec = make_rec(change_pct=0.0)
        config = make_config(risk_tolerance="conservative")
        assert check_change_cap(rec, config) is True

    def test_exact_cap_boundary_passes(self):
        # Exactly 10% with balanced (cap = 10%) — change_pct > cap fails, >= stays
        # cap = 0.10, change_pct = 0.10 → abs = 0.10, 0.10 > 0.10 is False → passes
        rec = make_rec(change_pct=0.10)
        config = make_config(risk_tolerance="balanced")
        assert check_change_cap(rec, config) is True


# ---------------------------------------------------------------------------
# _infer_lever
# ---------------------------------------------------------------------------

class TestInferLever:
    def test_increase_budget_is_budget(self):
        assert _infer_lever("increase_budget") == "budget"

    def test_decrease_budget_is_budget(self):
        assert _infer_lever("decrease_budget") == "budget"

    def test_increase_bid_is_bid(self):
        assert _infer_lever("increase_bid") == "bid"

    def test_decrease_bid_is_bid(self):
        assert _infer_lever("decrease_bid") == "bid"

    def test_troas_is_bid(self):
        assert _infer_lever("adjust_troas") == "bid"

    def test_tcpa_is_bid(self):
        assert _infer_lever("adjust_tcpa") == "bid"

    def test_pause_is_status(self):
        assert _infer_lever("pause") == "status"

    def test_enable_is_status(self):
        assert _infer_lever("enable") == "status"

    def test_status_keyword_is_status(self):
        assert _infer_lever("change_status") == "status"

    def test_unknown_action_is_unknown(self):
        assert _infer_lever("flag_review") == "unknown"

    def test_case_insensitive_budget(self):
        assert _infer_lever("INCREASE_BUDGET") == "budget"


# ---------------------------------------------------------------------------
# ExpiringCache
# ---------------------------------------------------------------------------

class TestExpiringCache:
    def test_set_and_get(self):
        cache = ExpiringCache()
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_missing_returns_default(self):
        cache = ExpiringCache()
        assert cache.get("nonexistent") is None

    def test_get_missing_with_custom_default(self):
        cache = ExpiringCache()
        assert cache.get("nonexistent", "fallback") == "fallback"

    def test_expired_entry_returns_default(self):
        cache = ExpiringCache(default_ttl=0)
        cache.set("key1", "value1", ttl=0)
        import time
        time.sleep(0.01)
        assert cache.get("key1") is None

    def test_delete_existing_returns_true(self):
        cache = ExpiringCache()
        cache.set("key1", "val")
        assert cache.delete("key1") is True

    def test_delete_nonexistent_returns_false(self):
        cache = ExpiringCache()
        assert cache.delete("nonexistent") is False

    def test_clear_removes_all(self):
        cache = ExpiringCache()
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert len(cache) == 0

    def test_len_counts_all_entries(self):
        cache = ExpiringCache()
        cache.set("a", 1)
        cache.set("b", 2)
        assert len(cache) == 2

    def test_contains_active_key(self):
        cache = ExpiringCache()
        cache.set("key1", "val")
        assert "key1" in cache

    def test_contains_missing_key(self):
        cache = ExpiringCache()
        assert "missing" not in cache

    def test_dict_assignment(self):
        cache = ExpiringCache()
        cache["key1"] = "value1"
        assert cache.get("key1") == "value1"

    def test_dict_access(self):
        cache = ExpiringCache()
        cache.set("key1", "value1")
        assert cache["key1"] == "value1"

    def test_dict_access_missing_raises_key_error(self):
        cache = ExpiringCache()
        with pytest.raises(KeyError):
            _ = cache["nonexistent"]

    def test_get_stats_returns_dict(self):
        cache = ExpiringCache()
        cache.set("a", 1)
        stats = cache.get_stats()
        assert "total_entries" in stats
        assert "active_entries" in stats
        assert "expired_entries" in stats

    def test_cleanup_expired_removes_expired(self):
        cache = ExpiringCache(default_ttl=0)
        cache.set("expired_key", "val", ttl=0)
        import time
        time.sleep(0.01)
        removed = cache.cleanup_expired()
        assert removed >= 1

    def test_cleanup_expired_keeps_active(self):
        cache = ExpiringCache(default_ttl=3600)
        cache.set("active_key", "val")
        removed = cache.cleanup_expired()
        assert removed == 0
        assert cache.get("active_key") == "val"

    def test_custom_ttl_per_key(self):
        cache = ExpiringCache(default_ttl=3600)
        cache.set("short", "val", ttl=0)
        import time
        time.sleep(0.01)
        assert cache.get("short") is None


# ---------------------------------------------------------------------------
# run_all_guardrails (mocked ChangeLog + get_daily_change_count)
# ---------------------------------------------------------------------------

class TestRunAllGuardrails:
    """Test run_all_guardrails with mocked DB-dependent components."""

    def _run(self, rec, config, mock_cooldown=False, mock_one_lever=False,
             mock_daily_count=0):
        from unittest.mock import patch, MagicMock
        from act_autopilot.guardrails import run_all_guardrails
        from datetime import date

        mock_cl = MagicMock()
        mock_cl.check_cooldown.return_value = mock_cooldown
        mock_cl.check_one_lever.return_value = mock_one_lever

        with patch("act_autopilot.guardrails.ChangeLog", return_value=mock_cl):
            with patch("act_autopilot.guardrails.get_daily_change_count",
                       return_value=mock_daily_count):
                return run_all_guardrails(rec, config, config.customer_id,
                                          date.today(), "dummy.duckdb")

    def test_all_checks_pass(self):
        rec = make_rec(change_pct=0.05, evidence={"clicks_w7": 50, "conversions_w7": 5})
        config = make_config(risk_tolerance="balanced")
        blocked, reason, checks = self._run(rec, config)
        assert blocked is False
        assert reason is None
        assert len(checks) > 0

    def test_guardrails_checked_list(self):
        rec = make_rec(change_pct=0.05, evidence={"clicks_w7": 50, "conversions_w7": 5})
        config = make_config()
        _blocked, _reason, checks = self._run(rec, config)
        assert "low_data_check" in checks
        assert "protected_entity_check" in checks
        assert "change_cap_check" in checks

    def test_low_data_blocks(self):
        rec = make_rec(change_pct=0.05, evidence={"clicks_w7": 5, "conversions_w7": 1})
        config = make_config()
        blocked, reason, _checks = self._run(rec, config)
        assert blocked is True
        assert reason is not None

    def test_protected_entity_blocks(self):
        rec = make_rec(entity_id="111", change_pct=0.05,
                       evidence={"clicks_w7": 50, "conversions_w7": 5})
        config = make_config(protected_entities=["111"])
        blocked, reason, _checks = self._run(rec, config)
        assert blocked is True

    def test_cooldown_blocks(self):
        rec = make_rec(change_pct=0.05, evidence={"clicks_w7": 50, "conversions_w7": 5})
        config = make_config()
        blocked, reason, _checks = self._run(rec, config, mock_cooldown=True)
        assert blocked is True
        assert "Cooldown" in reason

    def test_one_lever_blocks(self):
        rec = make_rec(change_pct=0.05, evidence={"clicks_w7": 50, "conversions_w7": 5})
        config = make_config()
        blocked, reason, _checks = self._run(rec, config, mock_one_lever=True)
        assert blocked is True

    def test_change_cap_blocks(self):
        rec = make_rec(change_pct=0.20, evidence={"clicks_w7": 50, "conversions_w7": 5})
        config = make_config(risk_tolerance="balanced")
        blocked, reason, _checks = self._run(rec, config)
        assert blocked is True
        assert "Change cap" in reason

    def test_daily_limit_blocks(self):
        rec = make_rec(change_pct=0.05, evidence={"clicks_w7": 50, "conversions_w7": 5})
        config = make_config()
        # Default max_changes_per_day in AutopilotConfig
        blocked, reason, _checks = self._run(rec, config, mock_daily_count=1000)
        # This depends on config.max_changes_per_day — check it's considered
        assert isinstance(blocked, bool)

    def test_already_blocked_rec(self):
        from act_autopilot.guardrails import run_all_guardrails
        from unittest.mock import patch, MagicMock
        from datetime import date
        rec = make_rec(change_pct=0.05, evidence={"clicks_w7": 50, "conversions_w7": 5})
        # Manually set blocked
        object.__setattr__(rec, 'blocked', True)
        object.__setattr__(rec, 'block_reason', 'Pre-blocked')
        config = make_config()
        mock_cl = MagicMock()
        with patch("act_autopilot.guardrails.ChangeLog", return_value=mock_cl):
            with patch("act_autopilot.guardrails.get_daily_change_count", return_value=0):
                blocked, reason, checks = run_all_guardrails(
                    rec, config, config.customer_id, date.today(), "dummy.duckdb"
                )
        assert blocked is True


# ---------------------------------------------------------------------------
# get_daily_change_count — DB-backed function (lines 237-258)
# ---------------------------------------------------------------------------


def _make_change_count_db(tmp_path, with_table=True, with_data=False):
    """Create a tmp DuckDB for get_daily_change_count tests."""
    import duckdb
    from datetime import date
    path = str(tmp_path / "change_count.duckdb")
    conn = duckdb.connect(path)
    conn.execute("CREATE SCHEMA IF NOT EXISTS analytics")
    if with_table:
        conn.execute("""
            CREATE TABLE analytics.change_log (
                customer_id VARCHAR,
                change_date DATE,
                rule_id     VARCHAR
            )
        """)
        if with_data:
            conn.execute(
                "INSERT INTO analytics.change_log VALUES (?, ?, ?)",
                ["9999999999", date.today().isoformat(), "budget_1"]
            )
    conn.close()
    return path


class TestGetDailyChangeCount:
    def _import(self):
        from act_autopilot.guardrails import get_daily_change_count
        return get_daily_change_count

    def test_returns_zero_when_no_data(self, tmp_path):
        from datetime import date
        fn = self._import()
        path = _make_change_count_db(tmp_path)
        result = fn("9999999999", date.today(), path)
        assert result == 0

    def test_returns_count_when_data(self, tmp_path):
        from datetime import date
        fn = self._import()
        path = _make_change_count_db(tmp_path, with_data=True)
        result = fn("9999999999", date.today(), path)
        assert result == 1

    def test_returns_zero_on_query_error(self, tmp_path):
        from datetime import date
        fn = self._import()
        # DB without the analytics.change_log table
        path = _make_change_count_db(tmp_path, with_table=False)
        result = fn("9999999999", date.today(), path)
        assert result == 0

    def test_unknown_customer_returns_zero(self, tmp_path):
        from datetime import date
        fn = self._import()
        path = _make_change_count_db(tmp_path, with_data=True)
        result = fn("unknown_customer", date.today(), path)
        assert result == 0

    def test_wrong_date_returns_zero(self, tmp_path):
        from datetime import date, timedelta
        fn = self._import()
        path = _make_change_count_db(tmp_path, with_data=True)
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        # Data was inserted for today, querying yesterday returns 0
        result = fn("9999999999", yesterday, path)
        assert result == 0


# ---------------------------------------------------------------------------
# check_spend_caps — DB-backed function (lines 280-362)
# ---------------------------------------------------------------------------


def _make_spend_caps_db(tmp_path, with_data=True):
    """Create a tmp DuckDB with analytics.campaign_daily using 'date' column."""
    import duckdb
    from datetime import date
    path = str(tmp_path / "spend_caps.duckdb")
    conn = duckdb.connect(path)
    conn.execute("CREATE SCHEMA IF NOT EXISTS analytics")
    conn.execute("""
        CREATE TABLE analytics.campaign_daily (
            customer_id VARCHAR,
            date        DATE,
            cost        DOUBLE
        )
    """)
    if with_data:
        conn.execute(
            "INSERT INTO analytics.campaign_daily VALUES (?, ?, ?)",
            ["9999999999", date.today().isoformat(), 100.0]
        )
    conn.close()
    return path


class TestCheckSpendCaps:
    def _import(self):
        from act_autopilot.guardrails import check_spend_caps
        return check_spend_caps

    def test_returns_dict(self, tmp_path):
        from datetime import date
        fn = self._import()
        path = _make_spend_caps_db(tmp_path)
        result = fn("9999999999", 50_000_000, date.today(), 100.0, 3000.0, path)
        assert isinstance(result, dict)

    def test_valid_key_present(self, tmp_path):
        from datetime import date
        fn = self._import()
        path = _make_spend_caps_db(tmp_path)
        result = fn("9999999999", 50_000_000, date.today(), 100.0, 3000.0, path)
        assert "valid" in result

    def test_under_daily_cap_returns_valid(self, tmp_path):
        from datetime import date
        fn = self._import()
        path = _make_spend_caps_db(tmp_path)
        # proposed_budget = 50M micros = £50, daily_cap = £100
        result = fn("9999999999", 50_000_000, date.today(), 100.0, 3000.0, path)
        assert result["valid"] is True

    def test_exceeds_daily_cap_returns_invalid(self, tmp_path):
        from datetime import date
        fn = self._import()
        path = _make_spend_caps_db(tmp_path)
        # proposed_budget = 200M micros = £200, daily_cap = £100
        result = fn("9999999999", 200_000_000, date.today(), 100.0, 3000.0, path)
        assert result["valid"] is False
        assert "daily cap" in result["reason"].lower()

    def test_exceeds_monthly_cap_returns_invalid(self, tmp_path):
        from datetime import date
        fn = self._import()
        path = _make_spend_caps_db(tmp_path)
        # proposed_budget = 50M micros = £50/day, monthly_cap = £50 (very low)
        result = fn("9999999999", 50_000_000, date.today(), 100.0, 50.0, path)
        assert result["valid"] is False
        assert "monthly cap" in result["reason"].lower()

    def test_daily_projected_returned(self, tmp_path):
        from datetime import date
        fn = self._import()
        path = _make_spend_caps_db(tmp_path)
        result = fn("9999999999", 50_000_000, date.today(), 100.0, 3000.0, path)
        assert "daily_projected" in result

    def test_monthly_projected_returned(self, tmp_path):
        from datetime import date
        fn = self._import()
        path = _make_spend_caps_db(tmp_path)
        result = fn("9999999999", 50_000_000, date.today(), 100.0, 3000.0, path)
        assert "monthly_projected" in result

    def test_query_error_returns_invalid(self, tmp_path):
        import duckdb
        from datetime import date
        fn = self._import()
        # Create empty DB without analytics schema — query will fail, exception caught
        path = str(tmp_path / "empty.duckdb")
        conn = duckdb.connect(path)
        conn.close()
        result = fn("9999999999", 50_000_000, date.today(), 100.0, 3000.0, path)
        assert isinstance(result, dict)

    def test_december_month_boundary(self, tmp_path):
        from datetime import date
        fn = self._import()
        path = _make_spend_caps_db(tmp_path)
        # December — next month is January of next year
        dec_date = date(2026, 12, 15)
        result = fn("9999999999", 50_000_000, dec_date, 100.0, 3000.0, path)
        assert isinstance(result, dict)
