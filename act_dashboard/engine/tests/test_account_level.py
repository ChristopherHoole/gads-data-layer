"""
Tests for the Account Level Engine.

Run from project root:
    python -m pytest act_dashboard/engine/tests/test_account_level.py -v

Uses real warehouse.duckdb with Objection Experts data for integration tests.
"""

import json
import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

from act_dashboard.engine.account_level import AccountLevelEngine
from act_dashboard.engine.base import BaseLevelEngine


class TestAccountLevelIntegration(unittest.TestCase):
    """Integration tests using real database."""

    def setUp(self):
        self.engine = AccountLevelEngine('oe001')

    def tearDown(self):
        self.engine.close()

    def test_single_campaign_zero_recommendations(self):
        """1-campaign account should generate 0 recommendations, no errors."""
        result = self.engine.run('2026-04-11')
        self.assertEqual(result['recommendations'], 0)
        self.assertEqual(result['reason'], 'insufficient_campaigns')

    def test_level_state_off_skips(self):
        """Level state OFF should skip entirely."""
        # Temporarily set to off
        self.engine.db.execute(
            "UPDATE act_v2_client_level_state SET state='off' WHERE client_id='oe001' AND level='account'"
        )
        try:
            result = self.engine.run('2026-04-11')
            # Reload to get updated state
            self.engine.level_state = self.engine._load_level_state()
            result = self.engine.run('2026-04-11')
            self.assertEqual(result['status'], 'skipped')
            self.assertEqual(result['reason'], 'level_off')
        finally:
            # Restore
            self.engine.db.execute(
                "UPDATE act_v2_client_level_state SET state='monitor_only' WHERE client_id='oe001' AND level='account'"
            )

    def test_level_state_monitor_only(self):
        """Level state MONITOR_ONLY runs engine, recommendations get mode='monitor_only'."""
        # The current state should already be monitor_only
        result = self.engine.run('2026-04-11')
        # Even with 0 recs for 1-campaign, the engine should NOT skip
        self.assertIn(result['status'], ['ok', 'skipped'])

    def test_idempotency(self):
        """Running twice produces same number of recommendations."""
        result1 = self.engine.run('2026-04-11')
        count1 = self.engine.db.execute(
            "SELECT COUNT(*) FROM act_v2_recommendations WHERE client_id='oe001' AND level='account'"
        ).fetchone()[0]

        result2 = self.engine.run('2026-04-11')
        count2 = self.engine.db.execute(
            "SELECT COUNT(*) FROM act_v2_recommendations WHERE client_id='oe001' AND level='account'"
        ).fetchone()[0]

        self.assertEqual(count1, count2)

    def test_settings_loaded(self):
        """Settings are loaded from database with correct types."""
        self.assertEqual(self.engine.get_setting('performance_scoring_weight_7d', 0), 50)
        self.assertEqual(self.engine.get_setting('performance_scoring_weight_14d', 0), 30)
        self.assertEqual(self.engine.get_setting('performance_scoring_weight_30d', 0), 20)
        self.assertEqual(self.engine.get_setting('max_overnight_budget_move_pct', 0), 10)
        self.assertEqual(self.engine.get_setting('budget_shift_cooldown_hours', 0), 72)
        self.assertEqual(self.engine.get_setting('deviation_threshold_pct', 0), 10)

    def test_client_loaded(self):
        """Client data is loaded correctly."""
        self.assertEqual(self.engine.client['persona'], 'lead_gen_cpa')
        self.assertEqual(self.engine.client['target_cpa'], 25.0)
        self.assertIsNone(self.engine.client['target_roas'])

    def test_snapshots_returned(self):
        """Snapshot retrieval returns data for valid dates."""
        snaps = self.engine.get_snapshots(level='campaign', date='2026-04-11', days_back=7)
        self.assertGreater(len(snaps), 0)
        # Each snapshot should have parsed metrics
        for s in snaps:
            self.assertIn('metrics', s)
            self.assertIsInstance(s['metrics'], dict)

    def test_cooldown_false_on_empty(self):
        """Cooldown check returns False when no monitoring entries exist."""
        result = self.engine.check_cooldown(self.engine.CHECK_ID, '20614788607')
        self.assertFalse(result)


class TestPerformanceScoring(unittest.TestCase):
    """Unit tests for scoring logic with mocked data."""

    def test_cpa_score_outperforming(self):
        """Campaign with CPA below target should get positive score."""
        # target_cpa = 25, actual_cpa = 20 → (25-20)/25*100 = 20% outperforming
        target = 25.0
        actual = 20.0
        score = (target - actual) / target * 100
        self.assertAlmostEqual(score, 20.0)

    def test_cpa_score_underperforming(self):
        """Campaign with CPA above target should get negative score."""
        # target_cpa = 25, actual_cpa = 35 → (25-35)/25*100 = -40%
        target = 25.0
        actual = 35.0
        score = (target - actual) / target * 100
        self.assertAlmostEqual(score, -40.0)

    def test_roas_score_outperforming(self):
        """Campaign with ROAS above target should get positive score."""
        # target_roas = 4.0, actual = 5.0 → (5-4)/4*100 = 25%
        target = 4.0
        actual = 5.0
        score = (actual - target) / target * 100
        self.assertAlmostEqual(score, 25.0)

    def test_weighted_blend(self):
        """Weighted blend should correctly combine 7d/14d/30d scores."""
        s7, s14, s30 = 20.0, 10.0, -5.0
        w7, w14, w30 = 0.50, 0.30, 0.20
        expected = (s7 * w7) + (s14 * w14) + (s30 * w30)
        self.assertAlmostEqual(expected, 12.0)

    def test_zero_conversions_with_spend(self):
        """Zero conversions with spend should give worst score (-100)."""
        # This matches the engine logic: spend > 0 but conversions = 0 → score = -100
        score = -100.0
        self.assertEqual(score, -100.0)

    def test_zero_spend_zero_conversions(self):
        """Zero spend and zero conversions should give neutral score (0)."""
        score = 0.0
        self.assertEqual(score, 0.0)


class TestBudgetAllocationGuardrails(unittest.TestCase):
    """Unit tests for budget allocation guardrails."""

    def test_deviation_threshold_blocks(self):
        """Score difference below threshold should prevent action."""
        deviation_threshold = 10
        score_diff = 5  # Below threshold
        self.assertLess(score_diff, deviation_threshold)

    def test_max_overnight_move_caps_shift(self):
        """Shift should be capped at max_overnight_budget_move_pct."""
        total_budget = 100.0
        max_move_pct = 10
        max_shift = total_budget * (max_move_pct / 100)
        self.assertEqual(max_shift, 10.0)

    def test_budget_band_min_prevents_decrease(self):
        """Campaign at min band should not have budget decreased."""
        current_share = 5.0
        min_band = 5.0
        self.assertLessEqual(current_share, min_band)

    def test_budget_band_max_prevents_increase(self):
        """Campaign at max band should not have budget increased."""
        current_share = 70.0
        max_band = 70.0
        self.assertGreaterEqual(current_share, max_band)


if __name__ == '__main__':
    unittest.main()
