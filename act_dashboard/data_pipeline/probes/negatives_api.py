"""N1a Step 1b: enumerate all ENABLED negative lists (names only) so we can
validate name-match dict for list_role."""
from pathlib import Path
from google.ads.googleads.client import GoogleAdsClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
YAML_PATH = str(PROJECT_ROOT / "secrets" / "google-ads.yaml")
DBD = "5380281688"


def main():
    client = GoogleAdsClient.load_from_storage(YAML_PATH)
    svc = client.get_service("GoogleAdsService")
    q = """
        SELECT shared_set.id, shared_set.name, shared_set.status,
               shared_set.member_count, shared_set.reference_count
        FROM shared_set
        WHERE shared_set.type = 'NEGATIVE_KEYWORDS'
        ORDER BY shared_set.name
    """
    rows = list(svc.search(customer_id=DBD, query=q))
    print(f"Total negative-keyword lists: {len(rows)}\n")
    print(f"{'Status':<10} {'Members':>8} {'Refs':>5}  Name")
    print("-" * 80)
    for r in rows:
        s = r.shared_set
        print(f"{s.status.name:<10} {s.member_count:>8} {s.reference_count:>5}  {s.name}")


if __name__ == "__main__":
    main()
