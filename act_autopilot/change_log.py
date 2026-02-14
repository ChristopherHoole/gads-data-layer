"""
Change log persistence - tracks executed changes for cooldown enforcement
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
    ) -> int:
        """
        Log an executed change

        Returns: change_id
        """
        conn = self._get_connection()

        # Calculate change_pct if not provided
        if change_pct is None:
            change_pct = ((new_value - old_value) / old_value) if old_value != 0 else 0

        # Use current timestamp if not provided
        if executed_at is None:
            executed_at = datetime.utcnow()

        result = conn.execute(
            """
            INSERT INTO analytics.change_log (
                customer_id, campaign_id, change_date, lever,
                old_value, new_value, change_pct, rule_id, risk_tier, approved_by, executed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        ]

        return [dict(zip(columns, row)) for row in results]
