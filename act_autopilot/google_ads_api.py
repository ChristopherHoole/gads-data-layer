"""
Google Ads API integration for campaign modifications.

Handles:
- Budget updates (daily budget changes)
- Bid target updates (tROAS/tCPA changes)
- Client authentication
- Error handling
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from act_autopilot.logging_config import setup_logging

logger = setup_logging(__name__)


def load_google_ads_client(config_path: str) -> GoogleAdsClient:
    """
    Load Google Ads API client from YAML configuration.

    Args:
        config_path: Path to google-ads.yaml file

    Returns:
        GoogleAdsClient instance

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    logger.info(f"Loading Google Ads client from {config_path}")

    try:
        client = GoogleAdsClient.load_from_storage(config_path)
        logger.info("Google Ads client loaded successfully")
        return client
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        raise
    except Exception as e:
        logger.error(f"Failed to load Google Ads client: {str(e)}")
        raise


def update_campaign_budget(
    client: GoogleAdsClient, customer_id: str, campaign_id: str, new_budget_micros: int
) -> dict:
    """
    Update a campaign's daily budget via Google Ads API.

    Args:
        client: GoogleAdsClient instance
        customer_id: Customer ID (digits only, no dashes)
        campaign_id: Campaign ID
        new_budget_micros: New budget in micros (e.g., 100.00 = 100_000_000)

    Returns:
        dict with 'success' and 'message' keys

    Raises:
        GoogleAdsException: If API call fails
    """
    logger.info(f"Updating campaign {campaign_id} budget to {new_budget_micros} micros")

    try:
        campaign_service = client.get_service("CampaignService")
        campaign_budget_service = client.get_service("CampaignBudgetService")

        # Get campaign's budget resource name
        campaign_resource_name = campaign_service.campaign_path(
            customer_id, campaign_id
        )

        # Get current campaign to find budget ID
        ga_service = client.get_service("GoogleAdsService")
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.campaign_budget
            FROM campaign
            WHERE campaign.id = {campaign_id}
        """

        response = ga_service.search(customer_id=customer_id, query=query)

        campaign_budget_resource_name = None
        for row in response:
            campaign_budget_resource_name = row.campaign.campaign_budget
            break

        if not campaign_budget_resource_name:
            raise ValueError(f"Campaign {campaign_id} not found")

        # Create budget operation
        budget_operation = client.get_type("CampaignBudgetOperation")
        budget_operation.update.resource_name = campaign_budget_resource_name
        budget_operation.update.amount_micros = new_budget_micros
        budget_operation.update_mask.paths.append("amount_micros")

        # Execute update
        response = campaign_budget_service.mutate_campaign_budgets(
            customer_id=customer_id, operations=[budget_operation]
        )

        logger.info(f"Budget update successful: {campaign_id}")
        return {
            "success": True,
            "message": f"Budget updated to {new_budget_micros / 1_000_000:.2f}",
            "resource_name": response.results[0].resource_name,
        }

    except GoogleAdsException as ex:
        logger.error(f"Google Ads API error: {ex}")
        error_message = f"Request ID: {ex.request_id}\n"
        for error in ex.failure.errors:
            error_message += f"Error: {error.message}\n"
        raise Exception(error_message)

    except Exception as e:
        logger.error(f"Unexpected error updating budget: {str(e)}")
        raise


def update_campaign_bidding_strategy(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str,
    new_target_value: float,
    bid_type: str = "target_roas",
) -> dict:
    """
    Update a campaign's bidding strategy target (tROAS or tCPA).

    Args:
        client: GoogleAdsClient instance
        customer_id: Customer ID (digits only, no dashes)
        campaign_id: Campaign ID
        new_target_value: New target value (ROAS as decimal, CPA in currency units)
        bid_type: Either 'target_roas' or 'target_cpa'

    Returns:
        dict with 'success' and 'message' keys

    Raises:
        GoogleAdsException: If API call fails
        ValueError: If bid_type is invalid
    """
    logger.info(f"Updating campaign {campaign_id} {bid_type} to {new_target_value}")

    if bid_type not in ["target_roas", "target_cpa"]:
        raise ValueError(
            f"Invalid bid_type: {bid_type}. Must be 'target_roas' or 'target_cpa'"
        )

    try:
        campaign_service = client.get_service("CampaignService")
        campaign_resource_name = campaign_service.campaign_path(
            customer_id, campaign_id
        )

        # Create campaign operation
        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.update
        campaign.resource_name = campaign_resource_name

        # Set the new target value based on bid type
        if bid_type == "target_roas":
            # tROAS is stored as a decimal (e.g., 3.5 = 350% ROAS)
            campaign.target_roas.target_roas = new_target_value
            update_mask_path = "target_roas.target_roas"
            logger.info(f"Setting target_roas to {new_target_value}")

        else:  # target_cpa
            # tCPA is stored in micros
            target_cpa_micros = int(new_target_value * 1_000_000)
            campaign.target_cpa.target_cpa_micros = target_cpa_micros
            update_mask_path = "target_cpa.target_cpa_micros"
            logger.info(
                f"Setting target_cpa to {new_target_value} ({target_cpa_micros} micros)"
            )

        # Set update mask
        campaign_operation.update_mask.paths.append(update_mask_path)

        # Execute update
        response = campaign_service.mutate_campaigns(
            customer_id=customer_id, operations=[campaign_operation]
        )

        logger.info(f"Bid target update successful: {campaign_id}")
        return {
            "success": True,
            "message": f"{bid_type} updated to {new_target_value}",
            "resource_name": response.results[0].resource_name,
        }

    except GoogleAdsException as ex:
        logger.error(f"Google Ads API error: {ex}")
        error_message = f"Request ID: {ex.request_id}\n"
        for error in ex.failure.errors:
            error_message += f"Error: {error.message}\n"
        raise Exception(error_message)

    except Exception as e:
        logger.error(f"Unexpected error updating bid target: {str(e)}")
        raise


def validate_campaign_exists(
    client: GoogleAdsClient, customer_id: str, campaign_id: str
) -> bool:
    """
    Check if a campaign exists.

    Args:
        client: GoogleAdsClient instance
        customer_id: Customer ID
        campaign_id: Campaign ID

    Returns:
        True if campaign exists, False otherwise
    """
    try:
        ga_service = client.get_service("GoogleAdsService")
        query = f"""
            SELECT campaign.id, campaign.name
            FROM campaign
            WHERE campaign.id = {campaign_id}
        """

        response = ga_service.search(customer_id=customer_id, query=query)

        for row in response:
            logger.info(f"Campaign exists: {row.campaign.name} ({campaign_id})")
            return True

        logger.warning(f"Campaign not found: {campaign_id}")
        return False

    except Exception as e:
        logger.error(f"Error validating campaign: {str(e)}")
        return False


def get_campaign_bidding_strategy(
    client: GoogleAdsClient, customer_id: str, campaign_id: str
) -> dict:
    """
    Get current bidding strategy details for a campaign.

    Args:
        client: GoogleAdsClient instance
        customer_id: Customer ID
        campaign_id: Campaign ID

    Returns:
        dict with bidding strategy info or None if not found
    """
    try:
        ga_service = client.get_service("GoogleAdsService")
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.target_roas.target_roas,
                campaign.target_cpa.target_cpa_micros,
                campaign.bidding_strategy_type
            FROM campaign
            WHERE campaign.id = {campaign_id}
        """

        response = ga_service.search(customer_id=customer_id, query=query)

        for row in response:
            campaign = row.campaign

            # Determine bid type and current value
            if campaign.target_roas.target_roas:
                bid_type = "target_roas"
                current_value = campaign.target_roas.target_roas
            elif campaign.target_cpa.target_cpa_micros:
                bid_type = "target_cpa"
                current_value = campaign.target_cpa.target_cpa_micros / 1_000_000
            else:
                bid_type = "unknown"
                current_value = None

            return {
                "campaign_id": str(campaign.id),
                "campaign_name": campaign.name,
                "bid_type": bid_type,
                "current_value": current_value,
                "strategy_type": campaign.bidding_strategy_type.name,
            }

        logger.warning(f"Campaign not found: {campaign_id}")
        return None

    except Exception as e:
        logger.error(f"Error getting bidding strategy: {str(e)}")
        return None
