"""
ACT v2 Google Ads Data Ingestion

Pulls data from Google Ads API and stores in act_v2_* tables.
Handles campaigns, ad groups, keywords, ads, search terms, and campaign segments.

All monetary values converted from micros to GBP (divide by 1,000,000).
"""

import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import duckdb
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
YAML_PATH = str(PROJECT_ROOT / "secrets" / "google-ads.yaml")
DB_PATH = str(PROJECT_ROOT / "warehouse.duckdb")
LOG_PATH = str(SCRIPT_DIR / "ingestion.log")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger('act_v2_ingestion')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

if not logger.handlers:
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

MICROS = 1_000_000


def _safe_div(numerator, denominator):
    """Safe division, returns 0.0 on zero denominator."""
    if not denominator:
        return 0.0
    return numerator / denominator


class GoogleAdsDataPipeline:
    def __init__(self, client_id: str, customer_id: str):
        """
        client_id: ACT internal client ID (e.g., 'oe001')
        customer_id: Google Ads customer ID (e.g., '8530211223')
        """
        self.client_id = client_id
        self.customer_id = customer_id
        self.google_ads_client = self._load_client()
        self.ga_service = self.google_ads_client.get_service("GoogleAdsService")
        self.db = self._connect_db()
        self.stats = {}

    def _load_client(self) -> GoogleAdsClient:
        """Load Google Ads client from secrets/google-ads.yaml"""
        return GoogleAdsClient.load_from_storage(YAML_PATH)

    def _connect_db(self):
        """Connect to warehouse.duckdb"""
        try:
            return duckdb.connect(DB_PATH)
        except duckdb.IOException:
            logger.error("Database is locked. Stop the Flask app first:")
            logger.error("  taskkill /IM python.exe /F")
            sys.exit(1)

    def _query(self, query: str):
        """Run a GAQL query and return the response iterator."""
        return self.ga_service.search(customer_id=self.customer_id, query=query)

    # -----------------------------------------------------------------------
    # Snapshot storage (idempotent: delete-then-insert)
    # -----------------------------------------------------------------------
    def _store_snapshot(self, date, level, entity_id, entity_name, parent_entity_id, metrics_dict):
        """Store a single entity snapshot."""
        self.db.execute(
            "DELETE FROM act_v2_snapshots WHERE client_id = ? AND snapshot_date = ? AND level = ? AND entity_id = ?",
            [self.client_id, date, level, str(entity_id)]
        )
        self.db.execute(
            """INSERT INTO act_v2_snapshots
               (client_id, snapshot_date, level, entity_id, entity_name, parent_entity_id, metrics_json)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [self.client_id, date, level, str(entity_id), entity_name,
             str(parent_entity_id) if parent_entity_id else None,
             json.dumps(metrics_dict)]
        )

    # -----------------------------------------------------------------------
    # Ingest orchestration
    # -----------------------------------------------------------------------
    def ingest_date(self, date: str):
        """Pull all data for a single date and store in act_v2_* tables."""
        logger.info(f"Ingesting {date} for {self.client_id}...")

        c = self.ingest_campaigns(date)
        ag = self.ingest_ad_groups(date)
        kw = self.ingest_keywords(date)
        ad = self.ingest_ads(date)
        st = self.ingest_search_terms(date)
        # Wave B — PMax terms from campaign_search_term_insight; must run after
        # ingest_search_terms (which clears the day) and after ingest_campaigns
        # (which populates act_v2_snapshots with campaign_type metadata we read).
        pst = self.ingest_pmax_search_terms(date)
        seg = self.ingest_campaign_segments(date)
        self.ingest_account(date)
        # N1a — negative-keyword lists are a point-in-time snapshot of current state,
        # not per-historical-date. We re-run on every ingest_date call and overwrite.
        nl = self.ingest_negative_lists(date)

        logger.info(f"  {date}: campaigns={c}, ad_groups={ag}, keywords={kw}, ads={ad}, search_terms={st}+pmax={pst}, segments={seg}, neg_lists={nl['lists']}/{nl['keywords']}kw")
        return {'campaigns': c, 'ad_groups': ag, 'keywords': kw, 'ads': ad,
                'search_terms': st, 'pmax_search_terms': pst, 'segments': seg,
                'neg_lists': nl['lists'], 'neg_keywords': nl['keywords']}

    def ingest_date_range(self, start_date: str, end_date: str):
        """Pull data for a range of dates (for backfill)."""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        total_days = (end - start).days + 1

        logger.info(f"Backfill: {start_date} to {end_date} ({total_days} days)")

        current = start
        day_num = 0
        while current <= end:
            day_num += 1
            date_str = current.strftime('%Y-%m-%d')
            try:
                result = self.ingest_date(date_str)
                for key, val in result.items():
                    self.stats[key] = self.stats.get(key, 0) + val
            except GoogleAdsException as e:
                logger.error(f"  API error on {date_str}: {e.failure.errors[0].message if e.failure.errors else e}")
            except Exception as e:
                logger.error(f"  Error on {date_str}: {e}")

            if day_num % 10 == 0:
                logger.info(f"  Progress: {day_num}/{total_days} days")

            current += timedelta(days=1)
            time.sleep(0.5)  # Avoid API rate limits

        logger.info(f"Backfill complete: {day_num} days processed")

    # -----------------------------------------------------------------------
    # Campaign ingestion
    # -----------------------------------------------------------------------
    def ingest_campaigns(self, date: str) -> int:
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                campaign_budget.amount_micros,
                campaign.bidding_strategy_type,
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc,
                metrics.cost_per_conversion,
                metrics.search_impression_share,
                metrics.search_budget_lost_impression_share,
                metrics.search_rank_lost_impression_share,
                segments.date
            FROM campaign
            WHERE segments.date = '{date}'
                AND campaign.status != 'REMOVED'
        """
        count = 0
        for row in self._query(query):
            cost = row.metrics.cost_micros / MICROS
            metrics = {
                "cost": round(cost, 2),
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "conversions": round(row.metrics.conversions, 2),
                "conversion_value": round(row.metrics.conversions_value, 2),
                "ctr": round(row.metrics.ctr, 6),
                "avg_cpc": round(row.metrics.average_cpc / MICROS, 2),
                "cost_per_conversion": round(row.metrics.cost_per_conversion / MICROS, 2),
                "conversion_rate": round(_safe_div(row.metrics.conversions, row.metrics.clicks), 4),
                "budget_amount": round(row.campaign_budget.amount_micros / MICROS, 2),
                "bid_strategy_type": row.campaign.bidding_strategy_type.name,
                "target_cpa": None,
                "target_roas": None,
                "campaign_status": row.campaign.status.name,
                "campaign_type": row.campaign.advertising_channel_type.name,
                "search_impression_share": round(row.metrics.search_impression_share, 4) if row.metrics.search_impression_share else None,
                "search_lost_is_budget": round(row.metrics.search_budget_lost_impression_share, 4) if row.metrics.search_budget_lost_impression_share else None,
                "search_lost_is_rank": round(row.metrics.search_rank_lost_impression_share, 4) if row.metrics.search_rank_lost_impression_share else None,
            }
            self._store_snapshot(date, 'campaign', row.campaign.id, row.campaign.name, None, metrics)
            count += 1
        return count

    # -----------------------------------------------------------------------
    # Ad Group ingestion
    # -----------------------------------------------------------------------
    def ingest_ad_groups(self, date: str) -> int:
        query = f"""
            SELECT
                ad_group.id,
                ad_group.name,
                ad_group.status,
                campaign.id,
                campaign.name,
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc,
                metrics.cost_per_conversion,
                segments.date
            FROM ad_group
            WHERE segments.date = '{date}'
                AND campaign.status != 'REMOVED'
                AND ad_group.status != 'REMOVED'
        """
        count = 0
        for row in self._query(query):
            metrics = {
                "cost": round(row.metrics.cost_micros / MICROS, 2),
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "conversions": round(row.metrics.conversions, 2),
                "conversion_value": round(row.metrics.conversions_value, 2),
                "ctr": round(row.metrics.ctr, 6),
                "avg_cpc": round(row.metrics.average_cpc / MICROS, 2),
                "cost_per_conversion": round(row.metrics.cost_per_conversion / MICROS, 2),
                "conversion_rate": round(_safe_div(row.metrics.conversions, row.metrics.clicks), 4),
                "ad_group_status": row.ad_group.status.name,
            }
            self._store_snapshot(date, 'ad_group', row.ad_group.id, row.ad_group.name,
                                row.campaign.id, metrics)
            count += 1
        return count

    # -----------------------------------------------------------------------
    # Keyword ingestion
    # -----------------------------------------------------------------------
    def ingest_keywords(self, date: str) -> int:
        query = f"""
            SELECT
                ad_group_criterion.criterion_id,
                ad_group_criterion.keyword.text,
                ad_group_criterion.keyword.match_type,
                ad_group_criterion.status,
                ad_group_criterion.quality_info.quality_score,
                ad_group_criterion.quality_info.creative_quality_score,
                ad_group_criterion.quality_info.search_predicted_ctr,
                ad_group_criterion.quality_info.post_click_quality_score,
                ad_group_criterion.effective_cpc_bid_micros,
                ad_group.id,
                ad_group.name,
                campaign.id,
                campaign.name,
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc,
                metrics.cost_per_conversion,
                segments.date
            FROM keyword_view
            WHERE segments.date = '{date}'
                AND campaign.status != 'REMOVED'
                AND ad_group.status != 'REMOVED'
        """
        count = 0
        for row in self._query(query):
            # Quality info fields may be 0 (UNSPECIFIED) if not available
            qs = row.ad_group_criterion.quality_info.quality_score
            quality_score = qs if qs > 0 else None

            creative_qs = row.ad_group_criterion.quality_info.creative_quality_score
            predicted_ctr = row.ad_group_criterion.quality_info.search_predicted_ctr
            landing_page = row.ad_group_criterion.quality_info.post_click_quality_score

            metrics = {
                "cost": round(row.metrics.cost_micros / MICROS, 2),
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "conversions": round(row.metrics.conversions, 2),
                "conversion_value": round(row.metrics.conversions_value, 2),
                "ctr": round(row.metrics.ctr, 6),
                "avg_cpc": round(row.metrics.average_cpc / MICROS, 2),
                "cost_per_conversion": round(row.metrics.cost_per_conversion / MICROS, 2),
                "conversion_rate": round(_safe_div(row.metrics.conversions, row.metrics.clicks), 4),
                "keyword_text": row.ad_group_criterion.keyword.text,
                "match_type": row.ad_group_criterion.keyword.match_type.name,
                "keyword_status": row.ad_group_criterion.status.name,
                "quality_score": quality_score,
                "expected_ctr": predicted_ctr.name if predicted_ctr else None,
                "ad_relevance": creative_qs.name if creative_qs else None,
                "landing_page_experience": landing_page.name if landing_page else None,
                "max_cpc_bid": round(row.ad_group_criterion.effective_cpc_bid_micros / MICROS, 2) if row.ad_group_criterion.effective_cpc_bid_micros else None,
            }
            # Use campaign_id as parent for keyword (ad_group_id stored in entity hierarchy)
            entity_id = f"{row.ad_group.id}_{row.ad_group_criterion.criterion_id}"
            self._store_snapshot(date, 'keyword', entity_id,
                                row.ad_group_criterion.keyword.text,
                                row.ad_group.id, metrics)
            count += 1
        return count

    # -----------------------------------------------------------------------
    # Ad ingestion
    # -----------------------------------------------------------------------
    def ingest_ads(self, date: str) -> int:
        query = f"""
            SELECT
                ad_group_ad.ad.id,
                ad_group_ad.ad.type,
                ad_group_ad.ad.name,
                ad_group_ad.ad.final_urls,
                ad_group_ad.status,
                ad_group_ad.ad_strength,
                ad_group.id,
                ad_group.name,
                campaign.id,
                campaign.name,
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc,
                metrics.cost_per_conversion,
                segments.date
            FROM ad_group_ad
            WHERE segments.date = '{date}'
                AND campaign.status != 'REMOVED'
                AND ad_group.status != 'REMOVED'
                AND ad_group_ad.status != 'REMOVED'
        """
        count = 0
        for row in self._query(query):
            final_urls = list(row.ad_group_ad.ad.final_urls) if row.ad_group_ad.ad.final_urls else []

            metrics = {
                "cost": round(row.metrics.cost_micros / MICROS, 2),
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "conversions": round(row.metrics.conversions, 2),
                "conversion_value": round(row.metrics.conversions_value, 2),
                "ctr": round(row.metrics.ctr, 6),
                "avg_cpc": round(row.metrics.average_cpc / MICROS, 2),
                "cost_per_conversion": round(row.metrics.cost_per_conversion / MICROS, 2),
                "conversion_rate": round(_safe_div(row.metrics.conversions, row.metrics.clicks), 4),
                "ad_type": row.ad_group_ad.ad.type_.name,
                "ad_status": row.ad_group_ad.status.name,
                "ad_strength": row.ad_group_ad.ad_strength.name if row.ad_group_ad.ad_strength else None,
                "final_urls": final_urls,
            }
            ad_name = row.ad_group_ad.ad.name or f"Ad {row.ad_group_ad.ad.id}"
            self._store_snapshot(date, 'ad', row.ad_group_ad.ad.id, ad_name,
                                row.ad_group.id, metrics)
            count += 1
        return count

    # -----------------------------------------------------------------------
    # Search terms ingestion
    # -----------------------------------------------------------------------
    def ingest_search_terms(self, date: str) -> int:
        """Search/Shopping campaign search terms via search_term_view.
        PMax terms come from ingest_pmax_search_terms (separate resource)."""
        query = f"""
            SELECT
                search_term_view.search_term,
                search_term_view.status,
                ad_group.id,
                ad_group.name,
                campaign.id,
                campaign.name,
                campaign.advertising_channel_type,
                segments.keyword.info.text,
                segments.keyword.info.match_type,
                segments.keyword.ad_group_criterion,
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc,
                metrics.cost_per_conversion,
                segments.date
            FROM search_term_view
            WHERE segments.date = '{date}'
                AND campaign.status != 'REMOVED'
        """
        # Delete existing search terms for this date (bulk idempotency;
        # covers both Search and PMax inserts below)
        self.db.execute(
            "DELETE FROM act_v2_search_terms WHERE client_id = ? AND snapshot_date = ?",
            [self.client_id, date]
        )

        count = 0
        try:
            for row in self._query(query):
                cost = row.metrics.cost_micros / MICROS
                clicks = row.metrics.clicks
                conversions = row.metrics.conversions

                kw_criterion = row.segments.keyword.ad_group_criterion
                keyword_id = kw_criterion.split('/')[-1] if kw_criterion else None

                self.db.execute(
                    """INSERT INTO act_v2_search_terms
                       (client_id, snapshot_date, campaign_id, campaign_name,
                        campaign_type, ad_group_id, ad_group_name, search_term,
                        match_type, status, keyword_text, keyword_id,
                        cost, impressions, clicks, conversions, conversion_value,
                        ctr, avg_cpc, cost_per_conversion, conversion_rate)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    [self.client_id, date,
                     str(row.campaign.id), row.campaign.name,
                     row.campaign.advertising_channel_type.name,
                     str(row.ad_group.id), row.ad_group.name,
                     row.search_term_view.search_term,
                     row.segments.keyword.info.match_type.name if row.segments.keyword.info.match_type else None,
                     row.search_term_view.status.name if row.search_term_view.status else None,
                     row.segments.keyword.info.text if row.segments.keyword.info.text else None,
                     keyword_id,
                     round(cost, 2),
                     row.metrics.impressions,
                     clicks,
                     round(conversions, 2),
                     round(row.metrics.conversions_value, 2),
                     round(row.metrics.ctr, 6),
                     round(row.metrics.average_cpc / MICROS, 2),
                     round(row.metrics.cost_per_conversion / MICROS, 2),
                     round(_safe_div(conversions, clicks), 4)]
                )
                count += 1
        except GoogleAdsException as e:
            # Search terms may not be available for all campaign types (e.g., PMax)
            err_msg = e.failure.errors[0].message if e.failure.errors else str(e)
            if 'not supported' in err_msg.lower() or 'not compatible' in err_msg.lower():
                logger.warning(f"  Search terms not available for {date}: {err_msg}")
            else:
                raise
        return count

    # -----------------------------------------------------------------------
    # PMax search-term ingestion (campaign_search_term_insight resource)
    # -----------------------------------------------------------------------
    def ingest_pmax_search_terms(self, date: str) -> int:
        """Ingest Performance Max search terms via campaign_search_term_insight.

        Must be called AFTER ingest_search_terms (which clears the day's rows
        in act_v2_search_terms via its delete-then-insert pattern). Per-row
        shape diverges from search_term_view:
          - per PMax campaign, terms come back as category_label (= the term)
          - no ad_group context; store ad_group_id/name = 'PMAX_ASSET_GROUP'
          - no keyword context; keyword_text/keyword_id = NULL
          - synthetic match_type = 'PMAX'
          - cost_micros is PROHIBITED on this resource -> cost = NULL
          - status not surfaced -> NULL
          - category_label='' represents Google's aggregated low-volume
            bucket; skip it (not actionable)

        GAQL quirk: segments.date can only appear when filtering by a single
        campaign_search_term_insight.id. Workaround: filter by campaign_id +
        segments.date without selecting segments.date. Tested working for
        DBD 2026-04-19 on API v23.
        """
        # 1. Find active PMax campaigns for this client on this date
        pmax_rows = self.db.execute(
            """SELECT entity_id, entity_name, metrics_json
               FROM act_v2_snapshots
               WHERE client_id = ? AND snapshot_date = ? AND level = 'campaign'""",
            [self.client_id, date],
        ).fetchall()
        pmax_campaigns = []
        for eid, name, mjson in pmax_rows:
            try:
                meta = json.loads(mjson) if isinstance(mjson, str) else mjson
            except Exception:  # noqa: BLE001
                continue
            if meta.get('campaign_type') == 'PERFORMANCE_MAX' and meta.get('campaign_status') != 'REMOVED':
                pmax_campaigns.append((eid, name))

        if not pmax_campaigns:
            return 0

        count = 0
        for campaign_id, campaign_name in pmax_campaigns:
            query = f"""
                SELECT
                    campaign_search_term_insight.category_label,
                    campaign_search_term_insight.id,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.conversions,
                    metrics.conversions_value,
                    metrics.ctr
                FROM campaign_search_term_insight
                WHERE campaign_search_term_insight.campaign_id = '{campaign_id}'
                  AND segments.date = '{date}'
            """
            try:
                rows = list(self._query(query))
            except GoogleAdsException as e:
                err = e.failure.errors[0].message if e.failure.errors else str(e)
                logger.warning(f"  [pmax-st] skip campaign={campaign_id}: {err[:200]}")
                continue

            for row in rows:
                term = row.campaign_search_term_insight.category_label
                if not term:
                    # Google's aggregated "Other search terms" bucket — skip
                    continue
                clicks = row.metrics.clicks
                conversions = row.metrics.conversions
                self.db.execute(
                    """INSERT INTO act_v2_search_terms
                       (client_id, snapshot_date, campaign_id, campaign_name,
                        campaign_type, ad_group_id, ad_group_name, search_term,
                        match_type, status, keyword_text, keyword_id,
                        cost, impressions, clicks, conversions, conversion_value,
                        ctr, avg_cpc, cost_per_conversion, conversion_rate)
                       VALUES (?, ?, ?, ?, 'PERFORMANCE_MAX',
                               'PMAX_ASSET_GROUP', 'PMAX_ASSET_GROUP', ?,
                               'PMAX', NULL, NULL, NULL,
                               NULL, ?, ?, ?, ?, ?, NULL, NULL, ?)""",
                    [self.client_id, date,
                     str(campaign_id), campaign_name,
                     term,
                     row.metrics.impressions,
                     clicks,
                     round(conversions, 2),
                     round(row.metrics.conversions_value, 2),
                     round(row.metrics.ctr, 6),
                     round(_safe_div(conversions, clicks), 4)],
                )
                count += 1
            logger.info(f"  [pmax-st] {campaign_name}: {len(rows)} rows returned")
        return count

    # -----------------------------------------------------------------------
    # Campaign segments ingestion (device, geo, ad schedule)
    # -----------------------------------------------------------------------
    def ingest_campaign_segments(self, date: str) -> int:
        # Delete existing segments for this date (bulk idempotency)
        self.db.execute(
            "DELETE FROM act_v2_campaign_segments WHERE client_id = ? AND snapshot_date = ?",
            [self.client_id, date]
        )

        total = 0
        total += self._ingest_device_segments(date)
        total += self._ingest_geo_segments(date)
        total += self._ingest_schedule_segments(date)
        return total

    def _ingest_device_segments(self, date: str) -> int:
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                segments.device,
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc,
                metrics.cost_per_conversion,
                segments.date
            FROM campaign
            WHERE segments.date = '{date}'
                AND campaign.status != 'REMOVED'
        """
        count = 0
        for row in self._query(query):
            self._store_segment(date, row.campaign.id, row.campaign.name,
                               'device', row.segments.device.name, row)
            count += 1
        return count

    def _ingest_geo_segments(self, date: str) -> int:
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                geographic_view.country_criterion_id,
                geographic_view.location_type,
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc,
                metrics.cost_per_conversion,
                segments.date
            FROM geographic_view
            WHERE segments.date = '{date}'
                AND campaign.status != 'REMOVED'
        """
        count = 0
        try:
            for row in self._query(query):
                geo_value = f"country_{row.geographic_view.country_criterion_id}"
                self._store_segment(date, row.campaign.id, row.campaign.name,
                                   'geo', geo_value, row)
                count += 1
        except GoogleAdsException as e:
            err_msg = e.failure.errors[0].message if e.failure.errors else str(e)
            logger.warning(f"  Geo segments not available for {date}: {err_msg}")
        return count

    def _ingest_schedule_segments(self, date: str) -> int:
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                segments.hour,
                segments.day_of_week,
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc,
                metrics.cost_per_conversion,
                segments.date
            FROM campaign
            WHERE segments.date = '{date}'
                AND campaign.status != 'REMOVED'
        """
        count = 0
        for row in self._query(query):
            schedule_value = f"{row.segments.day_of_week.name}_h{row.segments.hour}"
            self._store_segment(date, row.campaign.id, row.campaign.name,
                               'ad_schedule', schedule_value, row)
            count += 1
        return count

    def _store_segment(self, date, campaign_id, campaign_name, segment_type, segment_value, row):
        """Store a single campaign segment row."""
        cost = row.metrics.cost_micros / MICROS
        clicks = row.metrics.clicks
        conversions = row.metrics.conversions

        self.db.execute(
            """INSERT INTO act_v2_campaign_segments
               (client_id, snapshot_date, campaign_id, campaign_name,
                segment_type, segment_value, cost, impressions, clicks,
                conversions, conversion_value, ctr, avg_cpc,
                cost_per_conversion, conversion_rate, bid_modifier)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)""",
            [self.client_id, date,
             str(campaign_id), campaign_name,
             segment_type, segment_value,
             round(cost, 2),
             row.metrics.impressions,
             clicks,
             round(conversions, 2),
             round(row.metrics.conversions_value, 2),
             round(row.metrics.ctr, 6),
             round(row.metrics.average_cpc / MICROS, 2),
             round(row.metrics.cost_per_conversion / MICROS, 2),
             round(_safe_div(conversions, clicks), 4)]
        )

    # -----------------------------------------------------------------------
    # Account-level snapshot (aggregated from campaigns, not a separate API call)
    # -----------------------------------------------------------------------
    def ingest_account(self, date: str):
        """Compute account-level snapshot by aggregating campaign snapshots for this date."""
        rows = self.db.execute(
            """SELECT metrics_json FROM act_v2_snapshots
               WHERE client_id = ? AND snapshot_date = ? AND level = 'campaign'""",
            [self.client_id, date]
        ).fetchall()

        if not rows:
            return

        total_cost = 0.0
        total_impressions = 0
        total_clicks = 0
        total_conversions = 0.0
        total_conversion_value = 0.0

        for (metrics_str,) in rows:
            m = json.loads(metrics_str) if isinstance(metrics_str, str) else metrics_str
            total_cost += m.get("cost", 0)
            total_impressions += m.get("impressions", 0)
            total_clicks += m.get("clicks", 0)
            total_conversions += m.get("conversions", 0)
            total_conversion_value += m.get("conversion_value", 0)

        account_metrics = {
            "cost": round(total_cost, 2),
            "impressions": total_impressions,
            "clicks": total_clicks,
            "conversions": round(total_conversions, 2),
            "conversion_value": round(total_conversion_value, 2),
            "ctr": round(_safe_div(total_clicks, total_impressions), 6),
            "avg_cpc": round(_safe_div(total_cost, total_clicks), 2),
            "cost_per_conversion": round(_safe_div(total_cost, total_conversions), 2),
            "conversion_rate": round(_safe_div(total_conversions, total_clicks), 4),
        }
        self._store_snapshot(date, 'account', self.customer_id, 'Account Total', None, account_metrics)

    # -----------------------------------------------------------------------
    # N1a — Negative keyword lists ingestion
    # -----------------------------------------------------------------------
    def _resolve_list_role(self, name: str) -> str | None:
        """Map a Google Ads shared-set NAME to one of the 13 list_role enum values.

        Tolerance rules (brief N1a Q2):
        - case-insensitive
        - 'WORD' / 'WORDS' interchangeable
        - '1 WORD+' == '1 WORD' ('+' is semantic noise)
        - 'Competitors & Brands' canonical competitor prefix
        - '"phrase"' (quoted) vs '[exact]' (bracketed) identify match type

        Returns None when the list name doesn't fit any known role (caller logs
        a WARNING; typical in-the-wild misses are free-form lists like
        'DBD Negs' or 'KMG | Invisalign' which keep list_role = NULL).
        """
        if not name:
            return None
        n = name.lower().strip()

        # Identify match type token first
        has_exact = '[exact]' in n
        has_phrase = '"phrase"' in n

        # Strip the match-type tokens so the rest of the parser can look at the prefix
        core = n.replace('[exact]', '').replace('"phrase"', '').replace('  ', ' ').strip()

        # Competitor family (named 'Competitors & Brands ...')
        if core.startswith('competitors & brands'):
            if has_exact:
                return 'competitor_exact'
            if has_phrase:
                return 'competitor_phrase'
            return None

        # Location family ('Location 1 WORD ...' / 'Location 1 WORD+ ...')
        if core.startswith('location'):
            if has_exact:
                return 'location_exact'
            if has_phrase:
                return 'location_phrase'
            return None

        # N-WORD / N-WORDS family — accept '1 word', '2 words', ..., '5+ words'
        import re
        m = re.match(r'^(\d)\+?\s+words?\+?$', core)
        if m:
            n_words = int(m.group(1))
            if n_words >= 5 and has_exact:
                return '5plus_word_exact'
            if 1 <= n_words <= 4:
                if has_exact:
                    return f'{n_words}_word_exact'
                if has_phrase:
                    return f'{n_words}_word_phrase'
        return None

    def ingest_negative_lists(self, date: str) -> dict:
        """Snapshot current state of negative-keyword lists + individual keywords
        + campaign link status for this client. Called once per ingest_date.

        delete-then-insert pattern by (client_id, snapshot_date) for keywords
        and full overwrite for list rows (they represent current state).

        Returns dict(lists, keywords, unmatched_names).
        """
        # -------------------------------------------------------------------
        # 1. Fetch shared_set rows (negative-keyword lists), ENABLED only
        # -------------------------------------------------------------------
        sets_query = """
            SELECT shared_set.id, shared_set.name, shared_set.status,
                   shared_set.member_count, shared_set.reference_count,
                   shared_set.resource_name
            FROM shared_set
            WHERE shared_set.type = 'NEGATIVE_KEYWORDS'
              AND shared_set.status = 'ENABLED'
        """
        sets = list(self._query(sets_query))

        # -------------------------------------------------------------------
        # 2. Fetch campaign_shared_set links → determine is_linked_to_campaign
        # -------------------------------------------------------------------
        links_query = """
            SELECT campaign.status, campaign_shared_set.status, shared_set.id
            FROM campaign_shared_set
            WHERE shared_set.type = 'NEGATIVE_KEYWORDS'
        """
        linked_set_ids: set[str] = set()
        for row in self._query(links_query):
            # A list is "linked" if at least one ENABLED campaign has an
            # ENABLED link to it (drops REMOVED both sides).
            if (row.campaign.status.name == 'ENABLED'
                    and row.campaign_shared_set.status.name == 'ENABLED'):
                linked_set_ids.add(str(row.shared_set.id))

        # -------------------------------------------------------------------
        # 3. Upsert list rows
        # -------------------------------------------------------------------
        unmatched_names: list[str] = []
        list_count = 0
        # Upsert list rows (do NOT delete: historical keyword snapshots in
        # act_v2_negative_list_keywords FK to list_id; deterministic list_id
        # means we can overwrite in place).
        for s in sets:
            ss = s.shared_set
            google_id = str(ss.id)
            list_id = f"{self.client_id}-gal-{google_id}"  # gal = google-ads-list
            role = self._resolve_list_role(ss.name)
            if role is None:
                unmatched_names.append(ss.name)
                logger.warning(f"  [neg-list] No list_role match for '{ss.name}' (id={google_id}) — left NULL")
            self.db.execute(
                """INSERT OR REPLACE INTO act_v2_negative_keyword_lists
                   (list_id, client_id, google_ads_list_id, list_name,
                    word_count, match_type, list_role, keyword_count,
                    added_manually_count, added_by_act_count,
                    is_linked_to_campaign, last_synced_at)
                   VALUES (?, ?, ?, ?, NULL, NULL, ?, 0, 0, 0, ?, CURRENT_TIMESTAMP)""",
                [list_id, self.client_id, google_id, ss.name,
                 role, google_id in linked_set_ids],
            )
            list_count += 1

        # -------------------------------------------------------------------
        # 4. Fetch + upsert individual negative keywords for each list
        # -------------------------------------------------------------------
        # delete-then-insert pattern for this client + snapshot_date
        self.db.execute(
            "DELETE FROM act_v2_negative_list_keywords WHERE client_id = ? AND snapshot_date = ?",
            [self.client_id, date],
        )
        kw_count = 0
        for s in sets:
            google_id = str(s.shared_set.id)
            list_id = f"{self.client_id}-gal-{google_id}"
            crit_query = f"""
                SELECT shared_criterion.criterion_id,
                       shared_criterion.type,
                       shared_criterion.keyword.text,
                       shared_criterion.keyword.match_type
                FROM shared_criterion
                WHERE shared_set.id = {google_id}
            """
            members = 0
            for row in self._query(crit_query):
                if row.shared_criterion.type_.name != 'KEYWORD':
                    continue
                match_type = row.shared_criterion.keyword.match_type.name  # EXACT/PHRASE/BROAD
                self.db.execute(
                    """INSERT INTO act_v2_negative_list_keywords
                       (list_id, client_id, keyword_text, match_type,
                        google_ads_criterion_id, added_at, added_by, snapshot_date)
                       VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 'unknown', ?)""",
                    [list_id, self.client_id,
                     row.shared_criterion.keyword.text, match_type,
                     str(row.shared_criterion.criterion_id), date],
                )
                members += 1
                kw_count += 1
            # Update keyword_count on the list row
            self.db.execute(
                "UPDATE act_v2_negative_keyword_lists SET keyword_count = ? WHERE list_id = ?",
                [members, list_id],
            )

        logger.info(
            f"  [neg-list] {list_count} lists, {kw_count} keywords, "
            f"{len(linked_set_ids)} linked to active campaigns, "
            f"{len(unmatched_names)} unmatched names"
        )
        return {'lists': list_count, 'keywords': kw_count, 'unmatched_names': unmatched_names}

    def close(self):
        """Close the database connection."""
        if self.db:
            self.db.close()
