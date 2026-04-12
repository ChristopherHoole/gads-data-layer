"""
ACT v2 Engine — Base Level Engine

Base class for all level engines. Provides shared methods for:
- Database connection
- Client/settings/level state loading
- Snapshot retrieval
- Recommendation writing
- Cooldown checking
- Idempotent recommendation cleanup
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import duckdb

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ENGINE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = ENGINE_DIR.parent.parent
DB_PATH = str(PROJECT_ROOT / "warehouse.duckdb")
LOG_PATH = str(ENGINE_DIR / "engine.log")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger('act_v2_engine')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

if not logger.handlers:
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


class BaseLevelEngine:
    """Base class for all ACT v2 level engines."""

    LEVEL = None  # Override in subclass

    def __init__(self, client_id: str):
        self.client_id = client_id
        self.db = self._connect_db()
        self.client = self._load_client()
        self.settings = self._load_settings()
        self.level_state = self._load_level_state()

    def _connect_db(self):
        """Connect to warehouse.duckdb."""
        try:
            return duckdb.connect(DB_PATH)
        except duckdb.IOException:
            logger.error("Database is locked. Stop the Flask app first:")
            logger.error("  taskkill /IM python.exe /F")
            sys.exit(1)

    def _load_client(self) -> dict:
        """Load client from act_v2_clients."""
        row = self.db.execute(
            """SELECT client_id, client_name, google_ads_customer_id, persona,
                      monthly_budget, target_cpa, target_roas, active
               FROM act_v2_clients WHERE client_id = ?""",
            [self.client_id]
        ).fetchone()
        if not row:
            raise ValueError(f"Client '{self.client_id}' not found")
        return {
            'id': row[0], 'name': row[1], 'customer_id': row[2], 'persona': row[3],
            'monthly_budget': float(row[4]) if row[4] else 0,
            'target_cpa': float(row[5]) if row[5] else None,
            'target_roas': float(row[6]) if row[6] else None,
            'active': row[7],
        }

    def _load_settings(self) -> dict:
        """Load all settings from act_v2_client_settings."""
        rows = self.db.execute(
            "SELECT setting_key, setting_value, setting_type FROM act_v2_client_settings WHERE client_id = ?",
            [self.client_id]
        ).fetchall()
        settings = {}
        for key, value, stype in rows:
            settings[key] = {'value': value, 'type': stype}
        return settings

    def _load_level_state(self) -> dict:
        """Load all level states from act_v2_client_level_state."""
        rows = self.db.execute(
            "SELECT level, state FROM act_v2_client_level_state WHERE client_id = ?",
            [self.client_id]
        ).fetchall()
        return {r[0]: r[1] for r in rows}

    def get_setting(self, key: str, default=None):
        """Get a setting value with type conversion."""
        s = self.settings.get(key)
        if not s or s['value'] is None:
            return default
        val = s['value']
        stype = s['type']
        try:
            if stype == 'int':
                return int(val)
            elif stype == 'decimal':
                return float(val)
            elif stype == 'bool':
                return val.lower() in ('true', '1', 'yes')
            else:
                return val
        except (ValueError, TypeError):
            return default

    def get_snapshots(self, level: str, date: str, days_back: int = 30) -> list:
        """Get snapshot data for a date range.

        Returns list of dicts with parsed metrics_json.
        """
        start_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=days_back)).strftime('%Y-%m-%d')
        rows = self.db.execute(
            """SELECT snapshot_date, entity_id, entity_name, parent_entity_id, metrics_json
               FROM act_v2_snapshots
               WHERE client_id = ? AND level = ? AND snapshot_date BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
               ORDER BY snapshot_date, entity_id""",
            [self.client_id, level, start_date, date]
        ).fetchall()

        results = []
        for row in rows:
            metrics = row[4]
            if isinstance(metrics, str):
                metrics = json.loads(metrics)
            results.append({
                'snapshot_date': str(row[0]),
                'entity_id': str(row[1]),
                'entity_name': row[2],
                'parent_entity_id': row[3],
                'metrics': metrics,
            })
        return results

    def write_recommendation(self, check_id, entity_id, entity_name, parent_entity_id,
                             action_category, risk_level, summary, recommendation_text,
                             estimated_impact, decision_tree, current_value, proposed_value):
        """Write a recommendation to act_v2_recommendations."""
        # Mode derived from level state
        level_state = self.level_state.get(self.LEVEL, 'off')
        mode = 'active' if level_state == 'active' else 'monitor_only'

        self.db.execute(
            """INSERT INTO act_v2_recommendations
               (client_id, level, check_id, entity_id, entity_name, parent_entity_id,
                action_category, risk_level, summary, recommendation_text,
                estimated_impact, decision_tree_json, current_value_json, proposed_value_json,
                status, mode)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)""",
            [self.client_id, self.LEVEL, check_id, str(entity_id), entity_name,
             str(parent_entity_id) if parent_entity_id else None,
             action_category, risk_level, summary, recommendation_text,
             estimated_impact,
             json.dumps(decision_tree) if decision_tree else None,
             json.dumps(current_value) if current_value else None,
             json.dumps(proposed_value) if proposed_value else None,
             mode]
        )

    def check_cooldown(self, check_id: str, entity_id: str) -> bool:
        """Check if a cooldown is active for this check+entity.
        Returns True if cooldown IS active (should NOT act), False if ready."""
        # Look for active monitoring entries (not resolved) for this entity
        count = self.db.execute(
            """SELECT COUNT(*) FROM act_v2_monitoring
               WHERE client_id = ? AND entity_id = ? AND monitoring_type = 'cooldown'
               AND resolved_at IS NULL AND ends_at > CURRENT_TIMESTAMP""",
            [self.client_id, str(entity_id)]
        ).fetchone()[0]
        return count > 0

    def clear_old_recommendations(self, level: str):
        """Delete existing PENDING recommendations for idempotency."""
        deleted = self.db.execute(
            """DELETE FROM act_v2_recommendations
               WHERE client_id = ? AND level = ? AND status = 'pending'
               RETURNING recommendation_id""",
            [self.client_id, level]
        ).fetchall()
        if deleted:
            logger.info(f"  Cleared {len(deleted)} old pending recommendations for {level}")

    def close(self):
        """Close database connection."""
        if self.db:
            self.db.close()
