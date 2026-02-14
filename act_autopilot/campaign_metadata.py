"""
Campaign metadata cache for fast name lookups.

Provides:
- get_campaign_name(campaign_id) → campaign name
- get_all_campaign_names(customer_id) → dict of {campaign_id: name}
- update_campaign_metadata() → refresh from Google Ads API (optional)

Usage:
    from act_autopilot.campaign_metadata import CampaignMetadata

    metadata = CampaignMetadata(customer_id="9999999999")
    name = metadata.get_campaign_name("3001")
    # Returns: "Stable ROAS 2.0"
"""

import duckdb
from typing import Dict, Optional
from datetime import datetime

from .logging_config import setup_logging

logger = setup_logging(__name__)


class CampaignMetadata:
    """
    Campaign metadata cache with database-backed storage.

    Provides fast campaign name lookups without hitting Google Ads API.
    """

    def __init__(self, customer_id: str, db_path: str = "warehouse.duckdb"):
        """
        Initialize campaign metadata cache.

        Args:
            customer_id: Google Ads customer ID
            db_path: Path to DuckDB database
        """
        self.customer_id = customer_id
        self.db_path = db_path
        self._cache: Optional[Dict[str, str]] = None

        logger.debug(f"CampaignMetadata initialized for customer {customer_id}")

    def get_campaign_name(self, campaign_id: str) -> str:
        """
        Get campaign name for a campaign ID.

        Args:
            campaign_id: Campaign ID

        Returns:
            Campaign name, or "Campaign {campaign_id}" if not found
        """
        # Load cache if not loaded
        if self._cache is None:
            self._load_cache()

        # Return name or default
        name = self._cache.get(campaign_id)

        if name:
            logger.debug(f"Campaign {campaign_id}: {name}")
            return name
        else:
            logger.warning(
                f"Campaign {campaign_id} not found in metadata, using default name"
            )
            return f"Campaign {campaign_id}"

    def get_all_campaign_names(self) -> Dict[str, str]:
        """
        Get all campaign names for this customer.

        Returns:
            Dict of {campaign_id: campaign_name}
        """
        # Load cache if not loaded
        if self._cache is None:
            self._load_cache()

        logger.debug(f"Retrieved {len(self._cache)} campaign names")
        return self._cache.copy()

    def _load_cache(self) -> None:
        """Load campaign metadata from database into memory cache."""
        logger.debug(f"Loading campaign metadata for customer {self.customer_id}")

        con = duckdb.connect(self.db_path, read_only=True)

        try:
            result = con.execute(
                """
                SELECT campaign_id, campaign_name
                FROM analytics.campaign_metadata
                WHERE customer_id = ?
            """,
                [self.customer_id],
            ).fetchall()

            self._cache = {row[0]: row[1] for row in result}

            logger.info(f"Loaded {len(self._cache)} campaigns from metadata cache")

        except Exception as e:
            logger.error(f"Failed to load campaign metadata: {e}")
            logger.warning("Using empty cache - campaign names may not be available")
            self._cache = {}

        finally:
            con.close()

    def refresh_cache(self) -> None:
        """Force reload cache from database."""
        logger.info("Refreshing campaign metadata cache")
        self._cache = None
        self._load_cache()

    def update_metadata(
        self,
        campaign_id: str,
        campaign_name: str,
        campaign_status: Optional[str] = None,
        campaign_type: Optional[str] = None,
    ) -> None:
        """
        Update campaign metadata in database.

        Args:
            campaign_id: Campaign ID
            campaign_name: Campaign name
            campaign_status: Campaign status (ENABLED, PAUSED, REMOVED)
            campaign_type: Campaign type (SEARCH, SHOPPING, PMAX, etc.)
        """
        logger.info(f"Updating metadata for campaign {campaign_id}: {campaign_name}")

        con = duckdb.connect(self.db_path)

        try:
            con.execute(
                """
                INSERT OR REPLACE INTO analytics.campaign_metadata
                (customer_id, campaign_id, campaign_name, campaign_status, campaign_type, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                [
                    self.customer_id,
                    campaign_id,
                    campaign_name,
                    campaign_status,
                    campaign_type,
                    datetime.now(),
                ],
            )

            logger.debug("Metadata updated successfully")

            # Refresh cache
            self.refresh_cache()

        except Exception as e:
            logger.error(f"Failed to update campaign metadata: {e}")

        finally:
            con.close()

    def bulk_update_metadata(self, campaigns: list) -> None:
        """
        Bulk update campaign metadata.

        Args:
            campaigns: List of dicts with keys: campaign_id, campaign_name, campaign_status, campaign_type
        """
        logger.info(f"Bulk updating {len(campaigns)} campaigns")

        con = duckdb.connect(self.db_path)

        try:
            for campaign in campaigns:
                con.execute(
                    """
                    INSERT OR REPLACE INTO analytics.campaign_metadata
                    (customer_id, campaign_id, campaign_name, campaign_status, campaign_type, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    [
                        self.customer_id,
                        campaign["campaign_id"],
                        campaign["campaign_name"],
                        campaign.get("campaign_status"),
                        campaign.get("campaign_type"),
                        datetime.now(),
                    ],
                )

            logger.info(f"Bulk update complete: {len(campaigns)} campaigns")

            # Refresh cache
            self.refresh_cache()

        except Exception as e:
            logger.error(f"Failed to bulk update campaign metadata: {e}")

        finally:
            con.close()


def get_campaign_display_name(
    campaign_id: str,
    campaign_name: Optional[str],
    customer_id: str,
    db_path: str = "warehouse.duckdb",
) -> str:
    """
    Get display name for campaign in format "Name (ID)".

    Args:
        campaign_id: Campaign ID
        campaign_name: Campaign name (if already known)
        customer_id: Customer ID
        db_path: Database path

    Returns:
        Display name like "Stable ROAS 2.0 (3001)"
    """
    # If name provided, use it
    if campaign_name:
        return f"{campaign_name} ({campaign_id})"

    # Otherwise lookup from metadata
    metadata = CampaignMetadata(customer_id, db_path)
    name = metadata.get_campaign_name(campaign_id)

    return f"{name} ({campaign_id})"
