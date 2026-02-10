import random
from datetime import date, datetime, timezone

def mock_campaign_daily(run_id: str, customer_id: str, snapshot_date: date, seed: int) -> list[dict]:
    rnd = random.Random(seed)
    rows = []
    ingested_at = datetime.now(timezone.utc)

    # Create 5 deterministic campaigns
    for i in range(1, 6):
        impressions = rnd.randint(200, 5000)
        clicks = rnd.randint(10, max(10, impressions // 10))
        cost_micros = rnd.randint(50_000_000, 800_000_000)  # $50 to $800 (micros)
        conversions = round(rnd.random() * 10, 2)
        conv_value = round(conversions * rnd.uniform(20, 200), 2)

        all_conversions = conversions + round(rnd.random() * 2, 2)
        all_conv_value = conv_value + round(rnd.random() * 50, 2)

        rows.append(
            dict(
                run_id=run_id,
                ingested_at=ingested_at,
                customer_id=customer_id,
                snapshot_date=snapshot_date,
                campaign_id=str(1000 + i),
                campaign_name=f"Mock Campaign {i}",
                campaign_status="ENABLED",
                channel_type="SEARCH",
                impressions=impressions,
                clicks=clicks,
                cost_micros=cost_micros,
                conversions=conversions,
                conversions_value=conv_value,
                all_conversions=all_conversions,
                all_conversions_value=all_conv_value,
            )
        )
    return rows

def mock_campaign_config(run_id: str, customer_id: str, seed: int) -> list[dict]:
    rnd = random.Random(seed + 999)
    ingested_at = datetime.now(timezone.utc)
    rows = []
    for i in range(1, 6):
        rows.append(
            dict(
                run_id=run_id,
                ingested_at=ingested_at,
                customer_id=customer_id,
                campaign_id=str(1000 + i),
                campaign_name=f"Mock Campaign {i}",
                campaign_status="ENABLED",
                channel_type="SEARCH",
                bidding_strategy_type="MAXIMIZE_CONVERSIONS",
                budget_amount=round(rnd.uniform(10, 100), 2),
            )
        )
    return rows
