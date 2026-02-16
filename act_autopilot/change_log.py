"""
Change log persistence - tracks executed changes for cooldown enforcement

Extended in Chat 13 to support:
- Campaign changes (budget, bid)
- Keyword changes (add, pause, bid updates, negatives)
- Ad changes (pause, enable)
- Shopping changes (bid updates, product exclusions)
"""

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
import duckdb


class ChangeLog:
    """Manages change log persistence in DuckDB"""

    def __init__(self, db_path: str = "warehouse.duckdb"):
        self.db_path = Path(db_path)

    def _get_connection(self):
        """Get DuckDB connection"""
        return duckdb.connect(str(self.db_path))

    def log_change(
        self,
        customer_id: str,
        campaign_id: str,
        change_date: date,
        lever: str,
        old_value: float,
        new_value: float,
        rule_id: str,
        risk_tier: str,
        change_pct: Optional[float] = None,
        approved_by: Optional[str] = None,
        executed_at: Optional[datetime] = None,
        # New parameters for Chat 13
        action_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        match_type: Optional[str] = None,
        keyword_text: Optional[str] = None,
        ad_group_id: Optional[int] = None,
        metadata: Optional[str] = None,
    ) -> int:
        """
        Log an executed change

        Args:
            customer_id: Customer ID
            campaign_id: Campaign ID
            change_date: Date of change
            lever: Change lever (budget, bid, keyword, ad, product)
            old_value: Previous value
            new_value: New value
            rule_id: Rule that generated this change
            risk_tier: Risk level (LOW, MEDIUM, HIGH)
            change_pct: Percentage change (calculated if not provided)
            approved_by: Who approved the change
            executed_at: When executed (UTC timestamp)
            action_type: What action was performed (add_keyword, pause_ad, etc.)
            entity_type: What was changed (keyword, ad, product, campaign)
            entity_id: ID of the changed entity
            match_type: For keywords (EXACT, PHRASE, BROAD)
            keyword_text: Actual keyword text
            ad_group_id: Parent ad group ID
            metadata: JSON string with comprehensive metadata (Q5: comprehensive)

        Returns: change_id
        """
        conn = self._get_connection()

        # Calculate change_pct if not provided
        if change_pct is None:
            change_pct = ((new_value - old_value) / old_value) if old_value != 0 else 0

        # Use current timestamp if not provided
        if executed_at is None:
            executed_at = datetime.utcnow()

        # Determine action_type from lever if not provided (backwards compatibility)
        if action_type is None:
            if lever == "budget":
                action_type = "update_budget"
            elif lever == "bid":
                action_type = "update_bid_target"
            else:
                action_type = f"update_{lever}"

        # Determine entity_type from lever if not provided (backwards compatibility)
        if entity_type is None:
            if lever in ["budget", "bid"]:
                entity_type = "campaign"
            else:
                entity_type = lever

        # Use campaign_id as entity_id if not provided (backwards compatibility)
        if entity_id is None:
            entity_id = campaign_id

        result = conn.execute(
            """
            INSERT INTO analytics.change_log (
                customer_id, campaign_id, change_date, lever,
                old_value, new_value, change_pct, rule_id, risk_tier, 
                approved_by, executed_at,
                action_type, entity_type, entity_id,
                match_type, keyword_text, ad_group_id, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING change_id
        """,
            [
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
                executed_at,
                action_type,
                entity_type,
                entity_id,
                match_type,
                keyword_text,
                ad_group_id,
                metadata,
            ],
        ).fetchone()

        conn.close()

        return result[0] if result else None

    def get_recent_changes(
        self,
        customer_id: str,
        campaign_id: str,
        days_back: int = 7,
        lever: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get recent changes for a campaign

        Args:
            customer_id: Customer ID
            campaign_id: Campaign ID
            days_back: How many days back to look (default 7)
            lever: Optional filter by lever type

        Returns: List of change records
        """
        conn = self._get_connection()

        cutoff_date = date.today() - timedelta(days=days_back)

        if lever:
            query = """
                SELECT *
                FROM analytics.change_log
                WHERE customer_id = ?
                  AND campaign_id = ?
                  AND lever = ?
                  AND change_date >= ?
                ORDER BY change_date DESC, executed_at DESC
            """
            params = [customer_id, campaign_id, lever, cutoff_date]
        else:
            query = """
                SELECT *
                FROM analytics.change_log
                WHERE customer_id = ?
                  AND campaign_id = ?
                  AND change_date >= ?
                ORDER BY change_date DESC, executed_at DESC
            """
            params = [customer_id, campaign_id, cutoff_date]

        results = conn.execute(query, params).fetchall()
        conn.close()

        # Convert to list of dicts
        if not results:
            return []

        # Updated column list to include new Chat 13 columns
        columns = [
            "change_id",
            "customer_id",
            "campaign_id",
            "change_date",
            "lever",
            "old_value",
            "new_value",
            "change_pct",
            "rule_id",
            "risk_tier",
            "approved_by",
            "executed_at",
            "action_type",
            "entity_type",
            "entity_id",
            "match_type",
            "keyword_text",
            "ad_group_id",
            "metadata",
        ]

        return [dict(zip(columns, row)) for row in results]

    def check_cooldown(
        self, customer_id: str, campaign_id: str, lever: str, cooldown_days: int = 7
    ) -> bool:
        """
        Check if campaign+lever is in cooldown period

        Returns: True if cooldown active (change blocked), False if OK to change
        """
        recent = self.get_recent_changes(
            customer_id=customer_id,
            campaign_id=campaign_id,
            days_back=cooldown_days,
            lever=lever,
        )

        return len(recent) > 0

    def check_one_lever(
        self,
        customer_id: str,
        campaign_id: str,
        proposed_lever: str,
        cooldown_days: int = 7,
    ) -> bool:
        """
        Check one-lever-at-a-time rule

        Constitution rule: No budget+bid changes within 7 days

        Returns: True if violation (change blocked), False if OK
        """
        if proposed_lever not in ["budget", "bid"]:
            return False  # Rule only applies to budget/bid

        # Get all recent changes (any lever)
        recent = self.get_recent_changes(
            customer_id=customer_id, campaign_id=campaign_id, days_back=cooldown_days
        )

        # Check if opposite lever was changed
        opposite_lever = "bid" if proposed_lever == "budget" else "budget"

        for change in recent:
            if change["lever"] == opposite_lever:
                return True  # Violation: opposite lever changed recently

        return False

    def get_all_recent_changes(
        self, customer_id: str, days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """Get all recent changes across all campaigns for a customer"""
        conn = self._get_connection()

        cutoff_date = date.today() - timedelta(days=days_back)

        results = conn.execute(
            """
            SELECT *
            FROM analytics.change_log
            WHERE customer_id = ?
              AND change_date >= ?
            ORDER BY change_date DESC, executed_at DESC
        """,
            [customer_id, cutoff_date],
        ).fetchall()

        conn.close()

        if not results:
            return []

        # Updated column list to include new Chat 13 columns
        columns = [
            "change_id",
            "customer_id",
            "campaign_id",
            "change_date",
            "lever",
            "old_value",
            "new_value",
            "change_pct",
            "rule_id",
            "risk_tier",
            "approved_by",
            "executed_at",
            "action_type",
            "entity_type",
            "entity_id",
            "match_type",
            "keyword_text",
            "ad_group_id",
            "metadata",
        ]

        return [dict(zip(columns, row)) for row in results]

    def get_entity_changes(
        self,
        customer_id: str,
        entity_type: str,
        entity_id: str,
        days_back: int = 14,
    ) -> List[Dict[str, Any]]:
        """
        Get recent changes for a specific entity (keyword, ad, product)

        Useful for checking cooldowns on non-campaign entities.

        Args:
            customer_id: Customer ID
            entity_type: Type of entity (keyword, ad, product)
            entity_id: ID of the entity
            days_back: How many days back to look

        Returns: List of change records
        """
        conn = self._get_connection()

        cutoff_date = date.today() - timedelta(days=days_back)

        results = conn.execute(
            """
            SELECT *
            FROM analytics.change_log
            WHERE customer_id = ?
              AND entity_type = ?
              AND entity_id = ?
              AND change_date >= ?
            ORDER BY change_date DESC, executed_at DESC
        """,
            [customer_id, entity_type, str(entity_id), cutoff_date],
        ).fetchall()

        conn.close()

        if not results:
            return []

        columns = [
            "change_id",
            "customer_id",
            "campaign_id",
            "change_date",
            "lever",
            "old_value",
            "new_value",
            "change_pct",
            "rule_id",
            "risk_tier",
            "approved_by",
            "executed_at",
            "action_type",
            "entity_type",
            "entity_id",
            "match_type",
            "keyword_text",
            "ad_group_id",
            "metadata",
        ]

        return [dict(zip(columns, row)) for row in results]

    def get_action_type_count(
        self,
        customer_id: str,
        campaign_id: str,
        action_type: str,
        days_back: int = 1,
    ) -> int:
        """
        Count how many times a specific action was performed recently.

        Useful for enforcing daily limits (e.g., max 10 keyword adds per day).

        Args:
            customer_id: Customer ID
            campaign_id: Campaign ID (or None for all campaigns)
            action_type: Action to count (e.g., 'add_keyword', 'pause_ad')
            days_back: How many days back to look (default 1 = today only)

        Returns: Count of actions
        """
        conn = self._get_connection()

        cutoff_date = date.today() - timedelta(days=days_back)

        if campaign_id:
            query = """
                SELECT COUNT(*) as count
                FROM analytics.change_log
                WHERE customer_id = ?
                  AND campaign_id = ?
                  AND action_type = ?
                  AND change_date >= ?
            """
            params = [customer_id, campaign_id, action_type, cutoff_date]
        else:
            query = """
                SELECT COUNT(*) as count
                FROM analytics.change_log
                WHERE customer_id = ?
                  AND action_type = ?
                  AND change_date >= ?
            """
            params = [customer_id, action_type, cutoff_date]

        result = conn.execute(query, params).fetchone()
        conn.close()

        return result[0] if result else 0
