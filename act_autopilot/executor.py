"""
Execution engine for Google Ads campaign changes.
Handles both budget and bid target modifications.

Supports:
- Budget changes (daily budget increases/decreases)
- Bid changes (tROAS/tCPA target adjustments)
- Dry-run mode (simulation)
- Live mode (real API calls)
- Change logging
- Guardrail validation
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
from act_autopilot.models import Recommendation
from act_autopilot.change_log import ChangeLog
from act_autopilot.logging_config import setup_logging

logger = setup_logging(__name__)


@dataclass
class ExecutionResult:
    """Result of executing a single recommendation."""
    success: bool
    message: str
    error: Optional[str] = None
    executed_at: Optional[datetime] = None
    api_response: Optional[Dict] = None


class BudgetExecutor:
    """
    Executes budget and bid changes with validation and logging.
    
    Supports two modes:
    - Dry-run (default): Simulates changes, no API calls
    - Live: Makes real Google Ads API calls
    
    All changes are validated against Constitution guardrails:
    - Cooldown periods (7 days)
    - One-lever rule (budget ↔ bid)
    - Change magnitude limits (±5%/±10%/±15%)
    """
    
    def __init__(
        self,
        customer_id: str,
        db_path: str = "warehouse.duckdb",
        google_ads_client = None
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
        logger.info(f"BudgetExecutor initialized: customer_id={customer_id}, mode={mode}")
    
    def execute(
        self,
        recommendations: List[Recommendation],
        dry_run: bool = True,
        rule_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a list of recommendations.
        
        Args:
            recommendations: List of Recommendation objects
            dry_run: If True, simulate only. If False, make real API calls.
            rule_ids: Optional list of rule IDs to filter (e.g., ['BUDGET-001', 'BID-001'])
        
        Returns:
            Summary dict with total, successful, failed counts and detailed results
        """
        logger.info(f"Starting execution: total_recommendations={len(recommendations)}, dry_run={dry_run}")
        
        # Filter by rule_ids if provided
        if rule_ids:
            recommendations = [r for r in recommendations if r.rule_id in rule_ids]
            logger.info(f"Filtered by rule_ids: remaining={len(recommendations)}")
        
        # Filter to actual executable actions (exclude holds/status)
        executable_types = [
            'budget_increase', 
            'budget_decrease',
            'bid_target_increase',
            'bid_target_decrease'
        ]
        executable_recs = [r for r in recommendations if r.action_type in executable_types]
        
        logger.info(f"Executable recommendations: {len(executable_recs)} (budget + bid changes)")
        
        results = []
        successful = 0
        failed = 0
        
        for rec in executable_recs:
            result = self._execute_one(rec, dry_run)
            results.append({
                'rule_id': rec.rule_id,
                'campaign_id': rec.entity_id,
                'campaign_name': rec.campaign_name or 'Unknown',
                'action_type': rec.action_type,
                'success': result.success,
                'message': result.message,
                'error': result.error
            })
            
            if result.success:
                successful += 1
            else:
                failed += 1
        
        summary = {
            'total': len(executable_recs),
            'successful': successful,
            'failed': failed,
            'dry_run': dry_run,
            'results': results
        }
        
        logger.info(f"Execution complete: successful={successful}, failed={failed}")
        return summary
    
    def _execute_one(self, rec: Recommendation, dry_run: bool) -> ExecutionResult:
        """Execute a single recommendation."""
        logger.info(f"Executing {rec.rule_id} for campaign {rec.entity_id}")
        
        # Step 1: Pre-flight validation
        validation = self._validate_execution(rec)
        if not validation['valid']:
            logger.warning(f"Validation failed: {validation['reason']}")
            return ExecutionResult(
                success=False,
                message=f"Validation failed: {validation['reason']}",
                error=validation['reason']
            )
        
        # Step 2: Execute based on action type
        if rec.action_type in ['budget_increase', 'budget_decrease']:
            if dry_run:
                result = self._execute_budget_change_dryrun(rec)
            else:
                result = self._execute_budget_change_live(rec)
        elif rec.action_type in ['bid_target_increase', 'bid_target_decrease']:
            if dry_run:
                result = self._execute_bid_change_dryrun(rec)
            else:
                result = self._execute_bid_change_live(rec)
        else:
            return ExecutionResult(
                success=False,
                message=f"Unsupported action type: {rec.action_type}",
                error=f"Unsupported action type: {rec.action_type}"
            )
        
        # Step 3: Log if successful
        if result.success and not dry_run:
            self._log_change(rec)
        
        return result
    
    def _validate_execution(self, rec: Recommendation) -> Dict[str, Any]:
        """Validate recommendation before execution."""
        
        # Check 1: Determine lever
        if rec.action_type in ['budget_increase', 'budget_decrease']:
            lever = 'budget'
        elif rec.action_type in ['bid_target_increase', 'bid_target_decrease']:
            lever = 'bid'
        else:
            return {'valid': False, 'reason': f'Unknown action type: {rec.action_type}'}
        
        # Check 2: Cooldown (same lever)
        cooldown_violated = self.change_log.check_cooldown(
            customer_id=self.customer_id,
            campaign_id=rec.entity_id,
            lever=lever,
            cooldown_days=7
        )
        if cooldown_violated:
            return {'valid': False, 'reason': f'Cooldown violation - {lever} changed <7 days ago'}
        
        # Check 3: One-lever rule (opposite lever)
        opposite_lever = 'bid' if lever == 'budget' else 'budget'
        one_lever_violated = self.change_log.check_one_lever(
            customer_id=self.customer_id,
            campaign_id=rec.entity_id,
            proposed_lever=lever,
            cooldown_days=7
        )
        if one_lever_violated:
            return {'valid': False, 'reason': f'One-lever violation - {opposite_lever} changed <7 days ago'}
        
        # Check 4: Values exist
        if rec.current_value is None or rec.recommended_value is None:
            return {'valid': False, 'reason': 'Missing current_value or recommended_value'}
        
        # Check 5: Change magnitude limits (already in rec.change_pct)
        abs_change = abs(rec.change_pct) if rec.change_pct else 0.0
        if abs_change > 0.15:  # Max 15%
            return {'valid': False, 'reason': f'Change magnitude too large: {abs_change:.1%}'}
        
        return {'valid': True, 'reason': None}
    
    def _execute_budget_change_dryrun(self, rec: Recommendation) -> ExecutionResult:
        """Simulate budget change (dry-run)."""
        
        current = rec.current_value or 0
        proposed = rec.recommended_value or 0
        change_pct = rec.change_pct or 0
        
        message = f"""DRY-RUN: Would execute {rec.rule_id}
  Campaign: {rec.campaign_name or 'Unknown'} ({rec.entity_id})
  Current Budget: £{current:.2f}/day
  Proposed Budget: £{proposed:.2f}/day
  Change: {change_pct:+.1f}%
  Validation: PASS
  API call: SIMULATED
  Log: Would save to analytics.change_log"""
        
        logger.info(f"DRY-RUN budget change: {rec.rule_id} campaign={rec.entity_id}")
        return ExecutionResult(success=True, message=message)
    
    def _execute_bid_change_dryrun(self, rec: Recommendation) -> ExecutionResult:
        """Simulate bid change (dry-run)."""
        
        # Determine bid type
        bid_type = self._get_bid_type_from_recommendation(rec)
        
        current = rec.current_value or 0
        proposed = rec.recommended_value or 0
        change_pct = rec.change_pct or 0
        
        message = f"""DRY-RUN: Would execute {rec.rule_id}
  Campaign: {rec.campaign_name or 'Unknown'} ({rec.entity_id})
  Bid Type: {bid_type}
  Current: {current:.2f}
  Proposed: {proposed:.2f}
  Change: {change_pct:+.1f}%
  Validation: PASS
  API call: SIMULATED
  Log: Would save to analytics.change_log"""
        
        logger.info(f"DRY-RUN bid change: {rec.rule_id} campaign={rec.entity_id}")
        return ExecutionResult(success=True, message=message)
    
    def _get_bid_type_from_recommendation(self, rec: Recommendation) -> str:
        """Determine bid type from recommendation evidence."""
        evidence = rec.evidence or {}
        
        if 'bid_strategy' in evidence:
            strategy = evidence['bid_strategy'].lower()
            if 'roas' in strategy:
                return 'target_roas'
            elif 'cpa' in strategy:
                return 'target_cpa'
        
        # Default based on rule
        if 'roas' in rec.rule_name.lower():
            return 'target_roas'
        elif 'cpa' in rec.rule_name.lower():
            return 'target_cpa'
        
        logger.warning(f"Could not determine bid type for {rec.rule_id}, defaulting to target_roas")
        return 'target_roas'
    
    def _execute_budget_change_live(self, rec: Recommendation) -> ExecutionResult:
        """Execute real budget change via Google Ads API."""
        return ExecutionResult(
            success=False,
            message="Live execution not yet implemented",
            error="Live mode requires Google Ads API integration"
        )
    
    def _execute_bid_change_live(self, rec: Recommendation) -> ExecutionResult:
        """Execute real bid change via Google Ads API."""
        return ExecutionResult(
            success=False,
            message="Live execution not yet implemented",
            error="Live mode requires Google Ads API integration"
        )
    
    def _log_change(self, rec: Recommendation) -> None:
        """Log executed change to database."""
        lever = 'budget' if 'budget' in rec.action_type else 'bid'
        
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
            approved_by='system',
            executed_at=datetime.now()
        )
        logger.info(f"Logged change: {rec.rule_id} campaign={rec.entity_id}")
