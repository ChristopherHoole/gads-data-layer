"""
Tests the Google Ads API connection.
Run from project root: python -m act_dashboard.data_pipeline.test_api_connection
"""
import sys
from pathlib import Path
from google.ads.googleads.client import GoogleAdsClient

# Derive absolute path to secrets/google-ads.yaml from this file's location
YAML_PATH = str(Path(__file__).resolve().parents[2] / "secrets" / "google-ads.yaml")


def test_connection():
    try:
        client = GoogleAdsClient.load_from_storage(YAML_PATH)
        print("[OK] Client loaded successfully")
    except Exception as e:
        print(f"[FAIL] Failed to load client: {e}")
        sys.exit(1)

    customer_id = "8530211223"  # Objection Experts

    try:
        ga_service = client.get_service("GoogleAdsService")
        query = """
            SELECT campaign.id, campaign.name, campaign.status
            FROM campaign
            WHERE campaign.status != 'REMOVED'
            LIMIT 10
        """
        response = ga_service.search(customer_id=customer_id, query=query)

        campaigns = []
        for row in response:
            campaigns.append({
                "id": row.campaign.id,
                "name": row.campaign.name,
                "status": row.campaign.status.name
            })

        print(f"[OK] API call successful — found {len(campaigns)} campaigns:")
        for c in campaigns:
            print(f"  - {c['name']} ({c['status']})")

    except Exception as e:
        print(f"[FAIL] API call failed: {e}")
        sys.exit(1)

    print("\n[OK] Google Ads API connection verified successfully")


if __name__ == "__main__":
    test_connection()
