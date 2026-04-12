"""
ACT v2 Engine — Account Level

Implements the Account Level budget allocation check from v54 architecture.
Reads campaign performance data, calculates weighted scores, and generates
budget shift recommendations.
"""

import logging
from datetime import datetime, timedelta

from act_dashboard.engine.base import BaseLevelEngine

logger = logging.getLogger('act_v2_engine')


class AccountLevelEngine(BaseLevelEngine):
    LEVEL = 'account'
    CHECK_ID = 'account_budget_allocation'

    def run(self, evaluation_date: str):
        """Run all Account Level checks for a given date."""
        logger.info(f"{'=' * 50}")
        logger.info(f"Account Level Engine — {self.client['name']} ({self.client_id})")
        logger.info(f"Evaluation date: {evaluation_date}")
        logger.info(f"{'=' * 50}")

        # 1. Check if account level is enabled
        state = self.level_state.get('account', 'off')
        if state == 'off':
            logger.info(f"Account level is OFF for {self.client_id}, skipping")
            return {'status': 'skipped', 'reason': 'level_off', 'recommendations': 0}

        logger.info(f"Account level state: {state}")

        # 2. Clear old pending recommendations for idempotency
        self.clear_old_recommendations(self.LEVEL)

        # 3. Load ENABLED campaign data
        campaigns = self._get_enabled_campaigns(evaluation_date)
        logger.info(f"Found {len(campaigns)} ENABLED campaigns")

        if len(campaigns) < 2:
            logger.info(f"Only {len(campaigns)} ENABLED campaign(s) — budget allocation requires 2+, no action needed")
            return {'status': 'ok', 'reason': 'insufficient_campaigns', 'recommendations': 0}

        # 4. Get campaign roles
        roles = self._get_campaign_roles()

        # 5. Calculate performance scores
        scored = self._score_campaigns(campaigns, evaluation_date)
        for c in scored:
            logger.info(f"  {c['name']}: score={c['score']:.1f}, cost_30d={c['cost_30d']:.2f}, "
                        f"{'cpa' if self.client['persona'] == 'lead_gen_cpa' else 'roas'}_30d="
                        f"{c.get('cpa_30d', c.get('roas_30d', 'N/A'))}")

        # 6. Evaluate budget allocation
        recs = self._evaluate_budget_allocation(scored, roles, evaluation_date)
        logger.info(f"Generated {recs} recommendation(s)")

        return {'status': 'ok', 'recommendations': recs}

    def _get_enabled_campaigns(self, date: str) -> list:
        """Get ENABLED campaigns with their current-day metrics."""
        snapshots = self.get_snapshots(level='campaign', date=date, days_back=0)
        enabled = []
        for s in snapshots:
            status = s['metrics'].get('campaign_status', '')
            if status == 'ENABLED':
                enabled.append({
                    'entity_id': s['entity_id'],
                    'name': s['entity_name'],
                    'metrics': s['metrics'],
                })
        return enabled

    def _get_campaign_roles(self) -> dict:
        """Get campaign role assignments. Returns {campaign_id: role_code}."""
        rows = self.db.execute(
            "SELECT google_ads_campaign_id, role FROM act_v2_campaign_roles WHERE client_id = ?",
            [self.client_id]
        ).fetchall()
        roles = {str(r[0]): r[1] for r in rows}
        return roles

    def _score_campaigns(self, campaigns: list, date: str) -> list:
        """Calculate performance score for each campaign using weighted blend."""
        w7 = self.get_setting('performance_scoring_weight_7d', 50) / 100.0
        w14 = self.get_setting('performance_scoring_weight_14d', 30) / 100.0
        w30 = self.get_setting('performance_scoring_weight_30d', 20) / 100.0

        persona = self.client['persona']
        target_cpa = self.client['target_cpa']
        target_roas = self.client['target_roas']

        # Get all campaign snapshots for last 30 days (covers all 3 windows)
        all_snapshots = self.get_snapshots(level='campaign', date=date, days_back=30)

        # Calculate date boundaries
        eval_dt = datetime.strptime(date, '%Y-%m-%d')
        d7 = (eval_dt - timedelta(days=7)).strftime('%Y-%m-%d')
        d14 = (eval_dt - timedelta(days=14)).strftime('%Y-%m-%d')
        d30 = (eval_dt - timedelta(days=30)).strftime('%Y-%m-%d')

        scored = []
        for camp in campaigns:
            cid = camp['entity_id']

            # Filter snapshots to this campaign
            camp_snaps = [s for s in all_snapshots if s['entity_id'] == cid]

            # Aggregate for each window
            windows = {
                '7d': [s for s in camp_snaps if s['snapshot_date'] > d7],
                '14d': [s for s in camp_snaps if s['snapshot_date'] > d14],
                '30d': [s for s in camp_snaps if s['snapshot_date'] > d30],
            }

            if persona == 'lead_gen_cpa':
                scores = {}
                cpas = {}
                for window_name, snaps in windows.items():
                    total_cost = sum(s['metrics'].get('cost', 0) for s in snaps)
                    total_conv = sum(s['metrics'].get('conversions', 0) for s in snaps)

                    if total_conv > 0:
                        cpa = total_cost / total_conv
                        # Positive score = outperforming (CPA below target)
                        score = (target_cpa - cpa) / target_cpa * 100
                    elif total_cost > 0:
                        # Spent money but no conversions = worst score
                        score = -100.0
                        cpa = float('inf')
                    else:
                        # No activity — neutral
                        score = 0.0
                        cpa = 0.0

                    scores[window_name] = score
                    cpas[window_name] = cpa

                final_score = (scores['7d'] * w7) + (scores['14d'] * w14) + (scores['30d'] * w30)

                camp_result = {
                    **camp,
                    'score': final_score,
                    'score_7d': scores['7d'], 'score_14d': scores['14d'], 'score_30d': scores['30d'],
                    'cpa_7d': cpas['7d'], 'cpa_14d': cpas['14d'], 'cpa_30d': cpas['30d'],
                    'cost_30d': sum(s['metrics'].get('cost', 0) for s in windows['30d']),
                    'conversions_30d': sum(s['metrics'].get('conversions', 0) for s in windows['30d']),
                }
            else:  # ecommerce_roas
                scores = {}
                roass = {}
                for window_name, snaps in windows.items():
                    total_cost = sum(s['metrics'].get('cost', 0) for s in snaps)
                    total_value = sum(s['metrics'].get('conversion_value', 0) for s in snaps)

                    if total_cost > 0:
                        roas = total_value / total_cost
                        # Positive score = outperforming (ROAS above target)
                        score = (roas - target_roas) / target_roas * 100
                    else:
                        score = 0.0
                        roas = 0.0

                    scores[window_name] = score
                    roass[window_name] = roas

                final_score = (scores['7d'] * w7) + (scores['14d'] * w14) + (scores['30d'] * w30)

                camp_result = {
                    **camp,
                    'score': final_score,
                    'score_7d': scores['7d'], 'score_14d': scores['14d'], 'score_30d': scores['30d'],
                    'roas_7d': roass['7d'], 'roas_14d': roass['14d'], 'roas_30d': roass['30d'],
                    'cost_30d': sum(s['metrics'].get('cost', 0) for s in windows['30d']),
                }

            scored.append(camp_result)

        # Sort by score descending (best performer first)
        scored.sort(key=lambda c: c['score'], reverse=True)
        return scored

    def _evaluate_budget_allocation(self, scored_campaigns: list, roles: dict, date: str) -> int:
        """Evaluate and generate budget shift recommendations."""
        if len(scored_campaigns) < 2:
            return 0

        # Read settings
        allocation_mode = self.get_setting('budget_allocation_mode', 'automatic')
        max_move_pct = self.get_setting('max_overnight_budget_move_pct', 10)
        cooldown_hours = self.get_setting('budget_shift_cooldown_hours', 72)
        deviation_threshold = self.get_setting('deviation_threshold_pct', 10)

        # Calculate total daily budget from campaign data
        total_daily_budget = sum(
            c['metrics'].get('budget_amount', 0) for c in scored_campaigns
        )
        if total_daily_budget <= 0:
            logger.warning("  Total daily budget is 0, skipping budget allocation")
            return 0

        # Calculate average score
        avg_score = sum(c['score'] for c in scored_campaigns) / len(scored_campaigns)

        # Best performer = highest score, worst = lowest score
        best = scored_campaigns[0]
        worst = scored_campaigns[-1]

        # Check if score difference exceeds deviation threshold
        score_diff = best['score'] - worst['score']
        if score_diff < deviation_threshold:
            logger.info(f"  Score difference ({score_diff:.1f}) below threshold ({deviation_threshold}), no action needed")
            return 0

        # Check cooldowns
        if self.check_cooldown(self.CHECK_ID, best['entity_id']):
            logger.info(f"  Best performer '{best['name']}' is in cooldown, skipping")
            return 0
        if self.check_cooldown(self.CHECK_ID, worst['entity_id']):
            logger.info(f"  Worst performer '{worst['name']}' is in cooldown, skipping")
            return 0

        # Calculate current budget shares
        best_budget = best['metrics'].get('budget_amount', 0)
        worst_budget = worst['metrics'].get('budget_amount', 0)
        best_share = (best_budget / total_daily_budget * 100) if total_daily_budget > 0 else 0
        worst_share = (worst_budget / total_daily_budget * 100) if total_daily_budget > 0 else 0

        # Check budget bands
        best_role = roles.get(best['entity_id'])
        worst_role = roles.get(worst['entity_id'])

        if best_role:
            max_band = self.get_setting(f'budget_band_{best_role.lower()}_max_pct', 100)
            if best_share >= max_band:
                logger.info(f"  Best performer '{best['name']}' at max band ({best_share:.1f}% >= {max_band}%), skipping")
                return 0

        if worst_role:
            min_band = self.get_setting(f'budget_band_{worst_role.lower()}_min_pct', 0)
            if worst_share <= min_band:
                logger.info(f"  Worst performer '{worst['name']}' at min band ({worst_share:.1f}% <= {min_band}%), skipping")
                return 0

        # Calculate shift amount (capped at max overnight move)
        max_shift = total_daily_budget * (max_move_pct / 100)
        # Shift proportional to score difference, capped
        shift_amount = min(max_shift, worst_budget * 0.1)  # max 10% of underperformer budget
        shift_pct = (shift_amount / total_daily_budget * 100) if total_daily_budget > 0 else 0

        if shift_amount < 0.01:
            logger.info("  Calculated shift amount too small, skipping")
            return 0

        # Determine action category
        is_lead_gen = self.client['persona'] == 'lead_gen_cpa'
        metric_name = 'CPA' if is_lead_gen else 'ROAS'
        metric_val = best.get('cpa_30d', best.get('roas_30d', 'N/A'))

        if allocation_mode == 'manual':
            action_category = 'investigate'
        else:
            # Tightening (reducing underperformer) = act, loosening (increasing outperformer) = investigate
            # Budget shift is both — default to 'act' for automatic mode
            action_category = 'act'

        risk_level = 'low' if shift_pct <= 5 else 'medium'

        # Build decision tree
        decision_tree = {
            "check": "Account-level budget allocation (runs daily)",
            "signal": (f"Campaign '{best['name']}' {metric_name} is {best['score']:.1f}% "
                       f"{'below' if is_lead_gen and best['score'] > 0 else 'above'} target "
                       f"over weighted 7d/14d/30d blend"),
            "rule": (f"Budget shift of {shift_pct:.1f}% (£{shift_amount:.2f}/day) "
                     f"from '{worst['name']}' to '{best['name']}'. "
                     f"Within role bands and overnight move cap."),
            "cooldown": f"{cooldown_hours}hr cooldown after execution",
            "risk": (f"{'Low' if risk_level == 'low' else 'Medium'} — "
                     f"{'within normal optimization range' if risk_level == 'low' else 'larger shift, verify campaign health'}")
        }

        current_value = {
            best['name']: {'daily_budget': best_budget, 'share_pct': round(best_share, 1)},
            worst['name']: {'daily_budget': worst_budget, 'share_pct': round(worst_share, 1)},
        }

        proposed_value = {
            best['name']: {'daily_budget': round(best_budget + shift_amount, 2),
                           'share_pct': round((best_budget + shift_amount) / total_daily_budget * 100, 1)},
            worst['name']: {'daily_budget': round(worst_budget - shift_amount, 2),
                            'share_pct': round((worst_budget - shift_amount) / total_daily_budget * 100, 1)},
        }

        weekly_saving = shift_amount * 7 * (abs(best['score'] - worst['score']) / 100)
        estimated_impact = f"Estimated improvement: £{weekly_saving:.2f}/week based on {metric_name} differential"

        summary = (f"Shift {shift_pct:.1f}% of daily budget (£{shift_amount:.2f}) "
                   f"from '{worst['name']}' to '{best['name']}'")

        recommendation_text = (
            f"Campaign '{best['name']}' is outperforming with a score of {best['score']:.1f} "
            f"(30d {metric_name}: {metric_val}). "
            f"Campaign '{worst['name']}' is underperforming with a score of {worst['score']:.1f}. "
            f"Recommend shifting £{shift_amount:.2f}/day ({shift_pct:.1f}%) from underperformer to outperformer."
        )

        self.write_recommendation(
            check_id=self.CHECK_ID,
            entity_id=best['entity_id'],
            entity_name=best['name'],
            parent_entity_id=None,
            action_category=action_category,
            risk_level=risk_level,
            summary=summary,
            recommendation_text=recommendation_text,
            estimated_impact=estimated_impact,
            decision_tree=decision_tree,
            current_value=current_value,
            proposed_value=proposed_value,
        )

        logger.info(f"  Recommendation: {summary}")
        return 1
