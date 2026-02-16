"""
Google Ads API integration for campaign modifications.

Handles:
- Budget updates (daily budget changes)
- Bid target updates (tROAS/tCPA changes)
- Keyword operations (add, pause, bid updates, negatives)
- Ad operations (pause, enable)
- Shopping operations (bid updates, product exclusions)
- Client authentication
- Error handling
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.api_core import protobuf_helpers
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


# ============================================================================
# CAMPAIGN OPERATIONS (EXISTING)
# ============================================================================


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


# ============================================================================
# KEYWORD OPERATIONS (NEW - CHAT 13)
# ============================================================================


def add_keyword(
    client: GoogleAdsClient,
    customer_id: str,
    ad_group_id: str,
    keyword_text: str,
    match_type: str,
    bid_micros: int,
    dry_run: bool = True,
) -> dict:
    """
    Add a new keyword to an ad group.

    Args:
        client: GoogleAdsClient instance
        customer_id: Customer ID
        ad_group_id: Ad group ID
        keyword_text: Keyword text (e.g., "running shoes")
        match_type: EXACT, PHRASE, or BROAD
        bid_micros: Initial CPC bid in micros (REQUIRED - Q1 answer)
        dry_run: If True, validate only without making changes

    Returns:
        dict with keyword_id, status

    Raises:
        GoogleAdsException: If API call fails
    """
    if dry_run:
        logger.info(
            f"DRY RUN: Would add keyword '{keyword_text}' ({match_type}) "
            f"to ad group {ad_group_id} with bid {bid_micros}"
        )
        return {
            "keyword_id": f"simulated_{ad_group_id}_{keyword_text}",
            "keyword_text": keyword_text,
            "match_type": match_type,
            "bid_micros": bid_micros,
            "status": "dry_run",
        }

    ad_group_criterion_service = client.get_service("AdGroupCriterionService")

    # Map match type to API enum
    match_type_enum = client.enums.KeywordMatchTypeEnum
    match_type_map = {
        "EXACT": match_type_enum.EXACT,
        "PHRASE": match_type_enum.PHRASE,
        "BROAD": match_type_enum.BROAD,
    }

    if match_type not in match_type_map:
        raise ValueError(f"Invalid match_type: {match_type}")

    try:
        # Create keyword criterion
        operation = client.get_type("AdGroupCriterionOperation")
        criterion = operation.create
        criterion.ad_group = ad_group_criterion_service.ad_group_path(
            customer_id, ad_group_id
        )
        criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        criterion.keyword.text = keyword_text
        criterion.keyword.match_type = match_type_map[match_type]
        criterion.cpc_bid_micros = bid_micros

        response = ad_group_criterion_service.mutate_ad_group_criteria(
            customer_id=customer_id, operations=[operation]
        )

        keyword_id = response.results[0].resource_name.split("/")[-1]
        logger.info(
            f"Added keyword '{keyword_text}' ({match_type}) with ID {keyword_id}"
        )

        return {
            "keyword_id": keyword_id,
            "keyword_text": keyword_text,
            "match_type": match_type,
            "bid_micros": bid_micros,
            "status": "success",
        }

    except GoogleAdsException as ex:
        logger.error(f"Failed to add keyword: {ex}")
        raise


def pause_keyword(
    client: GoogleAdsClient,
    customer_id: str,
    ad_group_id: str,
    keyword_id: str,
    dry_run: bool = True,
) -> dict:
    """
    Pause a keyword (set status to PAUSED).

    Args:
        client: GoogleAdsClient instance
        customer_id: Customer ID
        ad_group_id: Ad group ID
        keyword_id: Keyword criterion ID
        dry_run: If True, validate only

    Returns:
        dict with status

    Raises:
        GoogleAdsException: If API call fails
    """
    if dry_run:
        logger.info(f"DRY RUN: Would pause keyword {keyword_id} in ad group {ad_group_id}")
        return {"keyword_id": keyword_id, "status": "dry_run"}

    ad_group_criterion_service = client.get_service("AdGroupCriterionService")

    try:
        operation = client.get_type("AdGroupCriterionOperation")
        criterion = operation.update
        criterion.resource_name = ad_group_criterion_service.ad_group_criterion_path(
            customer_id, ad_group_id, keyword_id
        )
        criterion.status = client.enums.AdGroupCriterionStatusEnum.PAUSED

        field_mask = protobuf_helpers.field_mask(None, criterion._pb)
        operation.update_mask.CopyFrom(field_mask)

        response = ad_group_criterion_service.mutate_ad_group_criteria(
            customer_id=customer_id, operations=[operation]
        )

        logger.info(f"Paused keyword {keyword_id}")
        return {"keyword_id": keyword_id, "status": "success"}

    except GoogleAdsException as ex:
        logger.error(f"Failed to pause keyword: {ex}")
        raise


def update_keyword_bid(
    client: GoogleAdsClient,
    customer_id: str,
    ad_group_id: str,
    keyword_id: str,
    new_bid_micros: int,
    dry_run: bool = True,
) -> dict:
    """
    Update keyword CPC bid.

    Args:
        client: GoogleAdsClient instance
        customer_id: Customer ID
        ad_group_id: Ad group ID
        keyword_id: Keyword criterion ID
        new_bid_micros: New bid in micros
        dry_run: If True, validate only

    Returns:
        dict with old_bid, new_bid, status

    Raises:
        GoogleAdsException: If API call fails
    """
    if dry_run:
        logger.info(
            f"DRY RUN: Would update keyword {keyword_id} bid to {new_bid_micros}"
        )
        return {
            "keyword_id": keyword_id,
            "old_bid_micros": 1500000,  # Simulated old bid
            "new_bid_micros": new_bid_micros,
            "status": "dry_run",
        }
    
    ad_group_criterion_service = client.get_service("AdGroupCriterionService")

    # Get current bid
    ga_service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
            ad_group_criterion.criterion_id,
            ad_group_criterion.cpc_bid_micros
        FROM ad_group_criterion
        WHERE ad_group_criterion.criterion_id = {keyword_id}
            AND ad_group_criterion.ad_group = 'customers/{customer_id}/adGroups/{ad_group_id}'
    """

    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        row = next(iter(response))
        old_bid_micros = row.ad_group_criterion.cpc_bid_micros

        # Update bid
        operation = client.get_type("AdGroupCriterionOperation")
        criterion = operation.update
        criterion.resource_name = ad_group_criterion_service.ad_group_criterion_path(
            customer_id, ad_group_id, keyword_id
        )
        criterion.cpc_bid_micros = new_bid_micros

        field_mask = protobuf_helpers.field_mask(None, criterion._pb)
        operation.update_mask.CopyFrom(field_mask)

        response = ad_group_criterion_service.mutate_ad_group_criteria(
            customer_id=customer_id, operations=[operation]
        )

        logger.info(
            f"Updated keyword {keyword_id} bid from {old_bid_micros} to {new_bid_micros}"
        )
        return {
            "keyword_id": keyword_id,
            "old_bid_micros": old_bid_micros,
            "new_bid_micros": new_bid_micros,
            "status": "success",
        }

    except GoogleAdsException as ex:
        logger.error(f"Failed to update keyword bid: {ex}")
        raise


def add_negative_keyword(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str,
    keyword_text: str,
    match_type: str,
    dry_run: bool = True,
) -> dict:
    """
    Add campaign-level negative keyword.

    Args:
        client: GoogleAdsClient instance
        customer_id: Customer ID
        campaign_id: Campaign ID
        keyword_text: Negative keyword text
        match_type: EXACT, PHRASE, or BROAD
        dry_run: If True, validate only

    Returns:
        dict with negative_keyword_id, status

    Raises:
        GoogleAdsException: If API call fails
    """
    if dry_run:
        logger.info(
            f"DRY RUN: Would add negative keyword '{keyword_text}' ({match_type}) "
            f"to campaign {campaign_id}"
        )
        return {
            "negative_keyword_id": f"simulated_neg_{campaign_id}_{keyword_text}",
            "keyword_text": keyword_text,
            "match_type": match_type,
            "status": "dry_run",
        }

    campaign_criterion_service = client.get_service("CampaignCriterionService")

    # Map match type to API enum
    match_type_enum = client.enums.KeywordMatchTypeEnum
    match_type_map = {
        "EXACT": match_type_enum.EXACT,
        "PHRASE": match_type_enum.PHRASE,
        "BROAD": match_type_enum.BROAD,
    }

    if match_type not in match_type_map:
        raise ValueError(f"Invalid match_type: {match_type}")

    try:
        operation = client.get_type("CampaignCriterionOperation")
        criterion = operation.create
        criterion.campaign = campaign_criterion_service.campaign_path(
            customer_id, campaign_id
        )
        criterion.negative = True
        criterion.keyword.text = keyword_text
        criterion.keyword.match_type = match_type_map[match_type]

        response = campaign_criterion_service.mutate_campaign_criteria(
            customer_id=customer_id, operations=[operation]
        )

        negative_keyword_id = response.results[0].resource_name.split("/")[-1]
        logger.info(
            f"Added negative keyword '{keyword_text}' ({match_type}) "
            f"with ID {negative_keyword_id}"
        )

        return {
            "negative_keyword_id": negative_keyword_id,
            "keyword_text": keyword_text,
            "match_type": match_type,
            "status": "success",
        }

    except GoogleAdsException as ex:
        logger.error(f"Failed to add negative keyword: {ex}")
        raise


# ============================================================================
# AD OPERATIONS (NEW - CHAT 13)
# ============================================================================


def pause_ad(
    client: GoogleAdsClient,
    customer_id: str,
    ad_group_id: str,
    ad_id: str,
    dry_run: bool = True,
) -> dict:
    """
    Pause an ad (set status to PAUSED).

    Args:
        client: GoogleAdsClient instance
        customer_id: Customer ID
        ad_group_id: Ad group ID
        ad_id: Ad ID
        dry_run: If True, validate only

    Returns:
        dict with status

    Raises:
        GoogleAdsException: If API call fails
    """
    if dry_run:
        logger.info(f"DRY RUN: Would pause ad {ad_id} in ad group {ad_group_id}")
        return {"ad_id": ad_id, "status": "dry_run"}

    ad_group_ad_service = client.get_service("AdGroupAdService")

    try:
        operation = client.get_type("AdGroupAdOperation")
        ad_group_ad = operation.update
        ad_group_ad.resource_name = ad_group_ad_service.ad_group_ad_path(
            customer_id, ad_group_id, ad_id
        )
        ad_group_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED

        field_mask = protobuf_helpers.field_mask(None, ad_group_ad._pb)
        operation.update_mask.CopyFrom(field_mask)

        response = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id, operations=[operation]
        )

        logger.info(f"Paused ad {ad_id}")
        return {"ad_id": ad_id, "status": "success"}

    except GoogleAdsException as ex:
        logger.error(f"Failed to pause ad: {ex}")
        raise


def enable_ad(
    client: GoogleAdsClient,
    customer_id: str,
    ad_group_id: str,
    ad_id: str,
    dry_run: bool = True,
) -> dict:
    """
    Enable an ad (set status to ENABLED).

    NOTE: Q2 answer (A) - Performance check (CTR improved ≥20%)
    is enforced in Executor validation, not here.

    Args:
        client: GoogleAdsClient instance
        customer_id: Customer ID
        ad_group_id: Ad group ID
        ad_id: Ad ID
        dry_run: If True, validate only

    Returns:
        dict with status

    Raises:
        GoogleAdsException: If API call fails
    """
    if dry_run:
        logger.info(f"DRY RUN: Would enable ad {ad_id} in ad group {ad_group_id}")
        return {"ad_id": ad_id, "status": "dry_run"}

    ad_group_ad_service = client.get_service("AdGroupAdService")

    try:
        operation = client.get_type("AdGroupAdOperation")
        ad_group_ad = operation.update
        ad_group_ad.resource_name = ad_group_ad_service.ad_group_ad_path(
            customer_id, ad_group_id, ad_id
        )
        ad_group_ad.status = client.enums.AdGroupAdStatusEnum.ENABLED

        field_mask = protobuf_helpers.field_mask(None, ad_group_ad._pb)
        operation.update_mask.CopyFrom(field_mask)

        response = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id, operations=[operation]
        )

        logger.info(f"Enabled ad {ad_id}")
        return {"ad_id": ad_id, "status": "success"}

    except GoogleAdsException as ex:
        logger.error(f"Failed to enable ad: {ex}")
        raise


# ============================================================================
# SHOPPING OPERATIONS (NEW - CHAT 13)
# ============================================================================


def update_product_partition_bid(
    client: GoogleAdsClient,
    customer_id: str,
    ad_group_id: str,
    partition_id: str,
    new_bid_micros: int,
    dry_run: bool = True,
) -> dict:
    """
    Update Shopping product partition bid.

    Args:
        client: GoogleAdsClient instance
        customer_id: Customer ID
        ad_group_id: Ad group ID
        partition_id: Product partition criterion ID
        new_bid_micros: New bid in micros
        dry_run: If True, validate only

    Returns:
        dict with old_bid, new_bid, status

    Raises:
        GoogleAdsException: If API call fails
    """
    if dry_run:
        logger.info(
            f"DRY RUN: Would update product partition {partition_id} bid to {new_bid_micros}"
        )
        return {
            "partition_id": partition_id,
            "old_bid_micros": 2000000,  # Simulated old bid
            "new_bid_micros": new_bid_micros,
            "status": "dry_run",
        }
    
    ad_group_criterion_service = client.get_service("AdGroupCriterionService")

    # Get current bid
    ga_service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
            ad_group_criterion.criterion_id,
            ad_group_criterion.cpc_bid_micros
        FROM ad_group_criterion
        WHERE ad_group_criterion.criterion_id = {partition_id}
            AND ad_group_criterion.ad_group = 'customers/{customer_id}/adGroups/{ad_group_id}'
            AND ad_group_criterion.type = 'LISTING_GROUP'
    """

    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        row = next(iter(response))
        old_bid_micros = row.ad_group_criterion.cpc_bid_micros

        # Update bid
        operation = client.get_type("AdGroupCriterionOperation")
        criterion = operation.update
        criterion.resource_name = ad_group_criterion_service.ad_group_criterion_path(
            customer_id, ad_group_id, partition_id
        )
        criterion.cpc_bid_micros = new_bid_micros

        field_mask = protobuf_helpers.field_mask(None, criterion._pb)
        operation.update_mask.CopyFrom(field_mask)

        response = ad_group_criterion_service.mutate_ad_group_criteria(
            customer_id=customer_id, operations=[operation]
        )

        logger.info(
            f"Updated product partition {partition_id} bid from {old_bid_micros} to {new_bid_micros}"
        )
        return {
            "partition_id": partition_id,
            "old_bid_micros": old_bid_micros,
            "new_bid_micros": new_bid_micros,
            "status": "success",
        }

    except GoogleAdsException as ex:
        logger.error(f"Failed to update product partition bid: {ex}")
        raise


def exclude_product(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str,
    product_id: str,
    dry_run: bool = True,
) -> dict:
    """
    Add campaign-level negative product target (Q3 answer: A - campaign-level).

    Args:
        client: GoogleAdsClient instance
        customer_id: Customer ID
        campaign_id: Campaign ID
        product_id: Product ID to exclude
        dry_run: If True, validate only

    Returns:
        dict with exclusion_id, status

    Raises:
        GoogleAdsException: If API call fails
    """
    if dry_run:
        logger.info(
            f"DRY RUN: Would exclude product {product_id} from campaign {campaign_id}"
        )
        return {
            "exclusion_id": f"simulated_excl_{campaign_id}_{product_id}",
            "product_id": product_id,
            "status": "dry_run",
        }

    campaign_criterion_service = client.get_service("CampaignCriterionService")

    try:
        operation = client.get_type("CampaignCriterionOperation")
        criterion = operation.create
        criterion.campaign = campaign_criterion_service.campaign_path(
            customer_id, campaign_id
        )
        criterion.negative = True

        # Set product scope (specific product exclusion)
        dimension = client.get_type("ListingScopeDimension")
        dimension.product_item_id.value = product_id
        criterion.listing_scope.dimensions.append(dimension)

        response = campaign_criterion_service.mutate_campaign_criteria(
            customer_id=customer_id, operations=[operation]
        )

        exclusion_id = response.results[0].resource_name.split("/")[-1]
        logger.info(f"Excluded product {product_id} with exclusion ID {exclusion_id}")

        return {
            "exclusion_id": exclusion_id,
            "product_id": product_id,
            "status": "success",
        }

    except GoogleAdsException as ex:
        logger.error(f"Failed to exclude product: {ex}")
        raise


# ============================================================================
# HELPER METHODS (NEW - CHAT 13)
# ============================================================================


def get_ad_group_keywords(
    client: GoogleAdsClient, customer_id: str, ad_group_id: str, date_range_days: int = 30
) -> list:
    """
    Fetch all keywords for an ad group.

    Args:
        client: GoogleAdsClient instance
        customer_id: Customer ID
        ad_group_id: Ad group ID
        date_range_days: Number of days for metrics

    Returns:
        List of keyword dictionaries

    Raises:
        GoogleAdsException: If API call fails
    """
    ga_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT
            ad_group_criterion.criterion_id,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group_criterion.status,
            ad_group_criterion.cpc_bid_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM ad_group_criterion
        WHERE ad_group_criterion.ad_group = 'customers/{customer_id}/adGroups/{ad_group_id}'
            AND ad_group_criterion.type = 'KEYWORD'
            AND segments.date DURING LAST_{date_range_days}_DAYS
    """

    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        keywords = []

        for row in response:
            keywords.append(
                {
                    "keyword_id": row.ad_group_criterion.criterion_id,
                    "keyword_text": row.ad_group_criterion.keyword.text,
                    "match_type": row.ad_group_criterion.keyword.match_type.name,
                    "status": row.ad_group_criterion.status.name,
                    "bid_micros": row.ad_group_criterion.cpc_bid_micros,
                    "impressions": row.metrics.impressions,
                    "clicks": row.metrics.clicks,
                    "cost_micros": row.metrics.cost_micros,
                    "conversions": row.metrics.conversions,
                }
            )

        return keywords

    except GoogleAdsException as ex:
        logger.error(f"Failed to fetch ad group keywords: {ex}")
        raise


def get_ad_group_ads(
    client: GoogleAdsClient, customer_id: str, ad_group_id: str, date_range_days: int = 30
) -> list:
    """
    Fetch all ads for an ad group.

    Args:
        client: GoogleAdsClient instance
        customer_id: Customer ID
        ad_group_id: Ad group ID
        date_range_days: Number of days for metrics

    Returns:
        List of ad dictionaries

    Raises:
        GoogleAdsException: If API call fails
    """
    ga_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT
            ad_group_ad.ad.id,
            ad_group_ad.ad.type,
            ad_group_ad.status,
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.conversions,
            metrics.cost_micros
        FROM ad_group_ad
        WHERE ad_group_ad.ad_group = 'customers/{customer_id}/adGroups/{ad_group_id}'
            AND segments.date DURING LAST_{date_range_days}_DAYS
    """

    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        ads = []

        for row in response:
            ads.append(
                {
                    "ad_id": row.ad_group_ad.ad.id,
                    "ad_type": row.ad_group_ad.ad.type_.name,
                    "status": row.ad_group_ad.status.name,
                    "impressions": row.metrics.impressions,
                    "clicks": row.metrics.clicks,
                    "ctr": row.metrics.ctr,
                    "conversions": row.metrics.conversions,
                    "cost_micros": row.metrics.cost_micros,
                }
            )

        return ads

    except GoogleAdsException as ex:
        logger.error(f"Failed to fetch ad group ads: {ex}")
        raise
