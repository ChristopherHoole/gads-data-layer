"""Verify PowerPoint report data against source CSVs."""
import pandas as pd
import os

DATA = "C:/Users/User/Desktop/gads-data-layer/potential_clients/objection_experts/data"

print("=" * 80)
print("1. SEARCH TERM WASTE TABLE (Slide 3)")
print("=" * 80)
df = pd.read_csv(f"{DATA}/04_search_terms_weekly.csv", skiprows=2)
# Clean numeric columns
for c in ['Cost', 'Clicks', 'Conversions']:
    df[c] = pd.to_numeric(df[c].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
agg = df.groupby('Search term').agg({'Cost': 'sum', 'Clicks': 'sum', 'Conversions': 'sum'}).reset_index()
waste = agg[agg['Conversions'] == 0].sort_values('Cost', ascending=False)
print(f"Total non-converting search terms: {len(waste)}")
print(f"Total waste spend: £{waste['Cost'].sum():.2f}")
print("\nTop 5 non-converting search terms by cost:")
for i, row in waste.head(5).iterrows():
    print(f"  {row['Search term']}: Cost=£{row['Cost']:.2f}, Clicks={int(row['Clicks'])}")

print("\n" + "=" * 80)
print("2. AD GROUP TABLE (Slide 6)")
print("=" * 80)
df = pd.read_csv(f"{DATA}/02_adgroup_weekly.csv", skiprows=2, thousands=',')
for c in ['Cost', 'Clicks', 'Conversions']:
    df[c] = pd.to_numeric(df[c].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
agg = df.groupby('Ad group').agg({'Cost': 'sum', 'Clicks': 'sum', 'Conversions': 'sum'}).reset_index()
print("Ad group performance (all):")
for i, row in agg.iterrows():
    cpa = row['Cost'] / row['Conversions'] if row['Conversions'] > 0 else float('inf')
    cpa_str = f"£{cpa:.2f}" if cpa != float('inf') else "N/A"
    print(f"  {row['Ad group']}: Cost=£{row['Cost']:.2f}, Clicks={int(row['Clicks'])}, Conv={row['Conversions']:.2f}, CPA={cpa_str}")

print("\n" + "=" * 80)
print("3. DEVICE TABLE (Slide 9) - GLO Campaign only")
print("=" * 80)
# This CSV has multiline fields, need to handle carefully
df = pd.read_csv(f"{DATA}/08_device.csv", skiprows=2, thousands=',')
# Clean device names (may have newlines)
df['Device'] = df['Device'].str.strip().str.replace('\n', '')
df_glo = df[df['Campaign'] == 'GLO Campaign']
for c in ['Cost', 'Clicks', 'Conversions']:
    df_glo[c] = pd.to_numeric(df_glo[c].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
agg = df_glo.groupby('Device').agg({'Cost': 'sum', 'Clicks': 'sum', 'Conversions': 'sum'}).reset_index()
print("Device performance (GLO Campaign):")
for i, row in agg.iterrows():
    cpa = row['Cost'] / row['Conversions'] if row['Conversions'] > 0 else float('inf')
    cpa_str = f"£{cpa:.2f}" if cpa != float('inf') else "N/A"
    print(f"  {row['Device']}: Cost=£{row['Cost']:.2f}, Clicks={int(row['Clicks'])}, Conv={row['Conversions']:.2f}, CPA={cpa_str}")

print("\n" + "=" * 80)
print("4. DAY OF WEEK (Slide 8)")
print("=" * 80)
df = pd.read_csv(f"{DATA}/10_day_of_week.csv", skiprows=2, thousands=',')
for c in ['Cost', 'Clicks', 'Conversions']:
    df[c] = pd.to_numeric(df[c].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
agg = df.groupby('Day of the week').agg({'Cost': 'sum', 'Clicks': 'sum', 'Conversions': 'sum'}).reset_index()
agg['CPA'] = agg.apply(lambda r: r['Cost'] / r['Conversions'] if r['Conversions'] > 0 else float('inf'), axis=1)
# Order days
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
agg['day_idx'] = agg['Day of the week'].map({d: i for i, d in enumerate(day_order)})
agg = agg.sort_values('day_idx')
print("Day of week performance (all campaigns):")
for i, row in agg.iterrows():
    cpa_str = f"£{row['CPA']:.2f}" if row['CPA'] != float('inf') else "N/A"
    print(f"  {row['Day of the week']}: Cost=£{row['Cost']:.2f}, Conv={row['Conversions']:.2f}, CPA={cpa_str}")

print("\n" + "=" * 80)
print("5. HOUR OF DAY (Slide 7) - Top 5 hours by CPA with 15+ conversions")
print("=" * 80)
df = pd.read_csv(f"{DATA}/09_hour_of_day.csv", skiprows=2, thousands=',')
for c in ['Cost', 'Clicks', 'Conversions']:
    df[c] = pd.to_numeric(df[c].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
agg = df.groupby('Hour of the day').agg({'Cost': 'sum', 'Clicks': 'sum', 'Conversions': 'sum'}).reset_index()
agg_15 = agg[agg['Conversions'] >= 15].copy()
agg_15['CPA'] = agg_15['Cost'] / agg_15['Conversions']
agg_15 = agg_15.sort_values('CPA')
print(f"Hours with 15+ conversions: {len(agg_15)}")
print("\nTop 5 hours by CPA (lowest = best):")
for i, row in agg_15.head(5).iterrows():
    print(f"  Hour {int(row['Hour of the day']):02d}: Cost=£{row['Cost']:.2f}, Clicks={int(row['Clicks'])}, Conv={row['Conversions']:.2f}, CPA=£{row['CPA']:.2f}")

print("\n" + "=" * 80)
print("6. GEOGRAPHIC WASTE")
print("=" * 80)
df = pd.read_csv(f"{DATA}/07_geographic.csv", skiprows=2, thousands=',')
for c in ['Cost', 'Clicks', 'Conversions']:
    df[c] = pd.to_numeric(df[c].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
# Locations with Cost>0 and Conversions=0
waste_geo = df[(df['Cost'] > 0) & (df['Conversions'] == 0)]
# Aggregate by city
waste_agg = waste_geo.groupby('City (User location)').agg({'Cost': 'sum', 'Clicks': 'sum'}).reset_index()
waste_agg = waste_agg.sort_values('Cost', ascending=False)
total_waste_cities = len(waste_agg)
total_waste_spend = waste_agg['Cost'].sum()
print(f"Locations (cities) with Cost>0 and 0 conversions: {total_waste_cities}")
print(f"Total geographic waste spend: £{total_waste_spend:.2f}")
print("\nTop 5 wasting cities:")
for i, row in waste_agg.head(5).iterrows():
    print(f"  {row['City (User location)']}: Cost=£{row['Cost']:.2f}, Clicks={int(row['Clicks'])}")

print("\n" + "=" * 80)
print("7. TOTAL SPEND - GLO Campaign")
print("=" * 80)
df = pd.read_csv(f"{DATA}/01_campaign_weekly.csv", skiprows=2, thousands=',')
df['Clicks'] = pd.to_numeric(df['Clicks'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
df['Avg. CPC'] = pd.to_numeric(df['Avg. CPC'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
df['Conversions'] = pd.to_numeric(df['Conversions'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
glo = df[df['Campaign'] == 'GLO Campaign']
glo = glo.copy()
glo['Spend'] = glo['Clicks'] * glo['Avg. CPC']
total_spend = glo['Spend'].sum()
total_conv = glo['Conversions'].sum()
total_clicks = glo['Clicks'].sum()
print(f"GLO Campaign total spend (Clicks * Avg CPC): £{total_spend:.2f}")
print(f"GLO Campaign total conversions: {total_conv:.2f}")
print(f"GLO Campaign total clicks: {int(total_clicks)}")
print(f"GLO Campaign overall CPA: £{total_spend / total_conv:.2f}")
