"""
Budget execution engine with dry-run and live modes.

Handles:
- Pre-flight validation
- Google Ads API budget changes
- Change logging to database
- Error handling
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from .models import Recommendation
from .change_log import ChangeLog

logger = logging.getLogger(__name__)


class ExecutionResult:
    """Result of a single execution."""
    
    def __init__(
        self,
        recommendation: Recommendation,
        success: bool,
        message: str,
        api_response: Optional[Dict] = None,
        error: Optional[str] = None
    ):
        self.recommendation = recommendation
        self.success = success
        self.message = message
        self.api_response = api_response
        self.error = error
        self.executed_at = datetime.utcnow()


class BudgetExecutor:
    """
    Executes budget changes with dry-run and live modes.
    
    Dry-run: Simulates execution, logs what WOULD happen
    Live: Makes actual Google Ads API calls, logs to database
    """
    
    def __init__(
        self,
        customer_id: str,
        db_path: str = "warehouse.duckdb",
        google_ads_client = None
    ):
        """
        Args:
            customer_id: Google Ads customer ID
            db_path: Path to DuckDB database
            google_ads_client: GoogleAdsClient instance (None for dry-run)
        """
        self.customer_id = customer_id
        self.db_path = db_path
        self.client = google_ads_client
        self.change_log = ChangeLog(db_path)
        
    def execute(
        self,
        recommendations: List[Recommendation],
        dry_run: bool = True,
        rule_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute budget changes.
        
        Args:
            recommendations: List of recommendations to execute
            dry_run: If True, simulate only (default)
            rule_ids: If provided, only execute these rule IDs
            
        Returns:
            Summary dict with results
        """
        logger.info(f"Starting execution - dry_run={dry_run}")
        
        # Filter by rule_ids if provided
        if rule_ids:
            recommendations = [
                r for r in recommendations
                if r.rule_id in rule_ids
            ]
            logger.info(f"Filtered to {len(recommendations)} recommendations by rule_ids")
        
        # Filter budget changes only
        budget_recs = [
            r for r in recommendations
            if r.action_type in ['budget_increase', 'budget_decrease']
        ]
        
        logger.info(f"Processing {len(budget_recs)} budget recommendations")
        
        results = []
        for rec in budget_recs:
            result = self._execute_one(rec, dry_run)
            results.append(result)
        
        # Generate summary
        summary = self._generate_summary(results, dry_run)
        return summary
    
    def _execute_one(
        self,
        rec: Recommendation,
        dry_run: bool
    ) -> ExecutionResult:
        """Execute a single recommendation."""
        
        logger.info(f"Executing {rec.rule_id} on campaign {rec.entity_id}")
        
        # Step 1: Pre-flight validation
        validation = self._validate_execution(rec)
        if not validation['valid']:
            logger.warning(f"Validation failed: {validation['reason']}")
            return ExecutionResult(
                recommendation=rec,
                success=False,
                message=f"BLOCKED: {validation['reason']}",
                error=validation['reason']
            )
        
        # Step 2: Execute (dry-run or live)
        if dry_run:
            result = self._execute_budget_change_dryrun(rec)
        else:
            result = self._execute_budget_change_live(rec)
        
        # Step 3: Log to database (if live and successful)
        if not dry_run and result.success:
            self._log_change(rec, result)
        
        return result
    
    def _validate_execution(self, rec: Recommendation) -> Dict[str, Any]:
        """
        Pre-flight validation checks.
        
        Returns:
            dict: {'valid': bool, 'reason': str or None}
        """
        
        # Check if already blocked by guardrails
        if rec.blocked:
            return {
                'valid': False,
                'reason': f"Already blocked: {rec.block_reason}"
            }
        
        # Check cooldown via ChangeLog directly
        cooldown_blocked = self.change_log.check_cooldown(
            customer_id=self.customer_id,
            campaign_id=rec.entity_id,
            lever='budget',
            cooldown_days=7
        )
        
        if cooldown_blocked:
            return {
                'valid': False,
                'reason': "Cooldown violation - budget changed <7 days ago"
            }
        
        # Check one-lever rule via ChangeLog directly
        one_lever_violation = self.change_log.check_one_lever(
            customer_id=self.customer_id,
            campaign_id=rec.entity_id,
            proposed_lever='budget',
            cooldown_days=7
        )
        
        if one_lever_violation:
            return {
                'valid': False,
                'reason': "One-lever violation - bid changed <7 days ago"
            }
        
        # Check change magnitude
        if rec.change_pct is not None:
            abs_change = abs(rec.change_pct)
            
            # Absolute cap: 20%
            if abs_change > 0.20:
                return {
                    'valid': False,
                    'reason': f"Change magnitude {rec.change_pct:.1%} exceeds absolute cap ±20%"
                }
            
            # Conservative cap: 5%
            if abs_change > 0.05:
                return {
                    'valid': False,
                    'reason': f"Change magnitude {rec.change_pct:.1%} exceeds conservative cap ±5%"
                }
        
        # All checks passed
        return {'valid': True, 'reason': None}
    
    def _execute_budget_change_dryrun(self, rec: Recommendation) -> ExecutionResult:
        """Simulate budget change (dry-run mode)."""
        
        logger.info(f"DRY-RUN: Simulating {rec.rule_id}")
        
        message = (
            f"DRY-RUN: Would execute {rec.rule_id}\n"
            f"  Campaign: {rec.campaign_name} ({rec.entity_id})\n"
            f"  Current: {rec.current_value / 1_000_000:.2f}\n"
            f"  Proposed: {rec.recommended_value / 1_000_000:.2f}\n"
            f"  Change: {rec.change_pct:+.1%}\n"
            f"  Validation: PASS\n"
            f"  API call: SIMULATED\n"
            f"  Log: Would save to analytics.change_log"
        )
        
        return ExecutionResult(
            recommendation=rec,
            success=True,
            message=message,
            api_response={'simulated': True}
        )
    
    def _execute_budget_change_live(self, rec: Recommendation) -> ExecutionResult:
        """Execute budget change via Google Ads API."""
        
        if self.client is None:
            return ExecutionResult(
                recommendation=rec,
                success=False,
                message="FAILED: No Google Ads client provided",
                error="google_ads_client is None"
            )
        
        logger.info(f"LIVE: Executing {rec.rule_id}")
        
        try:
            # Call Google Ads API
            api_result = self._update_campaign_budget(
                campaign_id=rec.entity_id,
                new_budget_micros=int(rec.recommended_value)
            )
            
            message = (
                f"SUCCESS: Executed {rec.rule_id}\n"
                f"  Campaign: {rec.campaign_name} ({rec.entity_id})\n"
                f"  Old: {rec.current_value / 1_000_000:.2f}\n"
                f"  New: {rec.recommended_value / 1_000_000:.2f}\n"
                f"  Change: {rec.change_pct:+.1%}\n"
                f"  API response: {api_result['status']}"
            )
            
            return ExecutionResult(
                recommendation=rec,
                success=True,
                message=message,
                api_response=api_result
            )
            
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return ExecutionResult(
                recommendation=rec,
                success=False,
                message=f"FAILED: {str(e)}",
                error=str(e)
            )
    
    def _update_campaign_budget(
        self,
        campaign_id: str,
        new_budget_micros: int
    ) -> Dict[str, Any]:
        """Update campaign budget via Google Ads API."""
        
        from .google_ads_api import update_campaign_budget
        
        return update_campaign_budget(
            client=self.client,
            customer_id=self.customer_id,
            campaign_id=campaign_id,
            new_budget_micros=new_budget_micros
        )
    
    def _log_change(self, rec: Recommendation, result: ExecutionResult):
        """Log executed change to database."""
        
        logger.info(f"Logging change to database: {rec.rule_id}")
        
        self.change_log.log_change(
            customer_id=self.customer_id,
            campaign_id=rec.entity_id,
            change_date=datetime.utcnow().date(),
            lever='budget',
            old_value=rec.current_value,
            new_value=rec.recommended_value,
            change_pct=rec.change_pct,
            rule_id=rec.rule_id,
            risk_tier=rec.risk_tier,
            approved_by='system',  # TODO: Track if human-approved vs auto
            executed_at=result.executed_at
        )
    
    def _generate_summary(
        self,
        results: List[ExecutionResult],
        dry_run: bool
    ) -> Dict[str, Any]:
        """Generate execution summary."""
        
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        summary = {
            'total': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'dry_run': dry_run,
            'results': [
                {
                    'rule_id': r.recommendation.rule_id,
                    'campaign_id': r.recommendation.entity_id,
                    'campaign_name': r.recommendation.campaign_name,
                    'success': r.success,
                    'message': r.message,
                    'error': r.error
                }
                for r in results
            ]
        }
        
        return summary
