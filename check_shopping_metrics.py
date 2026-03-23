import sys
sys.path.insert(0, 'act_autopilot')

from recommendations_engine import SHOPPING_CAMPAIGN_METRIC_MAP

print("\n=== SHOPPING CAMPAIGN METRICS ===\n")

# Group metrics by category
categories = {
    'Performance': ['roas', 'conversions', 'conversion_rate', 'revenue'],
    'Cost': ['cost', 'cpc', 'cpa'],
    'Efficiency': ['clicks', 'impressions', 'ctr'],
    'Impression Share': ['search_impression_share', 'impression_share_lost'],
    'Quality': ['feed_errors', 'out_of_stock', 'optimization_score']
}

for category, keywords in categories.items():
    matching = [k for k in SHOPPING_CAMPAIGN_METRIC_MAP.keys() if any(kw in k.lower() for kw in keywords)]
    if matching:
        print(f"\n{category}:")
        for metric in sorted(matching):
            print(f"  - {metric}")

print(f"\n\nTOTAL METRICS: {len(SHOPPING_CAMPAIGN_METRIC_MAP)}")
print(f"\nAll metric keys:")
for key in sorted(SHOPPING_CAMPAIGN_METRIC_MAP.keys()):
    print(f"  {key}")
