"""
Synthetic data generator v2 - 20 campaigns, 365 days
Generates realistic Google Ads campaign data for testing
"""

import random
import math
from datetime import date, timedelta
from pathlib import Path
import duckdb

# Configuration
CUSTOMER_ID = "9999999999"
START_DATE = date(2025, 2, 13)
END_DATE = date(2026, 2, 12)
DAYS = 365

# Campaign scenarios (20 total)
CAMPAIGNS = [
    # 4 Stable (different ROAS levels)
    {"id": "3001", "name": "Stable ROAS 2.0", "scenario": "stable", "target_roas": 2.0},
    {"id": "3002", "name": "Stable ROAS 3.0", "scenario": "stable", "target_roas": 3.0},
    {"id": "3003", "name": "Stable ROAS 4.0", "scenario": "stable", "target_roas": 4.0},
    {"id": "3004", "name": "Stable ROAS 5.0", "scenario": "stable", "target_roas": 5.0},
    
    # 3 Growth (improving over time)
    {"id": "3005", "name": "Growth Strong", "scenario": "growth", "growth_rate": 0.002},
    {"id": "3006", "name": "Growth Moderate", "scenario": "growth", "growth_rate": 0.001},
    {"id": "3007", "name": "Growth Slow", "scenario": "growth", "growth_rate": 0.0005},
    
    # 3 Decline (degrading over time)
    {"id": "3008", "name": "Decline Fast", "scenario": "decline", "decline_rate": 0.002},
    {"id": "3009", "name": "Decline Moderate", "scenario": "decline", "decline_rate": 0.001},
    {"id": "3010", "name": "Decline Slow", "scenario": "decline", "decline_rate": 0.0005},
    
    # 2 Seasonal (Q4 peaks, Q2 troughs)
    {"id": "3011", "name": "Seasonal High Amplitude", "scenario": "seasonal", "amplitude": 0.5},
    {"id": "3012", "name": "Seasonal Low Amplitude", "scenario": "seasonal", "amplitude": 0.25},
    
    # 3 Volatile (high day-to-day variance)
    {"id": "3013", "name": "Volatile High", "scenario": "volatile", "volatility": 0.4},
    {"id": "3014", "name": "Volatile Medium", "scenario": "volatile", "volatility": 0.25},
    {"id": "3015", "name": "Volatile Low", "scenario": "volatile", "volatility": 0.15},
    
    # 2 Low-data (consistently < 30 clicks/7d)
    {"id": "3016", "name": "Low Data Micro", "scenario": "low_data", "scale": 0.1},
    {"id": "3017", "name": "Low Data Small", "scenario": "low_data", "scale": 0.2},
    
    # 2 Budget-constrained (lost IS budget > 15%)
    {"id": "3018", "name": "Budget Constrained High", "scenario": "budget_constrained", "lost_is": 0.25},
    {"id": "3019", "name": "Budget Constrained Medium", "scenario": "budget_constrained", "lost_is": 0.18},
    
    # 1 Recovery (bad first 6 months → good last 6 months)
    {"id": "3020", "name": "Recovery Turnaround", "scenario": "recovery"},
]


def generate_stable(campaign, day_index, base_metrics):
    """Stable performance with minor daily noise"""
    target_roas = campaign.get("target_roas", 3.0)
    noise = random.uniform(0.95, 1.05)
    
    impressions = int(base_metrics["impressions"] * noise)
    clicks = int(base_metrics["clicks"] * noise)
    cost = base_metrics["cost"] * noise
    
    # ROAS around target with small variance
    roas_multiplier = random.uniform(0.9, 1.1)
    conversions = clicks * base_metrics["cvr"] * noise
    conv_value = cost * target_roas * roas_multiplier
    
    return impressions, clicks, cost, conversions, conv_value


def generate_growth(campaign, day_index, base_metrics):
    """Improving performance over time"""
    growth_rate = campaign.get("growth_rate", 0.001)
    growth_factor = 1 + (day_index * growth_rate)
    noise = random.uniform(0.95, 1.05)
    
    impressions = int(base_metrics["impressions"] * growth_factor * noise)
    clicks = int(base_metrics["clicks"] * growth_factor * noise)
    cost = base_metrics["cost"] * growth_factor * noise
    
    # Improving CVR and ROAS over time
    cvr = base_metrics["cvr"] * (1 + day_index * growth_rate * 0.5)
    roas = base_metrics["roas"] * (1 + day_index * growth_rate * 0.3)
    
    conversions = clicks * cvr * noise
    conv_value = cost * roas * noise
    
    return impressions, clicks, cost, conversions, conv_value


def generate_decline(campaign, day_index, base_metrics):
    """Degrading performance over time"""
    decline_rate = campaign.get("decline_rate", 0.001)
    decline_factor = 1 - (day_index * decline_rate)
    decline_factor = max(decline_factor, 0.4)  # Floor at 40%
    noise = random.uniform(0.95, 1.05)
    
    impressions = int(base_metrics["impressions"] * decline_factor * noise)
    clicks = int(base_metrics["clicks"] * decline_factor * noise)
    cost = base_metrics["cost"] * decline_factor * noise
    
    # Declining CVR and ROAS
    cvr = base_metrics["cvr"] * decline_factor
    roas = base_metrics["roas"] * decline_factor
    
    conversions = clicks * cvr * noise
    conv_value = cost * roas * noise
    
    return impressions, clicks, cost, conversions, conv_value


def generate_seasonal(campaign, day_index, base_metrics):
    """Seasonal pattern - Q4 peaks, Q2 troughs"""
    amplitude = campaign.get("amplitude", 0.3)
    
    # Seasonal wave: peaks around day 300 (Q4), troughs around day 120 (Q2)
    seasonal_factor = 1 + amplitude * math.sin((day_index - 120) * 2 * math.pi / 365)
    noise = random.uniform(0.95, 1.05)
    
    impressions = int(base_metrics["impressions"] * seasonal_factor * noise)
    clicks = int(base_metrics["clicks"] * seasonal_factor * noise)
    cost = base_metrics["cost"] * seasonal_factor * noise
    
    conversions = clicks * base_metrics["cvr"] * noise
    conv_value = cost * base_metrics["roas"] * noise
    
    return impressions, clicks, cost, conversions, conv_value


def generate_volatile(campaign, day_index, base_metrics):
    """High day-to-day variance"""
    volatility = campaign.get("volatility", 0.3)
    noise = random.uniform(1 - volatility, 1 + volatility)
    
    impressions = int(base_metrics["impressions"] * noise)
    clicks = int(base_metrics["clicks"] * noise)
    cost = base_metrics["cost"] * noise
    
    conversions = clicks * base_metrics["cvr"] * random.uniform(0.7, 1.3)
    conv_value = cost * base_metrics["roas"] * random.uniform(0.7, 1.3)
    
    return impressions, clicks, cost, conversions, conv_value


def generate_low_data(campaign, day_index, base_metrics):
    """Consistently low volume (< 30 clicks/7d)"""
    scale = campaign.get("scale", 0.15)
    noise = random.uniform(0.8, 1.2)
    
    impressions = int(base_metrics["impressions"] * scale * noise)
    clicks = int(base_metrics["clicks"] * scale * noise)
    cost = base_metrics["cost"] * scale * noise
    
    conversions = clicks * base_metrics["cvr"] * noise
    conv_value = cost * base_metrics["roas"] * noise
    
    return impressions, clicks, cost, conversions, conv_value


def generate_budget_constrained(campaign, day_index, base_metrics):
    """High lost IS budget"""
    lost_is = campaign.get("lost_is", 0.2)
    noise = random.uniform(0.95, 1.05)
    
    impressions = int(base_metrics["impressions"] * noise)
    clicks = int(base_metrics["clicks"] * noise)
    cost = base_metrics["cost"] * noise
    
    conversions = clicks * base_metrics["cvr"] * noise
    conv_value = cost * base_metrics["roas"] * noise
    
    # Add lost IS budget data (will be handled separately)
    return impressions, clicks, cost, conversions, conv_value


def generate_recovery(campaign, day_index, base_metrics):
    """Bad first 6 months → good last 6 months"""
    midpoint = DAYS / 2
    
    if day_index < midpoint:
        # First half: poor performance
        factor = 0.5 + (day_index / midpoint) * 0.3  # 0.5 → 0.8
        roas_mult = 0.6
    else:
        # Second half: strong recovery
        progress = (day_index - midpoint) / midpoint
        factor = 0.8 + progress * 0.4  # 0.8 → 1.2
        roas_mult = 0.6 + progress * 0.8  # 0.6 → 1.4
    
    noise = random.uniform(0.95, 1.05)
    
    impressions = int(base_metrics["impressions"] * factor * noise)
    clicks = int(base_metrics["clicks"] * factor * noise)
    cost = base_metrics["cost"] * factor * noise
    
    conversions = clicks * base_metrics["cvr"] * noise
    conv_value = cost * base_metrics["roas"] * roas_mult * noise
    
    return impressions, clicks, cost, conversions, conv_value


def generate_campaign_day(campaign, current_date, day_index):
    """Generate one day of data for a campaign"""
    scenario = campaign["scenario"]
    
    # Base metrics (average daily)
    base_metrics = {
        "impressions": 5000,
        "clicks": 150,
        "cost": 120.0,
        "cvr": 0.08,
        "roas": 3.0,
    }
    
    # Generate based on scenario
    generators = {
        "stable": generate_stable,
        "growth": generate_growth,
        "decline": generate_decline,
        "seasonal": generate_seasonal,
        "volatile": generate_volatile,
        "low_data": generate_low_data,
        "budget_constrained": generate_budget_constrained,
        "recovery": generate_recovery,
    }
    
    generator = generators.get(scenario, generate_stable)
    impressions, clicks, cost, conversions, conv_value = generator(campaign, day_index, base_metrics)
    
    # Calculate derived metrics
    ctr = clicks / impressions if impressions > 0 else 0
    cpc = cost / clicks if clicks > 0 else 0
    cvr = conversions / clicks if clicks > 0 else 0
    cpa = cost / conversions if conversions > 0 else 0
    roas = conv_value / cost if cost > 0 else 0
    
    # Lost IS budget (higher for budget_constrained scenarios)
    if scenario == "budget_constrained":
        lost_is_budget = campaign.get("lost_is", 0.2) + random.uniform(-0.05, 0.05)
        lost_is_budget = max(0, min(lost_is_budget, 0.5))
    else:
        lost_is_budget = random.uniform(0.02, 0.08)
    
    # Lost IS rank
    lost_is_rank = random.uniform(0.05, 0.15)
    
    return {
        "customer_id": CUSTOMER_ID,
        "snapshot_date": current_date,
        "campaign_id": campaign["id"],
        "campaign_name": campaign["name"],
        "campaign_status": "ENABLED",
        "impressions": impressions,
        "clicks": clicks,
        "cost_micros": int(cost * 1_000_000),
        "conversions": round(conversions, 2),
        "conversions_value": round(conv_value, 2),
        "ctr": round(ctr, 4),
        "cpc": round(cpc, 2),
        "cpm": round((cost / impressions * 1000), 2) if impressions > 0 else 0,
        "cvr": round(cvr, 4),
        "cpa": round(cpa, 2) if conversions > 0 else None,
        "roas": round(roas, 2),
        "search_impression_share": round(random.uniform(0.6, 0.9), 4),
        "search_budget_lost_impression_share": round(lost_is_budget, 4),
        "search_rank_lost_impression_share": round(lost_is_rank, 4),
    }


def generate_all_data():
    """Generate 20 campaigns × 365 days = 7,300 rows"""
    rows = []
    
    for day_index in range(DAYS):
        current_date = START_DATE + timedelta(days=day_index)
        
        for campaign in CAMPAIGNS:
            row = generate_campaign_day(campaign, current_date, day_index)
            rows.append(row)
    
    return rows


def write_to_duckdb(rows):
    """Write to warehouse.duckdb"""
    db_path = Path("warehouse.duckdb")
    
    conn = duckdb.connect(str(db_path))
    
    # Clear existing synthetic data from BASE TABLE
    conn.execute("DELETE FROM snap_campaign_daily WHERE customer_id = '9999999999'")
    
    # Insert into BASE TABLE (only raw columns)
    insert_sql = """
        INSERT INTO snap_campaign_daily (
            run_id, ingested_at, customer_id, snapshot_date, campaign_id, campaign_name, campaign_status,
            channel_type, impressions, clicks, cost_micros, conversions, conversions_value,
            all_conversions, all_conversions_value
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    # Insert in batches
    batch_size = 1000
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        
        for row in batch:
            conn.execute(insert_sql, [
                'synthetic-v2',  # run_id
                '2026-02-12 10:00:00',  # ingested_at
                row["customer_id"],
                row["snapshot_date"],
                row["campaign_id"],
                row["campaign_name"],
                row["campaign_status"],
                'SEARCH',  # channel_type
                row["impressions"],
                row["clicks"],
                row["cost_micros"],
                row["conversions"],
                row["conversions_value"],
                row["conversions"],  # all_conversions (same as conversions)
                row["conversions_value"],  # all_conversions_value
            ])
        
        if (i + batch_size) % 1000 == 0:
            print(f"  Inserted {min(i + batch_size, len(rows))} / {len(rows)} rows...")
    
    row_count = conn.execute("SELECT COUNT(*) FROM analytics.campaign_daily WHERE customer_id = '9999999999'").fetchone()[0]
    
    conn.close()
    
    return row_count

def main():
    print("Generating synthetic data v2...")
    print(f"  Campaigns: {len(CAMPAIGNS)}")
    print(f"  Date range: {START_DATE} to {END_DATE} ({DAYS} days)")
    print(f"  Expected rows: {len(CAMPAIGNS) * DAYS}\n")
    
    rows = generate_all_data()
    print(f"âœ… Generated {len(rows)} rows\n")
    
    print("Writing to warehouse.duckdb...")
    row_count = write_to_duckdb(rows)
    print(f"âœ… Wrote {row_count} rows to analytics.campaign_daily\n")
    
    print("DONE. Run refresh_readonly.ps1 to update browsing DB.")


if __name__ == "__main__":
    main()