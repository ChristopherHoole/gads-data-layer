"""
Google Ads API write functions for budget changes.

Handles:
- Campaign budget updates
- Error handling (rate limits, permissions, invalid campaigns)
- API response parsing
"""

import logging
from typing import Dict, Any
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

logger = logging.getLogger(__name__)


def update_campaign_budget(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str,
    new_budget_micros: int
) -> Dict[str, Any]:
    """
    Update campaign budget via Google Ads API.
    
    Args:
        client: GoogleAdsClient instance
        customer_id: Google Ads customer ID (digits only)
        campaign_id: Campaign ID (digits only)
        new_budget_micros: New budget in micros (e.g., 100000000 = £100)
        
    Returns:
        dict: {
            'status': 'success' or 'failed',
            'campaign_id': str,
            'old_budget_micros': int,
            'new_budget_micros': int,
            'resource_name': str,
            'error': str or None
        }
        
    Raises:
        GoogleAdsException: API errors
        ValueError: Invalid inputs
    """
    
    # Validate inputs
    if not customer_id or not customer_id.isdigit():
        raise ValueError(f"Invalid customer_id: {customer_id}")
    
    if not campaign_id or not campaign_id.isdigit():
        raise ValueError(f"Invalid campaign_id: {campaign_id}")
    
    if new_budget_micros <= 0:
        raise ValueError(f"Budget must be positive: {new_budget_micros}")
    
    logger.info(f"Updating campaign {campaign_id} budget to {new_budget_micros} micros")
    
    try:
        # Step 1: Get current campaign budget
        campaign_service = client.get_service("CampaignService")
        campaign_resource_name = campaign_service.campaign_path(customer_id, campaign_id)
        
        # Fetch current budget
        ga_service = client.get_service("GoogleAdsService")
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign_budget.amount_micros,
                campaign_budget.resource_name
            FROM campaign
            WHERE campaign.id = {campaign_id}
        """
        
        response = ga_service.search(customer_id=customer_id, query=query)
        
        campaign_row = None
        for row in response:
            campaign_row = row
            break
        
        if not campaign_row:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        old_budget_micros = campaign_row.campaign_budget.amount_micros
        budget_resource_name = campaign_row.campaign_budget.resource_name
        
        logger.info(f"Current budget: {old_budget_micros} micros")
        
        # Step 2: Update budget
        campaign_budget_service = client.get_service("CampaignBudgetService")
        
        # Create budget operation
        campaign_budget_operation = client.get_type("CampaignBudgetOperation")
        campaign_budget = campaign_budget_operation.update
        campaign_budget.resource_name = budget_resource_name
        campaign_budget.amount_micros = new_budget_micros
        
        # Set field mask
        client.copy_from(
            campaign_budget_operation.update_mask,
            client.get_type("google.protobuf.FieldMask"),
        )
        campaign_budget_operation.update_mask.paths.append("amount_micros")
        
        # Execute mutation
        response = campaign_budget_service.mutate_campaign_budgets(
            customer_id=customer_id,
            operations=[campaign_budget_operation]
        )
        
        logger.info(f"Budget updated successfully: {response.results[0].resource_name}")
        
        return {
            'status': 'success',
            'campaign_id': campaign_id,
            'old_budget_micros': old_budget_micros,
            'new_budget_micros': new_budget_micros,
            'resource_name': response.results[0].resource_name,
            'error': None
        }
        
    except GoogleAdsException as ex:
        logger.error(f"Google Ads API error: {ex}")
        
        # Parse error details
        error_msg = f"GoogleAdsException: {ex.error.code().name}"
        
        for error in ex.failure.errors:
            error_msg += f"\n  Error: {error.error_code}"
            if error.message:
                error_msg += f"\n  Message: {error.message}"
            if error.location:
                for field in error.location.field_path_elements:
                    error_msg += f"\n  Field: {field.field_name}"
        
        return {
            'status': 'failed',
            'campaign_id': campaign_id,
            'old_budget_micros': None,
            'new_budget_micros': new_budget_micros,
            'resource_name': None,
            'error': error_msg
        }
        
    except Exception as ex:
        logger.error(f"Unexpected error: {ex}")
        
        return {
            'status': 'failed',
            'campaign_id': campaign_id,
            'old_budget_micros': None,
            'new_budget_micros': new_budget_micros,
            'resource_name': None,
            'error': str(ex)
        }


def load_google_ads_client(config_path: str = "secrets/google-ads.yaml") -> GoogleAdsClient:
    """
    Load Google Ads API client from config file.
    
    Args:
        config_path: Path to google-ads.yaml credentials file
        
    Returns:
        GoogleAdsClient instance
    """
    logger.info(f"Loading Google Ads client from {config_path}")
    
    try:
        client = GoogleAdsClient.load_from_storage(config_path)
        logger.info("Google Ads client loaded successfully")
        return client
        
    except Exception as ex:
        logger.error(f"Failed to load Google Ads client: {ex}")
        raise
