"""
Radar Module: Rollback Executor
Executes rollbacks by reversing changes via Google Ads API.

Constitution Reference: Section 8 (Monitoring, Rollback & Anti-Oscillation)
"""

import duckdb
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass
import yaml


@dataclass
class RollbackResult:
    """Result of a rollback execution."""
    success: bool
    change_id: int
    campaign_id: str
    lever: str
    old_value: float  # Value before rollback (what we're rolling back FROM)
    new_value: float  # Value after rollback (what we're rolling back TO)
    error_message: Optional[str] = None
    dry_run: bool = False


class RollbackExecutor:
    """Execute rollbacks by reversing changes."""
    
    def __init__(self, db_path: str = "warehouse.duckdb"):
        self.db_path = db_path
    
    def plan_rollback(self, change_id: int) -> Optional[Dict]:
        """
        Plan a rollback by reading the change from change_log.
        
        Returns:
            Dict with change details needed for rollback, or None if not found
        """
        conn = duckdb.connect(self.db_path, read_only=True)
        
        query = """
        SELECT 
            change_id,
            customer_id,
            campaign_id,
            change_date,
            lever,
            old_value,
            new_value,
            change_pct,
            rule_id,
            risk_tier,
            executed_at,
            rollback_status
        FROM analytics.change_log
        WHERE change_id = ?
        """
        
        row = conn.execute(query, [change_id]).fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'change_id': row[0],
            'customer_id': row[1],
            'campaign_id': row[2],
            'change_date': row[3],
            'lever': row[4],
            'old_value': row[5],
            'new_value': row[6],
            'change_pct': row[7],
            'rule_id': row[8],
            'risk_tier': row[9],
            'executed_at': row[10],
            'rollback_status': row[11],
        }
    
    def execute_rollback_budget(
        self, 
        customer_id: str,
        campaign_id: str,
        target_value_micros: int,
        dry_run: bool = True
    ) -> RollbackResult:
        """
        Rollback a budget change.
        
        Args:
            customer_id: Google Ads customer ID
            campaign_id: Campaign ID
            target_value_micros: Budget to restore (in micros)
            dry_run: If True, simulate only (no API call)
        
        Returns:
            RollbackResult with success status
        """
        if dry_run:
            print(f"  [DRY-RUN] Would set campaign {campaign_id} budget to {target_value_micros / 1_000_000:.2f}")
            return RollbackResult(
                success=True,
                change_id=0,  # Filled by caller
                campaign_id=campaign_id,
                lever='budget',
                old_value=0,  # Filled by caller
                new_value=target_value_micros,
                dry_run=True
            )
        
        # LIVE MODE: Execute via Google Ads API
        try:
            from google.ads.googleads.client import GoogleAdsClient
            
            # Load credentials
            with open('secrets/google-ads.yaml', 'r') as f:
                credentials = yaml.safe_load(f)
            
            # Initialize client
            client = GoogleAdsClient.load_from_dict(credentials)
            campaign_service = client.get_service("CampaignService")
            
            # Build campaign resource name
            campaign_resource_name = campaign_service.campaign_path(customer_id, campaign_id)
            
            # Create campaign budget operation
            campaign_operation = client.get_type("CampaignOperation")
            campaign = campaign_operation.update
            campaign.resource_name = campaign_resource_name
            
            # Set budget (daily budget in micros)
            campaign.campaign_budget.amount_micros = target_value_micros
            
            # Set field mask
            client.copy_from(
                campaign_operation.update_mask,
                client.get_type("FieldMask", version="v18")(paths=["campaign_budget.amount_micros"])
            )
            
            # Execute
            response = campaign_service.mutate_campaigns(
                customer_id=customer_id,
                operations=[campaign_operation]
            )
            
            print(f"  [LIVE] ✅ Set campaign {campaign_id} budget to {target_value_micros / 1_000_000:.2f}")
            
            return RollbackResult(
                success=True,
                change_id=0,
                campaign_id=campaign_id,
                lever='budget',
                old_value=0,
                new_value=target_value_micros,
                dry_run=False
            )
        
        except Exception as e:
            print(f"  [LIVE] ❌ Budget rollback failed: {str(e)}")
            return RollbackResult(
                success=False,
                change_id=0,
                campaign_id=campaign_id,
                lever='budget',
                old_value=0,
                new_value=target_value_micros,
                error_message=str(e),
                dry_run=False
            )
    
    def execute_rollback_bid(
        self, 
        customer_id: str,
        campaign_id: str,
        target_value_micros: int,
        dry_run: bool = True
    ) -> RollbackResult:
        """
        Rollback a bid target change (tCPA or tROAS).
        
        Args:
            customer_id: Google Ads customer ID
            campaign_id: Campaign ID
            target_value_micros: Target to restore (micros for tCPA, ratio for tROAS)
            dry_run: If True, simulate only (no API call)
        
        Returns:
            RollbackResult with success status
        """
        if dry_run:
            print(f"  [DRY-RUN] Would set campaign {campaign_id} bid target to {target_value_micros / 1_000_000:.2f}")
            return RollbackResult(
                success=True,
                change_id=0,
                campaign_id=campaign_id,
                lever='bid',
                old_value=0,
                new_value=target_value_micros,
                dry_run=True
            )
        
        # LIVE MODE: Execute via Google Ads API
        try:
            from google.ads.googleads.client import GoogleAdsClient
            
            # Load credentials
            with open('secrets/google-ads.yaml', 'r') as f:
                credentials = yaml.safe_load(f)
            
            # Initialize client
            client = GoogleAdsClient.load_from_dict(credentials)
            campaign_service = client.get_service("CampaignService")
            
            # Build campaign resource name
            campaign_resource_name = campaign_service.campaign_path(customer_id, campaign_id)
            
            # Create campaign operation
            campaign_operation = client.get_type("CampaignOperation")
            campaign = campaign_operation.update
            campaign.resource_name = campaign_resource_name
            
            # Set bid target (this would need to detect tCPA vs tROAS)
            # For now, assume tROAS (most common for ecom)
            campaign.target_roas.target_roas = target_value_micros / 1_000_000
            
            # Set field mask
            client.copy_from(
                campaign_operation.update_mask,
                client.get_type("FieldMask", version="v18")(paths=["target_roas.target_roas"])
            )
            
            # Execute
            response = campaign_service.mutate_campaigns(
                customer_id=customer_id,
                operations=[campaign_operation]
            )
            
            print(f"  [LIVE] ✅ Set campaign {campaign_id} bid target to {target_value_micros / 1_000_000:.2f}")
            
            return RollbackResult(
                success=True,
                change_id=0,
                campaign_id=campaign_id,
                lever='bid',
                old_value=0,
                new_value=target_value_micros,
                dry_run=False
            )
        
        except Exception as e:
            print(f"  [LIVE] ❌ Bid rollback failed: {str(e)}")
            return RollbackResult(
                success=False,
                change_id=0,
                campaign_id=campaign_id,
                lever='bid',
                old_value=0,
                new_value=target_value_micros,
                error_message=str(e),
                dry_run=False
            )
    
    def execute_rollback(
        self,
        change: Dict,
        reason: str,
        dry_run: bool = True
    ) -> RollbackResult:
        """
        Execute a rollback.
        
        Args:
            change: Change dict from plan_rollback()
            reason: Reason for rollback (from RollbackDecision)
            dry_run: If True, simulate only (no API call)
        
        Returns:
            RollbackResult with success status
        """
        change_id = change['change_id']
        customer_id = change['customer_id']
        campaign_id = change['campaign_id']
        lever = change['lever']
        old_value = change['old_value']  # Value BEFORE original change (rollback target)
        new_value = change['new_value']  # Value AFTER original change (current value)
        
        print(f"\n{'[DRY-RUN] ' if dry_run else '[LIVE] '}Rolling back change {change_id}:")
        print(f"  Campaign: {campaign_id}")
        print(f"  Lever: {lever}")
        print(f"  Reverting: {new_value:.2f} → {old_value:.2f}")
        print(f"  Reason: {reason}")
        
        # Execute appropriate rollback based on lever
        if lever == 'budget':
            result = self.execute_rollback_budget(
                customer_id=customer_id,
                campaign_id=campaign_id,
                target_value_micros=int(old_value),  # Rollback TO old_value
                dry_run=dry_run
            )
        elif lever == 'bid':
            result = self.execute_rollback_bid(
                customer_id=customer_id,
                campaign_id=campaign_id,
                target_value_micros=int(old_value),  # Rollback TO old_value
                dry_run=dry_run
            )
        else:
            print(f"  ❌ Unsupported lever: {lever}")
            return RollbackResult(
                success=False,
                change_id=change_id,
                campaign_id=campaign_id,
                lever=lever,
                old_value=new_value,  # Current value
                new_value=old_value,  # Target value
                error_message=f"Unsupported lever: {lever}",
                dry_run=dry_run
            )
        
        # Fill in change_id and values
        result.change_id = change_id
        result.old_value = new_value  # Current value (rolling back FROM)
        result.new_value = old_value  # Target value (rolling back TO)
        
        return result
    
    def log_rollback(
        self,
        result: RollbackResult,
        reason: str,
        original_change: Dict
    ):
        """
        Log rollback to database.
        
        Creates a new change_log entry for the rollback and marks original as rolled back.
        """
        if result.dry_run:
            print(f"  [DRY-RUN] Would log rollback to database")
            return
        
        conn = duckdb.connect(self.db_path)
        
        try:
            # 1. Insert new change_log entry for the rollback itself
            insert_query = """
            INSERT INTO analytics.change_log (
                customer_id,
                campaign_id,
                change_date,
                lever,
                old_value,
                new_value,
                change_pct,
                rule_id,
                risk_tier,
                approved_by,
                executed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            change_pct = (result.new_value - result.old_value) / result.old_value if result.old_value > 0 else 0
            
            conn.execute(insert_query, [
                original_change['customer_id'],
                result.campaign_id,
                datetime.now().date(),
                result.lever,
                result.old_value,
                result.new_value,
                change_pct,
                'ROLLBACK',
                'low',  # Rollbacks are always low risk (reverting to known state)
                'RADAR_AUTO',
                datetime.now()
            ])
            
            # Get the new rollback change_id
            rollback_id = conn.execute("SELECT MAX(change_id) FROM analytics.change_log").fetchone()[0]
            
            # 2. Mark original change as rolled back
            update_query = """
            UPDATE analytics.change_log
            SET rollback_status = 'rolled_back',
                rollback_id = ?,
                rollback_reason = ?,
                rollback_executed_at = ?
            WHERE change_id = ?
            """
            
            conn.execute(update_query, [
                rollback_id,
                reason,
                datetime.now(),
                result.change_id
            ])
            
            conn.commit()
            print(f"  ✅ Rollback logged to database (rollback_id={rollback_id})")
        
        except Exception as e:
            print(f"  ❌ Failed to log rollback: {str(e)}")
            conn.rollback()
        
        finally:
            conn.close()
    
    def mark_change_confirmed_good(self, change_id: int):
        """
        Mark a change as confirmed good (no rollback needed).
        
        This closes the monitoring window and prevents future rollback checks.
        """
        conn = duckdb.connect(self.db_path)
        
        try:
            update_query = """
            UPDATE analytics.change_log
            SET rollback_status = 'confirmed_good',
                monitoring_completed_at = ?
            WHERE change_id = ?
            """
            
            conn.execute(update_query, [datetime.now(), change_id])
            conn.commit()
            print(f"  ✅ Change {change_id} marked as confirmed good")
        
        except Exception as e:
            print(f"  ❌ Failed to mark change: {str(e)}")
            conn.rollback()
        
        finally:
            conn.close()


def execute_rollbacks(
    changes_to_rollback: List[Dict],
    reasons: List[str],
    dry_run: bool = True,
    db_path: str = "warehouse.duckdb"
) -> List[RollbackResult]:
    """
    Execute multiple rollbacks.
    
    Args:
        changes_to_rollback: List of change dicts from plan_rollback()
        reasons: List of reasons (one per change)
        dry_run: If True, simulate only
        db_path: Path to DuckDB
    
    Returns:
        List of RollbackResult objects
    """
    executor = RollbackExecutor(db_path=db_path)
    results = []
    
    for change, reason in zip(changes_to_rollback, reasons):
        result = executor.execute_rollback(change, reason, dry_run=dry_run)
        results.append(result)
        
        # Log to database if successful and not dry-run
        if result.success and not dry_run:
            executor.log_rollback(result, reason, change)
    
    return results
