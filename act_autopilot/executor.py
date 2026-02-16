"""
Execution engine for Google Ads campaign changes.
Handles budget, bid, keyword, ad, and Shopping modifications.

Supports:
- Campaign changes (budgets, bid targets)
- Keyword operations (add, pause, bid updates, negatives)
- Ad operations (pause, enable with CTR checks)
- Shopping operations (bid updates, product exclusions)
- Dry-run mode (simulation)
- Live mode (real API calls)
- Change logging with comprehensive metadata
- Constitution guardrail validation
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import duckdb
from act_autopilot.models import Recommendation
from act_autopilot.change_log import ChangeLog
from act_autopilot.logging_config import setup_logging
from act_autopilot.google_ads_api import (
    update_campaign_budget,
    update_campaign_bidding_strategy,
    validate_campaign_exists,
    add_keyword,
    pause_keyword,
    update_keyword_bid,
    add_negative_keyword,
    pause_ad,
    enable_ad,
    update_product_partition_bid,
    exclude_product,
    get_ad_group_keywords,
    get_ad_group_ads,
)

logger = setup_logging(__name__)


@dataclass
class ExecutionResult:
    """Result of executing a single recommendation."""

    success: bool
    message: str
    error: Optional[str] = None
    executed_at: Optional[datetime] = None
    api_response: Optional[Dict] = None


class Executor:
    """
    Executes campaign, keyword, ad, and Shopping changes with validation and logging.

    Supports two modes:
    - Dry-run (default): Simulates changes, no API calls
    - Live: Makes real Google Ads API calls

    All changes are validated against Constitution guardrails:
    - Campaign: 7-day cooldown, one-lever rule, ±15% max change
    - Keywords: 14-day cooldown, max 10 adds/day, max 20 negatives/day, ±20% bids, ≥30 clicks data
    - Ads: 7-day cooldown, max 5 pauses/day, min 2 active, CTR improvement check for re-enable
    - Shopping: 14-day cooldown, max 10 exclusions/day, ±20% bids, OOS protection
    """

    def __init__(
        self,
        customer_id: str,
        db_path: str = "warehouse.duckdb",
        google_ads_client=None,
    ):
        """
        Initialize executor.

        Args:
            customer_id: Google Ads customer ID (digits only)
            db_path: Path to DuckDB database
            google_ads_client: GoogleAdsClient instance (None for dry-run)
        """
        self.customer_id = customer_id
        self.db_path = db_path
        self.client = google_ads_client
        self.change_log = ChangeLog(db_path)

        mode = "DRY-RUN" if google_ads_client is None else "LIVE"
        logger.info(f"Executor initialized: customer_id={customer_id}, mode={mode}")

    def execute(
        self,
        recommendations: List[Recommendation],
        dry_run: bool = True,
        rule_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a list of recommendations.

        Args:
            recommendations: List of Recommendation objects
            dry_run: If True, simulate only. If False, make real API calls.
            rule_ids: Optional list of rule IDs to filter

        Returns:
            Summary dict with total, successful, failed counts and detailed results
        """
        logger.info(
            f"Starting execution: total_recommendations={len(recommendations)}, dry_run={dry_run}"
        )

        # Filter by rule_ids if provided
        if rule_ids:
            recommendations = [r for r in recommendations if r.rule_id in rule_ids]
            logger.info(f"Filtered by rule_ids: remaining={len(recommendations)}")

        # Filter to executable actions
        executable_types = [
            # Campaign
            "budget_increase",
            "budget_decrease",
            "bid_target_increase",
            "bid_target_decrease",
            # Keywords
            "add_keyword",
            "pause_keyword",
            "update_keyword_bid",
            "add_negative_keyword",
            # Ads
            "pause_ad",
            "enable_ad",
            # Shopping
            "update_product_bid",
            "exclude_product",
        ]
        executable_recs = [
            r for r in recommendations if r.action_type in executable_types
        ]

        logger.info(f"Executable recommendations: {len(executable_recs)}")

        results = []
        successful = 0
        failed = 0

        for rec in executable_recs:
            # Q4 answer: A - Log error, skip recommendation, continue with others
            try:
                result = self._execute_one(rec, dry_run)
                results.append(
                    {
                        "rule_id": rec.rule_id,
                        "entity_id": rec.entity_id,
                        "entity_name": rec.campaign_name or rec.evidence.get("keyword_text") or "Unknown",
                        "action_type": rec.action_type,
                        "success": result.success,
                        "message": result.message,
                        "error": result.error,
                    }
                )

                if result.success:
                    successful += 1
                else:
                    failed += 1

            except Exception as e:
                # Q4: Log and continue
                error_msg = str(e)
                logger.error(f"Error executing {rec.rule_id}: {error_msg}")
                results.append(
                    {
                        "rule_id": rec.rule_id,
                        "entity_id": rec.entity_id,
                        "entity_name": rec.campaign_name or rec.evidence.get("keyword_text") or "Unknown",
                        "action_type": rec.action_type,
                        "success": False,
                        "message": f"Execution error: {error_msg}",
                        "error": error_msg,
                    }
                )
                failed += 1

        summary = {
            "total": len(executable_recs),
            "successful": successful,
            "failed": failed,
            "dry_run": dry_run,
            "results": results,
        }

        logger.info(f"Execution complete: successful={successful}, failed={failed}")
        return summary

    def _execute_one(self, rec: Recommendation, dry_run: bool) -> ExecutionResult:
        """Execute a single recommendation."""
        logger.info(f"Executing {rec.rule_id} for {rec.entity_id}")

        # Route to appropriate handler based on action type
        if rec.action_type in ["budget_increase", "budget_decrease"]:
            return self._execute_budget_change(rec, dry_run)
        elif rec.action_type in ["bid_target_increase", "bid_target_decrease"]:
            return self._execute_bid_change(rec, dry_run)
        elif rec.action_type == "add_keyword":
            return self._execute_keyword_add(rec, dry_run)
        elif rec.action_type == "pause_keyword":
            return self._execute_keyword_pause(rec, dry_run)
        elif rec.action_type == "update_keyword_bid":
            return self._execute_keyword_bid(rec, dry_run)
        elif rec.action_type == "add_negative_keyword":
            return self._execute_negative_keyword(rec, dry_run)
        elif rec.action_type == "pause_ad":
            return self._execute_ad_pause(rec, dry_run)
        elif rec.action_type == "enable_ad":
            return self._execute_ad_enable(rec, dry_run)
        elif rec.action_type == "update_product_bid":
            return self._execute_shopping_bid(rec, dry_run)
        elif rec.action_type == "exclude_product":
            return self._execute_product_exclude(rec, dry_run)
        else:
            return ExecutionResult(
                success=False,
                message=f"Unsupported action type: {rec.action_type}",
                error=f"Unsupported action type: {rec.action_type}",
            )

    # ========================================================================
    # CAMPAIGN EXECUTION (EXISTING)
    # ========================================================================

    def _execute_budget_change(
        self, rec: Recommendation, dry_run: bool
    ) -> ExecutionResult:
        """Execute budget change with validation."""
        # Validate
        validation = self._validate_campaign_action(rec, "budget")
        if not validation["valid"]:
            logger.warning(f"Validation failed: {validation['reason']}")
            return ExecutionResult(
                success=False,
                message=f"Validation failed: {validation['reason']}",
                error=validation["reason"],
            )

        if dry_run:
            return self._execute_budget_change_dryrun(rec)
        else:
            return self._execute_budget_change_live(rec)

    def _execute_bid_change(
        self, rec: Recommendation, dry_run: bool
    ) -> ExecutionResult:
        """Execute bid change with validation."""
        # Validate
        validation = self._validate_campaign_action(rec, "bid")
        if not validation["valid"]:
            logger.warning(f"Validation failed: {validation['reason']}")
            return ExecutionResult(
                success=False,
                message=f"Validation failed: {validation['reason']}",
                error=validation["reason"],
            )

        if dry_run:
            return self._execute_bid_change_dryrun(rec)
        else:
            return self._execute_bid_change_live(rec)

    def _validate_campaign_action(
        self, rec: Recommendation, lever: str
    ) -> Dict[str, Any]:
        """Validate campaign action (existing logic)."""
        # Check cooldown (same lever)
        cooldown_violated = self.change_log.check_cooldown(
            customer_id=self.customer_id,
            campaign_id=rec.entity_id,
            lever=lever,
            cooldown_days=7,
        )
        if cooldown_violated:
            return {
                "valid": False,
                "reason": f"Cooldown violation - {lever} changed <7 days ago",
            }

        # Check one-lever rule
        opposite_lever = "bid" if lever == "budget" else "budget"
        one_lever_violated = self.change_log.check_one_lever(
            customer_id=self.customer_id,
            campaign_id=rec.entity_id,
            proposed_lever=lever,
            cooldown_days=7,
        )
        if one_lever_violated:
            return {
                "valid": False,
                "reason": f"One-lever violation - {opposite_lever} changed <7 days ago",
            }

        # Check values exist
        if rec.current_value is None or rec.recommended_value is None:
            return {
                "valid": False,
                "reason": "Missing current_value or recommended_value",
            }

        # Check magnitude (max 15%)
        abs_change = abs(rec.change_pct) if rec.change_pct else 0.0
        if abs_change > 0.15:
            return {
                "valid": False,
                "reason": f"Change magnitude too large: {abs_change:.1%}",
            }

        return {"valid": True, "reason": None}

    def _execute_budget_change_dryrun(self, rec: Recommendation) -> ExecutionResult:
        """Simulate budget change (dry-run)."""
        current = rec.current_value or 0
        proposed = rec.recommended_value or 0
        change_pct = rec.change_pct or 0

        message = f"""DRY-RUN: Would execute {rec.rule_id}
  Campaign: {rec.campaign_name or 'Unknown'} ({rec.entity_id})
  Current Budget: £{current:.2f}/day
  Proposed Budget: £{proposed:.2f}/day
  Change: {change_pct * 100:+.1f}%
  Validation: PASS
  API call: SIMULATED
  Log: Would save to analytics.change_log"""

        logger.info(f"DRY-RUN budget change: {rec.rule_id} campaign={rec.entity_id}")
        return ExecutionResult(success=True, message=message)

    def _execute_bid_change_dryrun(self, rec: Recommendation) -> ExecutionResult:
        """Simulate bid change (dry-run)."""
        bid_type = self._get_bid_type_from_recommendation(rec)
        current = rec.current_value or 0
        proposed = rec.recommended_value or 0
        change_pct = rec.change_pct or 0

        message = f"""DRY-RUN: Would execute {rec.rule_id}
  Campaign: {rec.campaign_name or 'Unknown'} ({rec.entity_id})
  Bid Type: {bid_type}
  Current: {current:.2f}
  Proposed: {proposed:.2f}
  Change: {change_pct * 100:+.1f}%
  Validation: PASS
  API call: SIMULATED
  Log: Would save to analytics.change_log"""

        logger.info(f"DRY-RUN bid change: {rec.rule_id} campaign={rec.entity_id}")
        return ExecutionResult(success=True, message=message)

    def _execute_budget_change_live(self, rec: Recommendation) -> ExecutionResult:
        """Execute real budget change via Google Ads API."""
        if not self.client:
            return ExecutionResult(
                success=False,
                message="No Google Ads client configured",
                error="Cannot execute live without Google Ads API client",
            )

        try:
            if not validate_campaign_exists(
                self.client, self.customer_id, rec.entity_id
            ):
                return ExecutionResult(
                    success=False,
                    message=f"Campaign {rec.entity_id} not found",
                    error=f"Campaign {rec.entity_id} does not exist",
                )

            new_budget_micros = int((rec.recommended_value or 0) * 1_000_000)

            response = update_campaign_budget(
                client=self.client,
                customer_id=self.customer_id,
                campaign_id=rec.entity_id,
                new_budget_micros=new_budget_micros,
            )

            # Log the change
            self._log_campaign_change(rec, "budget")

            message = f"""LIVE: Executed {rec.rule_id}
  Campaign: {rec.campaign_name or 'Unknown'} ({rec.entity_id})
  Old Budget: £{rec.current_value:.2f}/day
  New Budget: £{rec.recommended_value:.2f}/day
  Change: {(rec.change_pct or 0) * 100:+.1f}%
  API Response: {response['message']}
  Status: SUCCESS"""

            logger.info(
                f"LIVE budget change successful: {rec.rule_id} campaign={rec.entity_id}"
            )

            return ExecutionResult(
                success=True,
                message=message,
                executed_at=datetime.now(),
                api_response=response,
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"LIVE budget change failed: {error_msg}")
            return ExecutionResult(
                success=False, message=f"API call failed: {error_msg}", error=error_msg
            )

    def _execute_bid_change_live(self, rec: Recommendation) -> ExecutionResult:
        """Execute real bid change via Google Ads API."""
        if not self.client:
            return ExecutionResult(
                success=False,
                message="No Google Ads client configured",
                error="Cannot execute live without Google Ads API client",
            )

        try:
            if not validate_campaign_exists(
                self.client, self.customer_id, rec.entity_id
            ):
                return ExecutionResult(
                    success=False,
                    message=f"Campaign {rec.entity_id} not found",
                    error=f"Campaign {rec.entity_id} does not exist",
                )

            bid_type = self._get_bid_type_from_recommendation(rec)

            response = update_campaign_bidding_strategy(
                client=self.client,
                customer_id=self.customer_id,
                campaign_id=rec.entity_id,
                new_target_value=rec.recommended_value or 0,
                bid_type=bid_type,
            )

            # Log the change
            self._log_campaign_change(rec, "bid")

            message = f"""LIVE: Executed {rec.rule_id}
  Campaign: {rec.campaign_name or 'Unknown'} ({rec.entity_id})
  Bid Type: {bid_type}
  Old Target: {rec.current_value:.2f}
  New Target: {rec.recommended_value:.2f}
  Change: {(rec.change_pct or 0) * 100:+.1f}%
  API Response: {response['message']}
  Status: SUCCESS"""

            logger.info(
                f"LIVE bid change successful: {rec.rule_id} campaign={rec.entity_id}"
            )

            return ExecutionResult(
                success=True,
                message=message,
                executed_at=datetime.now(),
                api_response=response,
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"LIVE bid change failed: {error_msg}")
            return ExecutionResult(
                success=False, message=f"API call failed: {error_msg}", error=error_msg
            )

    # ========================================================================
    # KEYWORD EXECUTION (NEW - CHAT 13)
    # ========================================================================

    def _execute_keyword_add(
        self, rec: Recommendation, dry_run: bool
    ) -> ExecutionResult:
        """Execute keyword addition with validation."""
        # Validate
        validation = self._validate_keyword_action(rec, "add")
        if not validation["valid"]:
            logger.warning(f"Validation failed: {validation['reason']}")
            return ExecutionResult(
                success=False,
                message=f"Validation failed: {validation['reason']}",
                error=validation["reason"],
            )

        # Extract parameters from recommendation
        ad_group_id = rec.evidence.get("ad_group_id")
        keyword_text = rec.evidence.get("keyword_text")
        match_type = rec.evidence.get("match_type", "EXACT")
        bid_micros = rec.evidence.get("bid_micros")  # Q1: Required

        if not all([ad_group_id, keyword_text, bid_micros]):
            return ExecutionResult(
                success=False,
                message="Missing required parameters: ad_group_id, keyword_text, or bid_micros",
                error="Missing required parameters",
            )

        try:
            response = add_keyword(
                client=self.client,
                customer_id=self.customer_id,
                ad_group_id=str(ad_group_id),
                keyword_text=keyword_text,
                match_type=match_type,
                bid_micros=int(bid_micros),
                dry_run=dry_run,
            )

            if not dry_run and response["status"] == "success":
                self._log_keyword_change(rec, "add_keyword", response)

            message = f"""{'DRY-RUN' if dry_run else 'LIVE'}: {rec.rule_id}
  Keyword: '{keyword_text}' ({match_type})
  Ad Group: {ad_group_id}
  Initial Bid: £{bid_micros / 1_000_000:.2f}
  Status: {response['status'].upper()}"""

            return ExecutionResult(
                success=True, message=message, api_response=response
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Keyword add failed: {error_msg}")
            return ExecutionResult(
                success=False, message=f"Failed: {error_msg}", error=error_msg
            )

    def _execute_keyword_pause(
        self, rec: Recommendation, dry_run: bool
    ) -> ExecutionResult:
        """Execute keyword pause with validation."""
        # Validate
        validation = self._validate_keyword_action(rec, "pause")
        if not validation["valid"]:
            logger.warning(f"Validation failed: {validation['reason']}")
            return ExecutionResult(
                success=False,
                message=f"Validation failed: {validation['reason']}",
                error=validation["reason"],
            )

        ad_group_id = rec.evidence.get("ad_group_id")
        keyword_id = rec.entity_id

        if not all([ad_group_id, keyword_id]):
            return ExecutionResult(
                success=False,
                message="Missing required parameters: ad_group_id or keyword_id",
                error="Missing required parameters",
            )

        try:
            response = pause_keyword(
                client=self.client,
                customer_id=self.customer_id,
                ad_group_id=str(ad_group_id),
                keyword_id=str(keyword_id),
                dry_run=dry_run,
            )

            if not dry_run and response["status"] == "success":
                self._log_keyword_change(rec, "pause_keyword", response)

            message = f"""{'DRY-RUN' if dry_run else 'LIVE'}: {rec.rule_id}
  Keyword: '{rec.evidence.get("keyword_text") or keyword_id}'
  Ad Group: {ad_group_id}
  Action: PAUSE
  Status: {response['status'].upper()}"""

            return ExecutionResult(
                success=True, message=message, api_response=response
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Keyword pause failed: {error_msg}")
            return ExecutionResult(
                success=False, message=f"Failed: {error_msg}", error=error_msg
            )

    def _execute_keyword_bid(
        self, rec: Recommendation, dry_run: bool
    ) -> ExecutionResult:
        """Execute keyword bid update with validation."""
        # Validate
        validation = self._validate_keyword_action(rec, "bid")
        if not validation["valid"]:
            logger.warning(f"Validation failed: {validation['reason']}")
            return ExecutionResult(
                success=False,
                message=f"Validation failed: {validation['reason']}",
                error=validation["reason"],
            )

        ad_group_id = rec.evidence.get("ad_group_id")
        keyword_id = rec.entity_id
        new_bid_micros = int((rec.recommended_value or 0) * 1_000_000)

        if not all([ad_group_id, keyword_id, new_bid_micros]):
            return ExecutionResult(
                success=False,
                message="Missing required parameters",
                error="Missing required parameters",
            )

        try:
            response = update_keyword_bid(
                client=self.client,
                customer_id=self.customer_id,
                ad_group_id=str(ad_group_id),
                keyword_id=str(keyword_id),
                new_bid_micros=new_bid_micros,
                dry_run=dry_run,
            )

            if not dry_run and response["status"] == "success":
                self._log_keyword_change(rec, "update_keyword_bid", response)

            message = f"""{'DRY-RUN' if dry_run else 'LIVE'}: {rec.rule_id}
  Keyword: '{rec.evidence.get("keyword_text") or keyword_id}'
  Old Bid: £{rec.current_value:.2f}
  New Bid: £{rec.recommended_value:.2f}
  Change: {(rec.change_pct or 0) * 100:+.1f}%
  Status: {response['status'].upper()}"""

            return ExecutionResult(
                success=True, message=message, api_response=response
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Keyword bid update failed: {error_msg}")
            return ExecutionResult(
                success=False, message=f"Failed: {error_msg}", error=error_msg
            )

    def _execute_negative_keyword(
        self, rec: Recommendation, dry_run: bool
    ) -> ExecutionResult:
        """Execute negative keyword addition with validation."""
        # Validate
        validation = self._validate_keyword_action(rec, "negative")
        if not validation["valid"]:
            logger.warning(f"Validation failed: {validation['reason']}")
            return ExecutionResult(
                success=False,
                message=f"Validation failed: {validation['reason']}",
                error=validation["reason"],
            )

        campaign_id = rec.evidence.get("campaign_id")
        keyword_text = rec.evidence.get("keyword_text")
        match_type = rec.evidence.get("match_type", "EXACT")

        if not all([campaign_id, keyword_text]):
            return ExecutionResult(
                success=False,
                message="Missing required parameters: campaign_id or keyword_text",
                error="Missing required parameters",
            )

        try:
            response = add_negative_keyword(
                client=self.client,
                customer_id=self.customer_id,
                campaign_id=str(campaign_id),
                keyword_text=keyword_text,
                match_type=match_type,
                dry_run=dry_run,
            )

            if not dry_run and response["status"] == "success":
                self._log_keyword_change(rec, "add_negative_keyword", response)

            message = f"""{'DRY-RUN' if dry_run else 'LIVE'}: {rec.rule_id}
  Negative Keyword: '{keyword_text}' ({match_type})
  Campaign: {campaign_id}
  Status: {response['status'].upper()}"""

            return ExecutionResult(
                success=True, message=message, api_response=response
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Negative keyword add failed: {error_msg}")
            return ExecutionResult(
                success=False, message=f"Failed: {error_msg}", error=error_msg
            )

    def _validate_keyword_action(
        self, rec: Recommendation, action: str
    ) -> Dict[str, Any]:
        """Validate keyword action against Constitution guardrails."""
        conn = duckdb.connect(self.db_path, read_only=True)

        try:
            # Check 1: Daily add limit (max 10 keywords/day per campaign)
            if action == "add":
                campaign_id = rec.evidence.get("campaign_id")
                today = datetime.now().date()

                count = conn.execute(
                    """
                    SELECT COUNT(*) FROM analytics.change_log
                    WHERE customer_id = ?
                      AND campaign_id = ?
                      AND action_type = 'add_keyword'
                      AND CAST(executed_at AS DATE) = ?
                """,
                    [self.customer_id, str(campaign_id), today],
                ).fetchone()[0]

                if count >= 10:
                    return {
                        "valid": False,
                        "reason": f"Daily keyword add limit reached (10/day): {count} already added today",
                    }

            # Check 2: Daily negative limit (max 20 negatives/day per campaign)
            if action == "negative":
                campaign_id = rec.evidence.get("campaign_id")
                today = datetime.now().date()

                count = conn.execute(
                    """
                    SELECT COUNT(*) FROM analytics.change_log
                    WHERE customer_id = ?
                      AND campaign_id = ?
                      AND action_type = 'add_negative_keyword'
                      AND CAST(executed_at AS DATE) = ?
                """,
                    [self.customer_id, str(campaign_id), today],
                ).fetchone()[0]

                if count >= 20:
                    return {
                        "valid": False,
                        "reason": f"Daily negative keyword limit reached (20/day): {count} already added today",
                    }

            # Check 3: Cooldown (14 days for same keyword)
            if action in ["pause", "bid"]:
                keyword_id = rec.entity_id
                cooldown_date = (datetime.now() - timedelta(days=14)).date()

                last_change = conn.execute(
                    """
                    SELECT MAX(executed_at) FROM analytics.change_log
                    WHERE customer_id = ?
                      AND entity_id = ?
                      AND entity_type = 'keyword'
                      AND CAST(executed_at AS DATE) >= ?
                """,
                    [self.customer_id, str(keyword_id), cooldown_date],
                ).fetchone()[0]

                if last_change:
                    return {
                        "valid": False,
                        "reason": f"Cooldown violation - keyword changed within 14 days (last: {last_change})",
                    }

            # Check 4: Data requirement (≥30 clicks in last 30 days before pause)
            if action == "pause":
                clicks = rec.evidence.get("clicks_30d", 0)
                if clicks < 30:
                    return {
                        "valid": False,
                        "reason": f"Insufficient data - need ≥30 clicks, found {clicks}",
                    }

            # Check 5: Bid change magnitude (±20% max)
            if action == "bid":
                abs_change = abs(rec.change_pct) if rec.change_pct else 0.0
                if abs_change > 0.20:
                    return {
                        "valid": False,
                        "reason": f"Bid change too large: {abs_change:.1%} (max ±20%)",
                    }

            return {"valid": True, "reason": None}

        finally:
            conn.close()

    # ========================================================================
    # AD EXECUTION (NEW - CHAT 13)
    # ========================================================================

    def _execute_ad_pause(self, rec: Recommendation, dry_run: bool) -> ExecutionResult:
        """Execute ad pause with validation."""
        # Validate
        validation = self._validate_ad_action(rec, "pause")
        if not validation["valid"]:
            logger.warning(f"Validation failed: {validation['reason']}")
            return ExecutionResult(
                success=False,
                message=f"Validation failed: {validation['reason']}",
                error=validation["reason"],
            )

        ad_group_id = rec.evidence.get("ad_group_id")
        ad_id = rec.entity_id

        if not all([ad_group_id, ad_id]):
            return ExecutionResult(
                success=False,
                message="Missing required parameters: ad_group_id or ad_id",
                error="Missing required parameters",
            )

        try:
            response = pause_ad(
                client=self.client,
                customer_id=self.customer_id,
                ad_group_id=str(ad_group_id),
                ad_id=str(ad_id),
                dry_run=dry_run,
            )

            if not dry_run and response["status"] == "success":
                self._log_ad_change(rec, "pause_ad", response)

            message = f"""{'DRY-RUN' if dry_run else 'LIVE'}: {rec.rule_id}
  Ad: {ad_id}
  Ad Group: {ad_group_id}
  Action: PAUSE
  Status: {response['status'].upper()}"""

            return ExecutionResult(
                success=True, message=message, api_response=response
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Ad pause failed: {error_msg}")
            return ExecutionResult(
                success=False, message=f"Failed: {error_msg}", error=error_msg
            )

    def _execute_ad_enable(
        self, rec: Recommendation, dry_run: bool
    ) -> ExecutionResult:
        """Execute ad re-enable with validation (Q2: CTR improvement check)."""
        # Validate (includes CTR improvement check per Q2: A)
        validation = self._validate_ad_action(rec, "enable")
        if not validation["valid"]:
            logger.warning(f"Validation failed: {validation['reason']}")
            return ExecutionResult(
                success=False,
                message=f"Validation failed: {validation['reason']}",
                error=validation["reason"],
            )

        ad_group_id = rec.evidence.get("ad_group_id")
        ad_id = rec.entity_id

        if not all([ad_group_id, ad_id]):
            return ExecutionResult(
                success=False,
                message="Missing required parameters: ad_group_id or ad_id",
                error="Missing required parameters",
            )

        try:
            response = enable_ad(
                client=self.client,
                customer_id=self.customer_id,
                ad_group_id=str(ad_group_id),
                ad_id=str(ad_id),
                dry_run=dry_run,
            )

            if not dry_run and response["status"] == "success":
                self._log_ad_change(rec, "enable_ad", response)

            message = f"""{'DRY-RUN' if dry_run else 'LIVE'}: {rec.rule_id}
  Ad: {ad_id}
  Ad Group: {ad_group_id}
  Action: ENABLE
  CTR Check: PASSED
  Status: {response['status'].upper()}"""

            return ExecutionResult(
                success=True, message=message, api_response=response
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Ad enable failed: {error_msg}")
            return ExecutionResult(
                success=False, message=f"Failed: {error_msg}", error=error_msg
            )

    def _validate_ad_action(self, rec: Recommendation, action: str) -> Dict[str, Any]:
        """Validate ad action against Constitution guardrails."""
        conn = duckdb.connect(self.db_path, read_only=True)

        try:
            ad_group_id = rec.evidence.get("ad_group_id")

            # Check 1: Daily pause limit (max 5 pauses/day per ad group)
            if action == "pause":
                today = datetime.now().date()

                count = conn.execute(
                    """
                    SELECT COUNT(*) FROM analytics.change_log
                    WHERE customer_id = ?
                      AND ad_group_id = ?
                      AND action_type = 'pause_ad'
                      AND CAST(executed_at AS DATE) = ?
                """,
                    [self.customer_id, str(ad_group_id), today],
                ).fetchone()[0]

                if count >= 5:
                    return {
                        "valid": False,
                        "reason": f"Daily ad pause limit reached (5/day): {count} already paused today",
                    }

                # Check minimum active ads (never pause if it would leave <2 active)
                active_ads = rec.evidence.get("active_ads_count", 0)
                if active_ads <= 2:
                    return {
                        "valid": False,
                        "reason": f"Cannot pause - would leave only {active_ads - 1} active ads (min 2 required)",
                    }

            # Check 2: Cooldown (7 days for same ad)
            if action in ["pause", "enable"]:
                ad_id = rec.entity_id
                cooldown_date = (datetime.now() - timedelta(days=7)).date()

                last_change = conn.execute(
                    """
                    SELECT MAX(executed_at) FROM analytics.change_log
                    WHERE customer_id = ?
                      AND entity_id = ?
                      AND entity_type = 'ad'
                      AND CAST(executed_at AS DATE) >= ?
                """,
                    [self.customer_id, str(ad_id), cooldown_date],
                ).fetchone()[0]

                if last_change:
                    return {
                        "valid": False,
                        "reason": f"Cooldown violation - ad changed within 7 days (last: {last_change})",
                    }

            # Check 3: Data requirements
            if action == "pause":
                # CTR-based pause: ≥1000 impressions (30d)
                impressions = rec.evidence.get("impressions_30d", 0)
                if impressions < 1000:
                    return {
                        "valid": False,
                        "reason": f"Insufficient data for CTR-based pause - need ≥1000 impressions, found {impressions}",
                    }

                # CVR-based pause: ≥100 clicks (30d)
                clicks = rec.evidence.get("clicks_30d", 0)
                if clicks < 100 and "cvr" in rec.rule_id.lower():
                    return {
                        "valid": False,
                        "reason": f"Insufficient data for CVR-based pause - need ≥100 clicks, found {clicks}",
                    }

            # Check 4: Q2 answer (A) - CTR improvement check for re-enable
            if action == "enable":
                # Verify ad group CTR improved ≥20% since pause
                ctr_at_pause = rec.evidence.get("ctr_at_pause", 0)
                current_ctr = rec.evidence.get("current_ad_group_ctr", 0)

                if ctr_at_pause > 0:
                    improvement = (current_ctr - ctr_at_pause) / ctr_at_pause
                    if improvement < 0.20:
                        return {
                            "valid": False,
                            "reason": f"CTR improvement insufficient - need ≥20%, found {improvement:.1%}",
                        }

            return {"valid": True, "reason": None}

        finally:
            conn.close()

    # ========================================================================
    # SHOPPING EXECUTION (NEW - CHAT 13)
    # ========================================================================

    def _execute_shopping_bid(
        self, rec: Recommendation, dry_run: bool
    ) -> ExecutionResult:
        """Execute Shopping bid update with validation."""
        # Validate
        validation = self._validate_shopping_action(rec, "bid")
        if not validation["valid"]:
            logger.warning(f"Validation failed: {validation['reason']}")
            return ExecutionResult(
                success=False,
                message=f"Validation failed: {validation['reason']}",
                error=validation["reason"],
            )

        ad_group_id = rec.evidence.get("ad_group_id")
        partition_id = rec.entity_id
        new_bid_micros = int((rec.recommended_value or 0) * 1_000_000)

        if not all([ad_group_id, partition_id, new_bid_micros]):
            return ExecutionResult(
                success=False,
                message="Missing required parameters",
                error="Missing required parameters",
            )

        try:
            response = update_product_partition_bid(
                client=self.client,
                customer_id=self.customer_id,
                ad_group_id=str(ad_group_id),
                partition_id=str(partition_id),
                new_bid_micros=new_bid_micros,
                dry_run=dry_run,
            )

            if not dry_run and response["status"] == "success":
                self._log_shopping_change(rec, "update_product_bid", response)

            message = f"""{'DRY-RUN' if dry_run else 'LIVE'}: {rec.rule_id}
  Product Partition: {partition_id}
  Old Bid: £{rec.current_value:.2f}
  New Bid: £{rec.recommended_value:.2f}
  Change: {(rec.change_pct or 0) * 100:+.1f}%
  Status: {response['status'].upper()}"""

            return ExecutionResult(
                success=True, message=message, api_response=response
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Shopping bid update failed: {error_msg}")
            return ExecutionResult(
                success=False, message=f"Failed: {error_msg}", error=error_msg
            )

    def _execute_product_exclude(
        self, rec: Recommendation, dry_run: bool
    ) -> ExecutionResult:
        """Execute product exclusion with validation (Q3: campaign-level)."""
        # Validate
        validation = self._validate_shopping_action(rec, "exclude")
        if not validation["valid"]:
            logger.warning(f"Validation failed: {validation['reason']}")
            return ExecutionResult(
                success=False,
                message=f"Validation failed: {validation['reason']}",
                error=validation["reason"],
            )

        campaign_id = rec.evidence.get("campaign_id")
        product_id = rec.evidence.get("product_id")

        if not all([campaign_id, product_id]):
            return ExecutionResult(
                success=False,
                message="Missing required parameters: campaign_id or product_id",
                error="Missing required parameters",
            )

        try:
            response = exclude_product(
                client=self.client,
                customer_id=self.customer_id,
                campaign_id=str(campaign_id),
                product_id=str(product_id),
                dry_run=dry_run,
            )

            if not dry_run and response["status"] == "success":
                self._log_shopping_change(rec, "exclude_product", response)

            message = f"""{'DRY-RUN' if dry_run else 'LIVE'}: {rec.rule_id}
  Product: {product_id}
  Campaign: {campaign_id}
  Action: EXCLUDE (campaign-level)
  Status: {response['status'].upper()}"""

            return ExecutionResult(
                success=True, message=message, api_response=response
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Product exclusion failed: {error_msg}")
            return ExecutionResult(
                success=False, message=f"Failed: {error_msg}", error=error_msg
            )

    def _validate_shopping_action(
        self, rec: Recommendation, action: str
    ) -> Dict[str, Any]:
        """Validate Shopping action against Constitution guardrails."""
        conn = duckdb.connect(self.db_path, read_only=True)

        try:
            # Check 1: Daily exclusion limit (max 10/day per campaign)
            if action == "exclude":
                campaign_id = rec.evidence.get("campaign_id")
                today = datetime.now().date()

                count = conn.execute(
                    """
                    SELECT COUNT(*) FROM analytics.change_log
                    WHERE customer_id = ?
                      AND campaign_id = ?
                      AND action_type = 'exclude_product'
                      AND CAST(executed_at AS DATE) = ?
                """,
                    [self.customer_id, str(campaign_id), today],
                ).fetchone()[0]

                if count >= 10:
                    return {
                        "valid": False,
                        "reason": f"Daily product exclusion limit reached (10/day): {count} already excluded today",
                    }

            # Check 2: Cooldown (14 days for same product)
            if action in ["bid", "exclude"]:
                product_id = rec.entity_id or rec.evidence.get("product_id")
                cooldown_date = (datetime.now() - timedelta(days=14)).date()

                last_change = conn.execute(
                    """
                    SELECT MAX(executed_at) FROM analytics.change_log
                    WHERE customer_id = ?
                      AND entity_id = ?
                      AND entity_type = 'product'
                      AND CAST(executed_at AS DATE) >= ?
                """,
                    [self.customer_id, str(product_id), cooldown_date],
                ).fetchone()[0]

                if last_change:
                    return {
                        "valid": False,
                        "reason": f"Cooldown violation - product changed within 14 days (last: {last_change})",
                    }

            # Check 3: Out-of-stock protection
            is_out_of_stock = rec.evidence.get("out_of_stock", False)
            if is_out_of_stock:
                return {
                    "valid": False,
                    "reason": "Cannot modify out-of-stock product - fix feed first",
                }

            # Check 4: Feed quality protection
            feed_quality_issue = rec.evidence.get("feed_quality_issue", False)
            if action == "exclude" and feed_quality_issue:
                return {
                    "valid": False,
                    "reason": "Cannot exclude product with feed quality issues - fix feed first",
                }

            # Check 5: Bid change magnitude (±20% max)
            if action == "bid":
                abs_change = abs(rec.change_pct) if rec.change_pct else 0.0
                if abs_change > 0.20:
                    return {
                        "valid": False,
                        "reason": f"Bid change too large: {abs_change:.1%} (max ±20%)",
                    }

            # Check 6: Never exclude if only item in category
            if action == "exclude":
                is_only_in_category = rec.evidence.get("only_in_category", False)
                if is_only_in_category:
                    return {
                        "valid": False,
                        "reason": "Cannot exclude - only product in category",
                    }

            return {"valid": True, "reason": None}

        finally:
            conn.close()

    # ========================================================================
    # LOGGING (UPDATED FOR CHAT 13)
    # ========================================================================

    def _log_campaign_change(self, rec: Recommendation, lever: str) -> None:
        """Log campaign change to database."""
        self.change_log.log_change(
            customer_id=self.customer_id,
            campaign_id=rec.entity_id,
            change_date=datetime.now().date(),
            lever=lever,
            old_value=rec.current_value or 0,
            new_value=rec.recommended_value or 0,
            rule_id=rec.rule_id,
            risk_tier=rec.risk_tier,
            change_pct=rec.change_pct,
            approved_by="system",
            executed_at=datetime.now(),
            # New columns
            action_type=rec.action_type,
            entity_type="campaign",
            entity_id=rec.entity_id,
            metadata=self._build_metadata(rec),
        )
        logger.info(f"Logged campaign change: {rec.rule_id}")

    def _log_keyword_change(
        self, rec: Recommendation, action_type: str, api_response: dict
    ) -> None:
        """Log keyword change to database."""
        conn = duckdb.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT INTO analytics.change_log (
                    customer_id, campaign_id, change_date, lever,
                    old_value, new_value, rule_id, risk_tier, change_pct,
                    approved_by, executed_at,
                    action_type, entity_type, entity_id,
                    match_type, keyword_text, ad_group_id, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                [
                    self.customer_id,
                    rec.evidence.get("campaign_id"),
                    datetime.now().date(),
                    "keyword",
                    rec.current_value or 0,
                    rec.recommended_value or 0,
                    rec.rule_id,
                    rec.risk_tier,
                    rec.change_pct,
                    "system",
                    datetime.now(),
                    action_type,
                    "keyword",
                    api_response.get("keyword_id") or rec.entity_id,
                    rec.evidence.get("match_type"),
                    rec.evidence.get("keyword_text"),
                    rec.evidence.get("ad_group_id"),
                    self._build_metadata(rec, api_response),
                ],
            )
            conn.commit()
            logger.info(f"Logged keyword change: {action_type}")
        finally:
            conn.close()

    def _log_ad_change(
        self, rec: Recommendation, action_type: str, api_response: dict
    ) -> None:
        """Log ad change to database."""
        conn = duckdb.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT INTO analytics.change_log (
                    customer_id, campaign_id, change_date, lever,
                    old_value, new_value, rule_id, risk_tier, change_pct,
                    approved_by, executed_at,
                    action_type, entity_type, entity_id,
                    ad_group_id, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                [
                    self.customer_id,
                    rec.evidence.get("campaign_id"),
                    datetime.now().date(),
                    "ad",
                    rec.current_value or 0,
                    rec.recommended_value or 0,
                    rec.rule_id,
                    rec.risk_tier,
                    rec.change_pct,
                    "system",
                    datetime.now(),
                    action_type,
                    "ad",
                    rec.entity_id,
                    rec.evidence.get("ad_group_id"),
                    self._build_metadata(rec, api_response),
                ],
            )
            conn.commit()
            logger.info(f"Logged ad change: {action_type}")
        finally:
            conn.close()

    def _log_shopping_change(
        self, rec: Recommendation, action_type: str, api_response: dict
    ) -> None:
        """Log Shopping change to database."""
        conn = duckdb.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT INTO analytics.change_log (
                    customer_id, campaign_id, change_date, lever,
                    old_value, new_value, rule_id, risk_tier, change_pct,
                    approved_by, executed_at,
                    action_type, entity_type, entity_id,
                    ad_group_id, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                [
                    self.customer_id,
                    rec.evidence.get("campaign_id"),
                    datetime.now().date(),
                    "product",
                    rec.current_value or 0,
                    rec.recommended_value or 0,
                    rec.rule_id,
                    rec.risk_tier,
                    rec.change_pct,
                    "system",
                    datetime.now(),
                    action_type,
                    "product",
                    rec.entity_id or rec.evidence.get("product_id"),
                    rec.evidence.get("ad_group_id"),
                    self._build_metadata(rec, api_response),
                ],
            )
            conn.commit()
            logger.info(f"Logged Shopping change: {action_type}")
        finally:
            conn.close()

    def _build_metadata(
        self, rec: Recommendation, api_response: dict = None
    ) -> str:
        """Build comprehensive metadata JSON (Q5 answer: B)."""
        import json

        metadata = {
            "rule_id": rec.rule_id,
            "confidence": rec.confidence,
            "risk_level": rec.risk_tier,
            "evidence": rec.evidence or {},
            "reasoning": rec.reasoning or "",
            "old_values": {"value": rec.current_value},
            "new_values": {"value": rec.recommended_value},
        }

        if api_response:
            metadata["api_response"] = api_response

        return json.dumps(metadata)

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _get_bid_type_from_recommendation(self, rec: Recommendation) -> str:
        """Determine bid type from recommendation evidence."""
        evidence = rec.evidence or {}

        if "bid_strategy" in evidence:
            strategy = evidence["bid_strategy"].lower()
            if "roas" in strategy:
                return "target_roas"
            elif "cpa" in strategy:
                return "target_cpa"

        if "roas" in rec.rule_name.lower():
            return "target_roas"
        elif "cpa" in rec.rule_name.lower():
            return "target_cpa"

        logger.warning(
            f"Could not determine bid type for {rec.rule_id}, defaulting to target_roas"
        )
        return "target_roas"


# Backwards compatibility alias
BudgetExecutor = Executor
