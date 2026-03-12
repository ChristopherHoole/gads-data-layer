"""
tests/conftest.py — Shared fixtures for the ACT dashboard test suite.

Chat 89: No real DB, no real SMTP, no real Google Ads API calls.
Uses in-memory DuckDB with analytics schema + temp file for ro attachment.
"""

import contextlib
import os
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import duckdb
import pytest

# ── Project root on sys.path ──────────────────────────────────────────────────
PROJECT_ROOT = str(Path(__file__).parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

CUSTOMER_ID = "9999999999"
CONFIG_PATH = str(Path(PROJECT_ROOT) / "configs" / "client_synthetic.yaml")

# ── Connection wrapper that ignores close() calls ─────────────────────────────


class UnclosableConn:
    """Wraps a DuckDB connection so that close() is a no-op in tests."""

    def __init__(self, real_conn: duckdb.DuckDBPyConnection):
        self._conn = real_conn

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def close(self):
        pass  # no-op — the fixture manages the connection lifetime


# ── DB setup helpers ──────────────────────────────────────────────────────────

def _create_analytics_tables(conn: duckdb.DuckDBPyConnection):
    """Populate the analytics schema in a given DuckDB connection."""
    conn.execute("CREATE SCHEMA IF NOT EXISTS analytics")
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    # campaign_daily
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics.campaign_daily (
            customer_id      VARCHAR,
            campaign_id      BIGINT,
            campaign_name    VARCHAR,
            campaign_status  VARCHAR,
            channel_type     VARCHAR,
            snapshot_date    DATE,
            cost_micros      BIGINT,
            conversions_value DOUBLE,
            conversions      DOUBLE,
            all_conversions  DOUBLE,
            all_conversions_value DOUBLE,
            impressions      BIGINT,
            clicks           BIGINT,
            optimization_score DOUBLE,
            bid_strategy_type VARCHAR,
            search_impression_share DOUBLE,
            search_top_impression_share DOUBLE,
            search_absolute_top_impression_share DOUBLE,
            click_share      DOUBLE
        )
    """)
    conn.execute(f"""
        INSERT INTO analytics.campaign_daily VALUES
        ('{CUSTOMER_ID}', 111, 'Campaign Alpha', 'ENABLED', 'SEARCH', '{today}',
         5000000, 120.0, 3.0, 3.5, 125.0, 10000, 500, 0.85, 'TARGET_ROAS',
         0.65, 0.50, 0.30, 0.55),
        ('{CUSTOMER_ID}', 222, 'Campaign Beta', 'PAUSED', 'DISPLAY', '{yesterday}',
         2000000, 40.0, 1.0, 1.2, 42.0, 5000, 100, 0.50, 'TARGET_CPA',
         0.40, 0.25, 0.10, 0.30)
    """)

    # keyword_daily
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics.keyword_daily (
            customer_id  VARCHAR,
            keyword_id   BIGINT,
            keyword_text VARCHAR,
            match_type   VARCHAR,
            status       VARCHAR,
            campaign_id  BIGINT,
            campaign_name VARCHAR,
            ad_group_id  BIGINT,
            ad_group_name VARCHAR,
            snapshot_date DATE,
            quality_score INTEGER,
            cost         DOUBLE,
            conversions  DOUBLE,
            ctr          DOUBLE,
            roas         DOUBLE,
            impressions  BIGINT,
            clicks       BIGINT,
            bid_micros   BIGINT
        )
    """)
    conn.execute(f"""
        INSERT INTO analytics.keyword_daily VALUES
        ('{CUSTOMER_ID}', 1001, 'google ads agency', 'BROAD', 'ENABLED',
         111, 'Campaign Alpha', 2001, 'AdGroup 1', '{today}',
         7, 5.0, 0.5, 0.05, 2.5, 200, 10, 500000),
        ('{CUSTOMER_ID}', 1002, 'ppc management', 'EXACT', 'ENABLED',
         111, 'Campaign Alpha', 2001, 'AdGroup 1', '{today}',
         4, 2.0, 0.1, 0.02, 1.0, 100, 2, 300000)
    """)

    # ad_group_daily
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics.ad_group_daily (
            customer_id  VARCHAR,
            ad_group_id  BIGINT,
            ad_group_name VARCHAR,
            campaign_id  BIGINT,
            campaign_name VARCHAR,
            ad_group_status VARCHAR,
            ad_group_type VARCHAR,
            snapshot_date DATE,
            cost_micros  BIGINT,
            conversions_value DOUBLE,
            conversions  DOUBLE,
            all_conversions DOUBLE,
            all_conversions_value DOUBLE,
            impressions  BIGINT,
            clicks       BIGINT,
            target_cpa_micros BIGINT,
            cpc_bid_micros BIGINT,
            optimization_score DOUBLE,
            bid_strategy_type VARCHAR,
            search_impression_share DOUBLE,
            search_top_impression_share DOUBLE,
            search_absolute_top_impression_share DOUBLE,
            click_share  DOUBLE
        )
    """)
    conn.execute(f"""
        INSERT INTO analytics.ad_group_daily VALUES
        ('{CUSTOMER_ID}', 2001, 'AdGroup 1', 111, 'Campaign Alpha', 'ENABLED',
         'SEARCH_STANDARD', '{today}', 3000000, 80.0, 2.0, 2.5, 82.0, 6000, 300,
         25000000, 1000000, 0.80, 'TARGET_ROAS', 0.60, 0.45, 0.25, 0.50),
        ('{CUSTOMER_ID}', 2002, 'AdGroup 2', 222, 'Campaign Beta', 'PAUSED',
         'SEARCH_STANDARD', '{today}', 1000000, 20.0, 0.5, 0.6, 21.0, 2000, 80,
         30000000, 1500000, 0.60, 'TARGET_CPA', 0.35, 0.20, 0.08, 0.25)
    """)

    # ad_daily (Chat 88 new table)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics.ad_daily (
            customer_id  VARCHAR,
            ad_id        BIGINT,
            snapshot_date DATE,
            cost_micros  BIGINT,
            conversions_value DOUBLE,
            conversions  DOUBLE,
            impressions  BIGINT,
            clicks       BIGINT,
            ctr          DOUBLE,
            search_impression_share DOUBLE,
            search_top_impression_share DOUBLE,
            search_absolute_top_impression_share DOUBLE,
            click_share  DOUBLE
        )
    """)
    conn.execute(f"""
        INSERT INTO analytics.ad_daily VALUES
        ('{CUSTOMER_ID}', 3001, '{today}', 2000000, 60.0, 1.5, 5000, 200, 0.04,
         0.55, 0.40, 0.20, 0.45),
        ('{CUSTOMER_ID}', 3002, '{today}', 1000000, 30.0, 0.8, 2000, 100, 0.05,
         0.45, 0.30, 0.12, 0.35)
    """)

    # ad_features_daily (windowed columns used by ads route)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics.ad_features_daily (
            customer_id       VARCHAR,
            ad_id             BIGINT,
            snapshot_date     DATE,
            final_url         VARCHAR,
            campaign_name     VARCHAR,
            ad_group_name     VARCHAR,
            ad_status         VARCHAR,
            ad_type           VARCHAR,
            ad_strength       VARCHAR,
            cost_micros_30d   BIGINT,
            conversions_value_30d DOUBLE,
            conversions_30d   DOUBLE,
            cpa_30d           BIGINT,
            cvr_30d           DOUBLE,
            impressions_30d   BIGINT,
            clicks_30d        BIGINT,
            ctr_30d           DOUBLE
        )
    """)
    conn.execute(f"""
        INSERT INTO analytics.ad_features_daily VALUES
        ('{CUSTOMER_ID}', 3001, '{today}', 'https://example.com',
         'Campaign Alpha', 'AdGroup 1', 'ENABLED', 'EXPANDED_TEXT_AD', 'GOOD',
         2000000, 60.0, 1.5, 1333333, 0.0075, 5000, 200, 0.04),
        ('{CUSTOMER_ID}', 3002, '{today}', 'https://example.com/p2',
         'Campaign Beta', 'AdGroup 2', 'PAUSED', 'RESPONSIVE_SEARCH_AD', 'POOR',
         1000000, 30.0, 0.8, 1250000, 0.008, 2000, 100, 0.05)
    """)

    # shopping_campaign_daily
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics.shopping_campaign_daily (
            customer_id   VARCHAR,
            campaign_id   BIGINT,
            campaign_name VARCHAR,
            campaign_status VARCHAR,
            snapshot_date DATE,
            cost_micros   BIGINT,
            conversions_value DOUBLE,
            conversions   DOUBLE,
            impressions   BIGINT,
            clicks        BIGINT,
            ctr           DOUBLE,
            roas          DOUBLE,
            optimization_score DOUBLE,
            search_impression_share DOUBLE
        )
    """)
    conn.execute(f"""
        INSERT INTO analytics.shopping_campaign_daily VALUES
        ('{CUSTOMER_ID}', 333, 'Shopping Campaign', 'ENABLED', '{today}',
         8000000, 200.0, 5.0, 20000, 800, 0.04, 2.5, 0.75, 0.60)
    """)

    # product_features_daily (shopping products tab)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics.product_features_daily (
            customer_id   VARCHAR,
            product_id    VARCHAR,
            snapshot_date DATE,
            title         VARCHAR,
            brand         VARCHAR,
            condition_val VARCHAR,
            product_status VARCHAR,
            clicks_w7     BIGINT,
            conversions_w7 DOUBLE,
            cost_w7       DOUBLE,
            roas_w7       DOUBLE,
            impressions_w7 BIGINT,
            ctr_w7        DOUBLE
        )
    """)
    conn.execute(f"""
        INSERT INTO analytics.product_features_daily VALUES
        ('{CUSTOMER_ID}', 'PROD001', '{today}', 'Test Product', 'TestBrand',
         'new', 'ACTIVE', 50, 2.5, 25.0, 2.0, 1000, 0.05)
    """)

    # change_log (for system changes tab in changes route)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics.change_log (
            change_id     INTEGER,
            change_date   DATE,
            campaign_id   VARCHAR,
            customer_id   VARCHAR,
            lever         VARCHAR,
            old_value     DOUBLE,
            new_value     DOUBLE,
            change_pct    DOUBLE,
            rule_id       VARCHAR,
            risk_tier     VARCHAR,
            rollback_status VARCHAR,
            executed_at   TIMESTAMP
        )
    """)

    # keyword_features_daily (for keywords route)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics.keyword_features_daily (
            customer_id               VARCHAR,
            snapshot_date             DATE,
            keyword_id                BIGINT,
            keyword_text              VARCHAR,
            match_type                VARCHAR,
            status                    VARCHAR,
            campaign_id               BIGINT,
            campaign_name             VARCHAR,
            ad_group_name             VARCHAR,
            quality_score             INTEGER,
            quality_score_creative    INTEGER,
            quality_score_landing_page INTEGER,
            quality_score_relevance   INTEGER,
            clicks_w7_sum             BIGINT,
            impressions_w7_sum        BIGINT,
            cost_micros_w7_sum        BIGINT,
            conversions_w7_sum        DOUBLE,
            conversion_value_w7_sum   DOUBLE,
            ctr_w7                    DOUBLE,
            cpa_w7                    BIGINT,
            clicks_w30_sum            BIGINT,
            impressions_w30_sum       BIGINT,
            cost_micros_w30_sum       BIGINT,
            conversions_w30_sum       DOUBLE,
            conversion_value_w30_sum  DOUBLE,
            ctr_w30                   DOUBLE,
            cpa_w30                   BIGINT,
            roas_w30                  DOUBLE,
            low_data_flag             BOOLEAN,
            cvr_w30                   DOUBLE
        )
    """)
    conn.execute(f"""
        INSERT INTO analytics.keyword_features_daily VALUES
        ('{CUSTOMER_ID}', '{today}', 1001, 'google ads agency', 'BROAD', 'ENABLED',
         111, 'Campaign Alpha', 'AdGroup 1', 7, 6, 7, 5,
         50, 2000, 5000000, 1.5, 10.0, 0.025, 3333333,
         150, 6000, 15000000, 4.5, 30.0, 0.025, 3333333, 2.0, FALSE, 0.030),
        ('{CUSTOMER_ID}', '{today}', 1002, 'ppc management', 'EXACT', 'ENABLED',
         111, 'Campaign Alpha', 'AdGroup 1', 4, 3, 4, 4,
         20, 1000, 2000000, 0.5, 3.0, 0.020, 4000000,
         60, 3000, 6000000, 1.5, 9.0, 0.020, 4000000, 1.5, TRUE, 0.025)
    """)

    # search_term_daily (for keywords route search terms tab)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics.search_term_daily (
            customer_id         VARCHAR,
            snapshot_date       DATE,
            search_term         VARCHAR,
            keyword_text        VARCHAR,
            match_type          VARCHAR,
            search_term_status  VARCHAR,
            campaign_id         BIGINT,
            campaign_name       VARCHAR,
            ad_group_id         BIGINT,
            ad_group_name       VARCHAR,
            keyword_id          BIGINT,
            impressions         BIGINT,
            clicks              BIGINT,
            ctr                 DOUBLE,
            cost                DOUBLE,
            conversions         DOUBLE,
            conversions_value   DOUBLE
        )
    """)
    conn.execute(f"""
        INSERT INTO analytics.search_term_daily VALUES
        ('{CUSTOMER_ID}', '{today}', 'buy google ads management', 'google ads agency',
         'BROAD', 'ACTIVE', 111, 'Campaign Alpha', 2001, 'AdGroup 1', 1001,
         500, 25, 0.05, 50.0, 2.0, 20.0),
        ('{CUSTOMER_ID}', '{today}', 'cheap ppc', 'ppc management',
         'BROAD', 'ACTIVE', 111, 'Campaign Alpha', 2001, 'AdGroup 1', 1002,
         300, 15, 0.05, 30.0, 0.0, 0.0),
        ('{CUSTOMER_ID}', '{today}', 'free ads', 'google ads agency',
         'BROAD', 'ACTIVE', 111, 'Campaign Alpha', 2001, 'AdGroup 1', 1001,
         1000, 0, 0.0, 0.0, 0.0, 0.0)
    """)

    # campaign_features_daily (for recommendations engine)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics.campaign_features_daily (
            customer_id         VARCHAR,
            campaign_id         BIGINT,
            campaign_name       VARCHAR,
            snapshot_date       DATE,
            roas_w7_mean        DOUBLE,
            roas_w30_mean       DOUBLE,
            clicks_w7_sum       DOUBLE,
            conversions_w30_sum DOUBLE,
            cost_w14_cv         DOUBLE,
            anomaly_cost_z      DOUBLE,
            pacing_flag_over_105 BOOLEAN,
            ctr_w7_vs_prev_pct  DOUBLE,
            cvr_w7_vs_prev_pct  DOUBLE,
            cost_micros_w7_mean DOUBLE
        )
    """)
    # Row that breaches budget_1 rule: roas_7d > 1.15 × 4.0 = 4.6, clicks >= 30
    conn.execute(f"""
        INSERT INTO analytics.campaign_features_daily VALUES
        ('{CUSTOMER_ID}', 111, 'Campaign Alpha', '{today}',
         5.0, 4.5, 50.0, 8.0, 0.15, 0.5, FALSE, -5.0, -3.0, 5000000.0),
        ('{CUSTOMER_ID}', 222, 'Campaign Beta', '{today}',
         0.4, 0.6, 40.0, 2.0, 0.20, -0.3, FALSE, -25.0, -25.0, 2000000.0)
    """)


def _create_main_tables(conn: duckdb.DuckDBPyConnection):
    """Create writable tables in the main (in-memory) DB."""

    today = date.today().isoformat()

    # keyword_features_daily lives in the main DB (not the readonly attachment)
    # because keywords.py queries it without the 'ro.' prefix
    conn.execute("CREATE SCHEMA IF NOT EXISTS analytics")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics.keyword_features_daily (
            customer_id               VARCHAR,
            snapshot_date             DATE,
            keyword_id                BIGINT,
            keyword_text              VARCHAR,
            match_type                VARCHAR,
            status                    VARCHAR,
            campaign_id               BIGINT,
            campaign_name             VARCHAR,
            ad_group_name             VARCHAR,
            quality_score             INTEGER,
            quality_score_creative    INTEGER,
            quality_score_landing_page INTEGER,
            quality_score_relevance   INTEGER,
            clicks_w7_sum             BIGINT,
            impressions_w7_sum        BIGINT,
            cost_micros_w7_sum        BIGINT,
            conversions_w7_sum        DOUBLE,
            conversion_value_w7_sum   DOUBLE,
            ctr_w7                    DOUBLE,
            cpa_w7                    BIGINT,
            clicks_w30_sum            BIGINT,
            impressions_w30_sum       BIGINT,
            cost_micros_w30_sum       BIGINT,
            conversions_w30_sum       DOUBLE,
            conversion_value_w30_sum  DOUBLE,
            ctr_w30                   DOUBLE,
            cpa_w30                   BIGINT,
            roas_w30                  DOUBLE,
            low_data_flag             BOOLEAN,
            cvr_w30                   DOUBLE
        )
    """)
    conn.execute(f"""
        INSERT INTO analytics.keyword_features_daily VALUES
        ('{CUSTOMER_ID}', '{today}', 1001, 'google ads agency', 'BROAD', 'ENABLED',
         111, 'Campaign Alpha', 'AdGroup 1', 7, 6, 7, 5,
         50, 2000, 5000000, 1.5, 10.0, 0.025, 3333333,
         150, 6000, 15000000, 4.5, 30.0, 0.025, 3333333, 2.0, FALSE, 0.030),
        ('{CUSTOMER_ID}', '{today}', 1002, 'ppc management', 'EXACT', 'ENABLED',
         111, 'Campaign Alpha', 'AdGroup 1', 4, 3, 4, 4,
         20, 1000, 2000000, 0.5, 3.0, 0.020, 4000000,
         60, 3000, 6000000, 1.5, 9.0, 0.020, 4000000, 1.5, TRUE, 0.025)
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            rec_id              VARCHAR PRIMARY KEY,
            rule_id             VARCHAR,
            rule_type           VARCHAR,
            campaign_id         VARCHAR,
            campaign_name       VARCHAR,
            entity_type         VARCHAR,
            entity_id           VARCHAR,
            entity_name         VARCHAR,
            customer_id         VARCHAR,
            status              VARCHAR DEFAULT 'pending',
            action_direction    VARCHAR,
            action_magnitude    DOUBLE,
            current_value       DOUBLE,
            proposed_value      DOUBLE,
            trigger_summary     VARCHAR,
            confidence          VARCHAR,
            generated_at        TIMESTAMP,
            accepted_at         TIMESTAMP,
            monitoring_ends_at  TIMESTAMP,
            resolved_at         TIMESTAMP,
            outcome_metric      DOUBLE,
            created_at          TIMESTAMP,
            updated_at          TIMESTAMP,
            revert_reason       VARCHAR
        )
    """)

    conn.execute("CREATE SEQUENCE IF NOT EXISTS changes_seq START 1")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS changes (
            change_id       INTEGER DEFAULT nextval('changes_seq'),
            customer_id     VARCHAR NOT NULL,
            campaign_id     VARCHAR,
            campaign_name   VARCHAR,
            entity_type     VARCHAR,
            entity_id       VARCHAR,
            rule_id         VARCHAR,
            action_type     VARCHAR,
            old_value       DOUBLE,
            new_value       DOUBLE,
            justification   VARCHAR,
            executed_by     VARCHAR,
            executed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            dry_run         BOOLEAN DEFAULT FALSE,
            status          VARCHAR DEFAULT 'completed'
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS outreach_leads (
            id         INTEGER PRIMARY KEY,
            full_name  VARCHAR,
            company    VARCHAR,
            role       VARCHAR,
            email      VARCHAR,
            status     VARCHAR DEFAULT 'active',
            notes      VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS outreach_emails (
            id           INTEGER PRIMARY KEY,
            lead_id      INTEGER,
            subject      VARCHAR,
            body         VARCHAR,
            status       VARCHAR DEFAULT 'queued',
            sent_at      TIMESTAMP,
            scheduled_at TIMESTAMP,
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Raw tables that the shopping route queries from the main DB
    conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_shopping_campaign_daily (
            customer_id   VARCHAR,
            campaign_id   BIGINT,
            campaign_name VARCHAR,
            snapshot_date DATE,
            cost_micros   BIGINT,
            impressions   BIGINT,
            clicks        BIGINT,
            conversions   DOUBLE
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_product_feed_quality (
            customer_id VARCHAR,
            product_id  VARCHAR,
            ingested_at TIMESTAMP,
            status      VARCHAR,
            issues      VARCHAR
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_product_performance_daily (
            customer_id       VARCHAR,
            product_id        VARCHAR,
            product_title     VARCHAR,
            product_brand     VARCHAR,
            product_category  VARCHAR,
            availability      VARCHAR,
            snapshot_date     DATE,
            impressions       BIGINT,
            clicks            BIGINT,
            cost_micros       BIGINT,
            conversions       DOUBLE,
            conversions_value DOUBLE
        )
    """)
    conn.execute(f"""
        INSERT INTO raw_product_performance_daily VALUES
        ('{CUSTOMER_ID}', 'RAW001', 'Raw Product Title', 'RawBrand',
         'Electronics', 'in_stock', '{today}', 500, 20, 1000000, 1.5, 45.0)
    """)


def _seed_recommendations(conn: duckdb.DuckDBPyConnection):
    """Insert seed recommendation rows (5 rows — one per status)."""
    now = datetime.now()
    future = now + timedelta(days=7)

    # rec_id, rule_id, rule_type, campaign_id, campaign_name,
    # entity_type, entity_id, entity_name, customer_id, status,
    # action_direction, action_magnitude, current_value, proposed_value,
    # trigger_summary, confidence,
    # generated_at, accepted_at, monitoring_ends_at, resolved_at,
    # outcome_metric, created_at, updated_at, revert_reason

    conn.execute("""
        INSERT INTO recommendations (
            rec_id, rule_id, rule_type, campaign_id, campaign_name,
            entity_type, entity_id, entity_name, customer_id, status,
            action_direction, action_magnitude, current_value, proposed_value,
            trigger_summary, confidence,
            generated_at, accepted_at, monitoring_ends_at, resolved_at,
            outcome_metric, created_at, updated_at, revert_reason
        ) VALUES
        ('rec-001', 'budget_1', 'budget', '111', 'Campaign Alpha',
         'campaign', '111', 'Campaign Alpha', ?, 'pending',
         'increase', 10.0, 50.0, 55.0, 'roas 5.00 AND clicks 50.00', 'high',
         ?, NULL, NULL, NULL, NULL, ?, ?, NULL),
        ('rec-002', 'keyword_1', 'status', '111', 'Campaign Alpha',
         'keyword', '1002', 'ppc management', ?, 'pending',
         'pause', 0.0, 0.50, 0.50, 'quality_score = 4', 'medium',
         ?, NULL, NULL, NULL, NULL, ?, ?, NULL),
        ('rec-003', 'budget_2', 'budget', '222', 'Campaign Beta',
         'campaign', '222', 'Campaign Beta', ?, 'monitoring',
         'decrease', 10.0, 20.0, 18.0, 'roas 0.50 AND clicks 40.00', 'high',
         ?, ?, ?, NULL, NULL, ?, ?, NULL),
        ('rec-004', 'bid_1', 'bid', '111', 'Campaign Alpha',
         'campaign', '111', 'Campaign Alpha', ?, 'declined',
         'increase', 5.0, 4.0, 4.2, 'roas ok', 'low',
         ?, NULL, NULL, ?, NULL, ?, ?, NULL),
        ('rec-005', 'status_1', 'status', '222', 'Campaign Beta',
         'campaign', '222', 'Campaign Beta', ?, 'successful',
         'pause', 0.0, 0.0, 0.0, 'low roas', 'medium',
         ?, NULL, NULL, ?, NULL, ?, ?, NULL)
    """, [
        # rec-001: customer_id, generated_at, created_at, updated_at
        CUSTOMER_ID, now, now, now,
        # rec-002: customer_id, generated_at, created_at, updated_at
        CUSTOMER_ID, now, now, now,
        # rec-003: customer_id, generated_at, accepted_at, monitoring_ends_at, created_at, updated_at
        CUSTOMER_ID, now, now, future, now, now,
        # rec-004: customer_id, generated_at, resolved_at, created_at, updated_at
        CUSTOMER_ID, now, now, now, now,
        # rec-005: customer_id, generated_at, resolved_at, created_at, updated_at
        CUSTOMER_ID, now, now, now, now,
    ])


# ── Session-scoped: readonly analytics DB ─────────────────────────────────────


@pytest.fixture(scope="session")
def ro_db_path(tmp_path_factory):
    """Create a session-scoped readonly DuckDB file with all analytics tables."""
    tmp = tmp_path_factory.mktemp("ro_db")
    path = str(tmp / "ro_test.duckdb")
    conn = duckdb.connect(path)
    _create_analytics_tables(conn)
    conn.close()
    return path


# ── Function-scoped: fresh main DB per test ───────────────────────────────────


@pytest.fixture
def db_conn(ro_db_path):
    """
    Function-scoped in-memory DuckDB for the writable DB.
    Attaches the session-scoped analytics DB as 'ro'.
    """
    conn = duckdb.connect(":memory:")
    conn.execute(f"ATTACH '{ro_db_path}' AS ro (READ_ONLY)")
    _create_main_tables(conn)
    _seed_recommendations(conn)
    yield conn
    conn.close()


# ── Flask test app (session-scoped) ───────────────────────────────────────────


@pytest.fixture(scope="session")
def app():
    """
    Minimal Flask test app — no background threads, no CSRF, no rate limiter.
    Uses the real act_dashboard blueprint registration.
    """
    # Patch heavy background-thread starters before any import
    with (
        patch("act_dashboard.outreach_poller.start_poller", return_value=None),
        patch("act_dashboard.queue_scheduler.QueueScheduler", MagicMock()),
        patch("act_autopilot.radar.radar_loop", return_value=None),
    ):
        from flask import Flask
        from act_dashboard.auth import init_auth
        from act_dashboard.routes import register_blueprints
        from act_dashboard.cache import ExpiringCache

        flask_app = Flask("act_dashboard")
        flask_app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret-key-chat89",
            WTF_CSRF_ENABLED=False,
            AVAILABLE_CLIENTS=[("Test Client", CONFIG_PATH)],
            DEFAULT_CLIENT=CONFIG_PATH,
            RECOMMENDATIONS_CACHE=ExpiringCache(default_ttl=3600),
        )

        init_auth(flask_app)
        register_blueprints(flask_app)

        # Provide a no-op csrf_token for templates (WTF_CSRF_ENABLED=False)
        flask_app.jinja_env.globals["csrf_token"] = lambda: "test-csrf-token"

    return flask_app


# ── Test client (function-scoped) with auth + mocked DB ──────────────────────


@pytest.fixture
def client(app, db_conn):
    """
    Flask test client with:
    - session['logged_in'] = True
    - session['current_client_config'] = CONFIG_PATH
    - get_db_connection patched in all route modules to return UnclosableConn
    """

    def _mock_db(config=None, read_only=False):
        return UnclosableConn(db_conn)

    patch_targets = [
        "act_dashboard.routes.campaigns.get_db_connection",
        "act_dashboard.routes.keywords.get_db_connection",
        "act_dashboard.routes.ads.get_db_connection",
        "act_dashboard.routes.ad_groups.get_db_connection",
        "act_dashboard.routes.shopping.get_db_connection",
        "act_dashboard.routes.recommendations.get_db_connection",
        "act_dashboard.routes.changes.get_db_connection",
        "act_dashboard.routes.dashboard.get_db_connection",
    ]

    with contextlib.ExitStack() as stack:
        for target in patch_targets:
            try:
                stack.enter_context(patch(target, side_effect=_mock_db))
            except AttributeError:
                pass  # module may not import get_db_connection

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess["logged_in"] = True
                sess["current_client_config"] = CONFIG_PATH
            yield c
