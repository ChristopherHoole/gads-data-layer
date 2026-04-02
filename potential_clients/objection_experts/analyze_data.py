"""
Data analysis and chart generation for Objection Experts Waste Spend Report.
Outputs JSON data + chart images for the pptxgenjs presentation builder.
"""
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import json
import os
import re

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CHART_DIR = os.path.join(os.path.dirname(__file__), 'charts')
os.makedirs(CHART_DIR, exist_ok=True)

# ── Colour palette (aligned with ACT logo / Google brand) ──
NAVY = '#1A237E'       # Deep indigo-navy
BLUE = '#4285F4'       # Google Blue (logo outer ring)
RED = '#EA4335'        # Google Red (logo second ring)
AMBER = '#FBBC05'      # Google Yellow (logo third ring)
GREEN = '#34A853'      # Google Green (logo centre)
LIGHT_GREY = '#F5F6FA'
CHARCOAL = '#2C3E50'
WHITE = '#FFFFFF'
TEAL = '#4285F4'       # Use blue as primary accent (replaces old teal)

plt.rcParams.update({
    'font.family': 'Calibri',
    'font.size': 11,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.edgecolor': '#CBD5E1',
    'axes.labelcolor': CHARCOAL,
    'xtick.color': '#64748B',
    'ytick.color': '#64748B',
    'figure.facecolor': WHITE,
    'axes.facecolor': WHITE,
    'savefig.facecolor': WHITE,
    'savefig.bbox': 'tight',
    'savefig.dpi': 200,
})

def load_csv(filename, **kwargs):
    """Load a CSV with 2 header rows to skip."""
    path = os.path.join(DATA_DIR, filename)
    return pd.read_csv(path, skiprows=2, thousands=',', **kwargs)

def load_tsv_utf16(filename):
    """Load a UTF-16 TSV file with 2 header rows to skip."""
    path = os.path.join(DATA_DIR, filename)
    return pd.read_csv(path, skiprows=2, sep='\t', encoding='utf-16', thousands=',')

def pct(val):
    """Parse percentage strings like '5.16%' to float."""
    if isinstance(val, str):
        return float(val.replace('%', ''))
    return float(val)

# ─────────────────────────────────────────────
# 1. CAMPAIGN DATA (total spend)
# ─────────────────────────────────────────────
print("Loading campaign data...")
campaign = load_csv('01_campaign_weekly.csv')
# Calculate total cost - need to compute from Avg CPC * Clicks
campaign['Clicks'] = pd.to_numeric(campaign['Clicks'], errors='coerce')
campaign['Avg. CPC'] = pd.to_numeric(campaign['Avg. CPC'], errors='coerce')
campaign['Conversions'] = pd.to_numeric(campaign['Conversions'], errors='coerce')
campaign['Cost'] = campaign['Clicks'] * campaign['Avg. CPC']
total_spend = campaign[campaign['Campaign'] == 'GLO Campaign']['Cost'].sum()
total_conversions = campaign[campaign['Campaign'] == 'GLO Campaign']['Conversions'].sum()
print(f"  Total spend (GLO Campaign): £{total_spend:,.2f}")
print(f"  Total conversions: {total_conversions:.0f}")

# ─────────────────────────────────────────────
# 2. SEARCH TERM WASTE
# ─────────────────────────────────────────────
print("\nAnalyzing search terms...")
search = load_csv('04_search_terms_weekly.csv')
search['Cost'] = pd.to_numeric(search['Cost'], errors='coerce')
search['Clicks'] = pd.to_numeric(search['Clicks'], errors='coerce')
search['Conversions'] = pd.to_numeric(search['Conversions'], errors='coerce')
search['Impr.'] = pd.to_numeric(search['Impr.'], errors='coerce')

# Aggregate by search term
st_agg = search.groupby('Search term').agg({
    'Cost': 'sum',
    'Clicks': 'sum',
    'Conversions': 'sum',
    'Impr.': 'sum'
}).reset_index()
st_agg = st_agg.sort_values('Cost', ascending=False)

# Non-converting terms with spend
non_converting = st_agg[(st_agg['Cost'] > 0) & (st_agg['Conversions'] == 0)].copy()
non_converting = non_converting.sort_values('Cost', ascending=False)
total_non_converting_spend = non_converting['Cost'].sum()

print(f"  Non-converting search terms: {len(non_converting)}")
print(f"  Total waste on non-converting terms: £{total_non_converting_spend:,.2f}")

# Top 20 wasted search terms
top20_waste = non_converting.head(20)

# ── Categorize waste ──
def categorize_waste(term):
    term_lower = term.lower()
    # DIY / template / how-to
    if any(w in term_lower for w in ['template', 'how to', 'how do', 'example', 'write', 'writing', 'sample', 'draft', 'diy', 'yourself']):
        return 'DIY / Template Seekers'
    # Wrong service (planning permission, architects, etc.)
    if any(w in term_lower for w in ['architect', 'surveyor', 'solicitor', 'lawyer', 'barrister', 'consultant', 'agent', 'council', 'apply', 'application form', 'permission cost', 'planning permission uk', 'retrospective']):
        return 'Wrong Service'
    # Jobs / careers
    if any(w in term_lower for w in ['job', 'career', 'salary', 'hire', 'vacancy', 'recruitment']):
        return 'Jobs / Careers'
    # Informational / general
    if any(w in term_lower for w in ['what is', 'what are', 'meaning', 'definition', 'guide', 'advice', 'information', 'rules', 'regulation', 'law', 'act ', 'policy', 'process', 'procedure', 'timescale', 'time limit', 'deadline']):
        return 'Informational Queries'
    # Neighbourhood / different objection types
    if any(w in term_lower for w in ['neighbour', 'neighborhood', 'neighbour', 'fence', 'boundary', 'tree', 'noise', 'parking', 'extension next door']):
        return 'Neighbourhood Disputes'
    # Competitor names
    if any(w in term_lower for w in ['rightsurvey', 'planningaid', 'cpre', 'open spaces']):
        return 'Competitor / Brand Names'
    return 'Other Non-Converting'

non_converting['Category'] = non_converting['Search term'].apply(categorize_waste)
waste_by_category = non_converting.groupby('Category').agg({'Cost': 'sum', 'Clicks': 'sum'}).sort_values('Cost', ascending=False).reset_index()

print(f"\n  Waste by category:")
for _, row in waste_by_category.iterrows():
    print(f"    {row['Category']}: £{row['Cost']:.2f} ({row['Clicks']:.0f} clicks)")

# ── Chart: Top 20 Wasted Search Terms (table-style) ──
fig, ax = plt.subplots(figsize=(10, 6))
ax.axis('off')
top20_data = top20_waste[['Search term', 'Clicks', 'Cost', 'Conversions']].values.tolist()
for row in top20_data:
    row[2] = f"£{row[2]:,.2f}"
    row[1] = f"{int(row[1]):,}"
    row[3] = f"{int(row[3])}"

# Only show top 15 for readability
display_data = top20_data[:15]
table = ax.table(
    cellText=display_data,
    colLabels=['Search Term', 'Clicks', 'Cost', 'Conv.'],
    cellLoc='left',
    loc='center',
    colWidths=[0.55, 0.12, 0.18, 0.12]
)
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 1.6)

# Style header
for j in range(4):
    cell = table[0, j]
    cell.set_facecolor(NAVY)
    cell.set_text_props(color=WHITE, fontweight='bold', fontsize=10)
    cell.set_edgecolor('#E2E8F0')

# Style data rows
for i in range(1, len(display_data) + 1):
    bg = LIGHT_GREY if i % 2 == 0 else WHITE
    for j in range(4):
        cell = table[i, j]
        cell.set_facecolor(bg)
        cell.set_edgecolor('#E2E8F0')
        if j == 2:  # Cost column - red
            cell.set_text_props(color=RED, fontweight='bold')

plt.savefig(os.path.join(CHART_DIR, 'search_term_waste_table.png'), dpi=200, bbox_inches='tight', pad_inches=0.2)
plt.close()

# ── Chart: Waste by Category (horizontal bar) ──
fig, ax = plt.subplots(figsize=(9, 4.5))
cats = waste_by_category['Category'].values[::-1]
costs = waste_by_category['Cost'].values[::-1]
colors = [RED if c > 100 else AMBER for c in costs]
bars = ax.barh(cats, costs, color=colors, height=0.6, edgecolor='none')
ax.set_xlabel('Wasted Spend (£)', fontsize=11, color=CHARCOAL)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'£{x:,.0f}'))
for bar, cost in zip(bars, costs):
    if cost > 20:
        ax.text(bar.get_width() + max(costs)*0.02, bar.get_y() + bar.get_height()/2,
                f'£{cost:,.0f}', va='center', fontsize=10, color=CHARCOAL, fontweight='bold')
ax.set_xlim(0, max(costs) * 1.25)
ax.spines['left'].set_visible(False)
ax.tick_params(axis='y', length=0)
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, 'waste_by_category.png'), dpi=200, bbox_inches='tight', pad_inches=0.2)
plt.close()

# ─────────────────────────────────────────────
# 3. NEGATIVE KEYWORDS
# ─────────────────────────────────────────────
print("\nAnalyzing negative keywords...")
neg_kw = load_csv('12_negative_keywords.csv')  # Actually UTF-8 CSV despite brief saying UTF-16
neg_details = load_csv('Negative keyword details report.csv')

# Count by match type
neg_match_counts = neg_kw['Match type'].value_counts()
print(f"  Total negative keywords (main): {len(neg_kw)}")
print(f"  Match type distribution: {dict(neg_match_counts)}")
print(f"  Negative keyword details list: {len(neg_details)} terms")

exact_count = neg_match_counts.get('Exact match', 0)
phrase_count = neg_match_counts.get('Phrase match', 0)
broad_count = neg_match_counts.get('Broad match', 0) + len(neg_details[neg_details['match_type'] == 'BROAD'])

neg_data = {
    'total_main': len(neg_kw),
    'total_details': len(neg_details),
    'exact_count': int(exact_count),
    'phrase_count': int(phrase_count),
    'broad_count': int(broad_count),
    'examples_exact': neg_kw[neg_kw['Match type'] == 'Exact match']['Negative keyword'].head(8).tolist(),
    'examples_broad': neg_details['keyword_text'].head(8).tolist(),
}

# ── Negative keyword match type chart ──
fig, ax = plt.subplots(figsize=(5, 4))
match_labels = ['Exact Match', 'Phrase Match', 'Broad Match']
match_vals = [int(exact_count), int(phrase_count), int(broad_count)]
colors_pie = [RED, AMBER, GREEN]  # ACT logo: red, yellow, green
wedges, texts, autotexts = ax.pie(match_vals, labels=match_labels, colors=colors_pie,
                                   autopct='%1.0f%%', startangle=90, textprops={'fontsize': 11})
for t in autotexts:
    t.set_fontweight('bold')
    t.set_color(WHITE)
ax.set_title('Negative Keyword Match Types', fontsize=13, fontweight='bold', color=CHARCOAL, pad=15)
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, 'neg_kw_match_types.png'), dpi=200, bbox_inches='tight', pad_inches=0.2)
plt.close()

# ─────────────────────────────────────────────
# 4. AD GROUP WASTE
# ─────────────────────────────────────────────
print("\nAnalyzing ad groups...")
adgroup = load_csv('02_adgroup_weekly.csv')
adgroup['Cost'] = pd.to_numeric(adgroup['Cost'], errors='coerce')
adgroup['Clicks'] = pd.to_numeric(adgroup['Clicks'], errors='coerce')
adgroup['Conversions'] = pd.to_numeric(adgroup['Conversions'], errors='coerce')

ag_agg = adgroup.groupby('Ad group').agg({
    'Cost': 'sum',
    'Clicks': 'sum',
    'Conversions': 'sum'
}).reset_index()
ag_agg['CPA'] = ag_agg.apply(lambda r: r['Cost'] / r['Conversions'] if r['Conversions'] > 0 else None, axis=1)
ag_agg = ag_agg.sort_values('Cost', ascending=False)

print("  Ad group performance:")
for _, row in ag_agg.iterrows():
    cpa_str = f"£{row['CPA']:.2f}" if row['CPA'] else 'N/A'
    print(f"    {row['Ad group']}: £{row['Cost']:.2f}, {row['Conversions']:.0f} conv, CPA={cpa_str}")

zero_conv_groups = ag_agg[ag_agg['Conversions'] == 0]
zero_conv_spend = zero_conv_groups['Cost'].sum()

# ─────────────────────────────────────────────
# 5. TIME OF DAY WASTE
# ─────────────────────────────────────────────
print("\nAnalyzing time of day...")
hour_data = load_csv('09_hour_of_day.csv')
hour_data['Cost'] = pd.to_numeric(hour_data['Cost'], errors='coerce')
hour_data['Clicks'] = pd.to_numeric(hour_data['Clicks'], errors='coerce')
hour_data['Conversions'] = pd.to_numeric(hour_data['Conversions'], errors='coerce')

# Aggregate by hour across all campaigns and ad groups
hour_agg = hour_data.groupby('Hour of the day').agg({
    'Cost': 'sum',
    'Clicks': 'sum',
    'Conversions': 'sum'
}).reset_index()
hour_agg = hour_agg.sort_values('Hour of the day')
hour_agg['CPA'] = hour_agg.apply(lambda r: r['Cost'] / r['Conversions'] if r['Conversions'] > 0 else None, axis=1)

# Hours with zero conversions
zero_conv_hours = hour_agg[hour_agg['Conversions'] == 0]
zero_conv_hour_spend = zero_conv_hours['Cost'].sum()
print(f"  Hours with 0 conversions: {list(zero_conv_hours['Hour of the day'].values)}")
print(f"  Spend on zero-conv hours: £{zero_conv_hour_spend:.2f}")

# Hours with high CPA
high_cpa_hours = hour_agg[(hour_agg['CPA'].notna()) & (hour_agg['CPA'] > 60)]
high_cpa_spend = high_cpa_hours['Cost'].sum()

# ── Chart: Cost & Conversions by Hour ──
fig, ax1 = plt.subplots(figsize=(10, 4.5))
hours = hour_agg['Hour of the day'].values
costs = hour_agg['Cost'].values
convs = hour_agg['Conversions'].values

bar_colors = []
for h, c in zip(hours, convs):
    if c == 0:
        bar_colors.append(RED)
    elif c < 10:
        bar_colors.append(AMBER)
    else:
        bar_colors.append(TEAL)

bars = ax1.bar(hours, costs, color=bar_colors, width=0.7, alpha=0.85, edgecolor='none')
ax1.set_xlabel('Hour of Day', fontsize=11, color=CHARCOAL)
ax1.set_ylabel('Cost (£)', fontsize=11, color=CHARCOAL)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'£{x:,.0f}'))
ax1.set_xticks(range(0, 24))

ax2 = ax1.twinx()
ax2.plot(hours, convs, color=NAVY, linewidth=2.5, marker='o', markersize=5, zorder=5)
ax2.set_ylabel('Conversions', fontsize=11, color=NAVY)
ax2.spines['right'].set_visible(True)
ax2.spines['right'].set_color(NAVY)
ax2.spines['top'].set_visible(False)

# Legend
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
legend_elements = [
    Patch(facecolor=RED, label='Zero Conversions'),
    Patch(facecolor=AMBER, label='Low Conversions (<10)'),
    Patch(facecolor=BLUE, label='Active Hours'),
    Line2D([0], [0], color=NAVY, linewidth=2, marker='o', label='Conversions'),
]
fig.legend(handles=legend_elements, loc='lower center', ncol=4, frameon=False, fontsize=9,
           bbox_to_anchor=(0.45, -0.02))
plt.tight_layout()
plt.subplots_adjust(bottom=0.16)
plt.savefig(os.path.join(CHART_DIR, 'hour_of_day.png'), dpi=200, bbox_inches='tight', pad_inches=0.2)
plt.close()

# ─────────────────────────────────────────────
# 6. DAY OF WEEK
# ─────────────────────────────────────────────
print("\nAnalyzing day of week...")
dow_data = load_csv('10_day_of_week.csv')
dow_data['Cost'] = pd.to_numeric(dow_data['Cost'], errors='coerce')
dow_data['Clicks'] = pd.to_numeric(dow_data['Clicks'], errors='coerce')
dow_data['Conversions'] = pd.to_numeric(dow_data['Conversions'], errors='coerce')

dow_agg = dow_data.groupby('Day of the week').agg({
    'Cost': 'sum',
    'Clicks': 'sum',
    'Conversions': 'sum'
}).reset_index()

# Order days properly
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_agg['Day of the week'] = pd.Categorical(dow_agg['Day of the week'], categories=day_order, ordered=True)
dow_agg = dow_agg.sort_values('Day of the week')
dow_agg['CPA'] = dow_agg.apply(lambda r: r['Cost'] / r['Conversions'] if r['Conversions'] > 0 else None, axis=1)

print("  Day of week performance:")
for _, row in dow_agg.iterrows():
    cpa_str = f"£{row['CPA']:.2f}" if row['CPA'] else 'N/A'
    print(f"    {row['Day of the week']}: £{row['Cost']:.2f}, {row['Conversions']:.0f} conv, CPA={cpa_str}")

# Sunday CPA vs weekday avg
sunday_cpa = dow_agg[dow_agg['Day of the week'] == 'Sunday']['CPA'].values[0]
weekday_cpas = dow_agg[dow_agg['Day of the week'].isin(['Monday','Tuesday','Wednesday','Thursday','Friday'])]['CPA'].dropna()
avg_weekday_cpa = weekday_cpas.mean()

# ── Chart: Day of Week ──
fig, ax1 = plt.subplots(figsize=(9, 4.5))
days = dow_agg['Day of the week'].values
day_labels = [d[:3] for d in days]
costs = dow_agg['Cost'].values
convs = dow_agg['Conversions'].values
cpas = dow_agg['CPA'].values

x = np.arange(len(days))
width = 0.35

# Color bars by CPA performance
bar_colors_dow = []
for cpa in cpas:
    if cpa and cpa > 40:
        bar_colors_dow.append(RED)
    elif cpa and cpa > 30:
        bar_colors_dow.append(AMBER)
    else:
        bar_colors_dow.append(TEAL)

ax1.bar(x - width/2, costs, width, color=[NAVY]*7, alpha=0.7, label='Cost (£)')
ax1.set_ylabel('Cost (£)', fontsize=11, color=CHARCOAL)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'£{x:,.0f}'))
ax1.set_xticks(x)
ax1.set_xticklabels(day_labels)

ax2 = ax1.twinx()
ax2.bar(x + width/2, convs, width, color=TEAL, alpha=0.85, label='Conversions')
ax2.set_ylabel('Conversions', fontsize=11, color=TEAL)
ax2.spines['right'].set_visible(True)
ax2.spines['right'].set_color(TEAL)
ax2.spines['top'].set_visible(False)

# CPA line overlay
cpa_vals = [c if c else 0 for c in cpas]
ax3 = ax1.twinx()
ax3.spines['right'].set_position(('outward', 50))
ax3.plot(x, cpa_vals, color=RED, linewidth=2.5, marker='s', markersize=6, zorder=5, label='CPA (£)')
ax3.set_ylabel('CPA (£)', fontsize=11, color=RED)
ax3.spines['right'].set_color(RED)
ax3.spines['top'].set_visible(False)

# Combined legend — positioned BELOW chart to avoid overlapping bars
lines1 = [Patch(facecolor=NAVY, alpha=0.7, label='Cost'),
          Patch(facecolor=BLUE, alpha=0.85, label='Conversions'),
          Line2D([0], [0], color=RED, linewidth=2, marker='s', label='CPA')]
fig.legend(handles=lines1, loc='lower center', ncol=3, frameon=False, fontsize=9,
           bbox_to_anchor=(0.4, -0.02))
plt.tight_layout()
plt.subplots_adjust(bottom=0.18)
plt.savefig(os.path.join(CHART_DIR, 'day_of_week.png'), dpi=200, bbox_inches='tight', pad_inches=0.2)
plt.close()

# ─────────────────────────────────────────────
# 7. DEVICE WASTE
# ─────────────────────────────────────────────
print("\nAnalyzing device performance...")
device = load_csv('08_device.csv')
# Clean device names (has newlines in "Computers\n")
device['Device'] = device['Device'].str.strip()
device['Cost'] = pd.to_numeric(device['Cost'], errors='coerce')
device['Clicks'] = pd.to_numeric(device['Clicks'], errors='coerce')
device['Conversions'] = pd.to_numeric(device['Conversions'], errors='coerce')

# Filter to GLO Campaign only
device_glo = device[device['Campaign'] == 'GLO Campaign'].copy()
device_agg = device_glo.groupby('Device').agg({
    'Cost': 'sum',
    'Clicks': 'sum',
    'Conversions': 'sum'
}).reset_index()
device_agg['CPA'] = device_agg.apply(lambda r: r['Cost'] / r['Conversions'] if r['Conversions'] > 0 else None, axis=1)
device_agg['Conv Rate'] = device_agg.apply(lambda r: (r['Conversions'] / r['Clicks'] * 100) if r['Clicks'] > 0 else 0, axis=1)
device_agg = device_agg.sort_values('Cost', ascending=False)

# Get bid adjustments
bid_adj = {}
for _, row in device_glo.iterrows():
    dev = row['Device']
    if dev == 'Mobile phones':
        bid_adj[dev] = str(row.get('Campaign mobile bid adj.', '--')).strip()
    elif dev == 'Tablets':
        bid_adj[dev] = str(row.get('Campaign tablet bid adj.', '--')).strip()
    elif dev == 'Computers':
        bid_adj[dev] = str(row.get('Campaign desktop bid adj.', '--')).strip()

print("  Device performance (GLO Campaign):")
for _, row in device_agg.iterrows():
    cpa = f"£{row['CPA']:.2f}" if row['CPA'] else 'N/A'
    ba = bid_adj.get(row['Device'], '--')
    print(f"    {row['Device']}: £{row['Cost']:.2f}, {row['Conversions']:.0f} conv, CPA={cpa}, Bid adj={ba}")

# ─────────────────────────────────────────────
# 8. GEOGRAPHIC WASTE
# ─────────────────────────────────────────────
print("\nAnalyzing geographic performance...")
geo = load_csv('07_geographic.csv')
geo['Cost'] = pd.to_numeric(geo['Cost'], errors='coerce')
geo['Clicks'] = pd.to_numeric(geo['Clicks'], errors='coerce')
geo['Conversions'] = pd.to_numeric(geo['Conversions'], errors='coerce')

# Non-converting locations with spend
geo_waste = geo[(geo['Cost'] > 0) & (geo['Conversions'] == 0)].copy()
geo_waste = geo_waste.sort_values('Cost', ascending=False)
total_geo_waste = geo_waste['Cost'].sum()

# Also aggregate by region for a higher-level view
geo_region = geo.groupby('Region (User location)').agg({
    'Cost': 'sum',
    'Clicks': 'sum',
    'Conversions': 'sum'
}).reset_index()
geo_region['CPA'] = geo_region.apply(lambda r: r['Cost'] / r['Conversions'] if r['Conversions'] > 0 else None, axis=1)
geo_region_waste = geo_region[(geo_region['Cost'] > 5) & (geo_region['Conversions'] == 0)].sort_values('Cost', ascending=False)

print(f"  Non-converting locations: {len(geo_waste)}")
print(f"  Total geographic waste: £{total_geo_waste:.2f}")
print(f"  Top wasting locations:")
for _, row in geo_waste.head(15).iterrows():
    print(f"    {row['City (User location)']}, {row['Region (User location)']}: £{row['Cost']:.2f}")

# ── Chart: Geographic waste (top 15 cities) ──
fig, ax = plt.subplots(figsize=(9, 5))
top_geo = geo_waste.head(15)
cities = [f"{r['City (User location)']}" for _, r in top_geo.iterrows()]
geo_costs = top_geo['Cost'].values

bars = ax.barh(range(len(cities)-1, -1, -1), geo_costs, color=RED, height=0.6, alpha=0.85)
ax.set_yticks(range(len(cities)-1, -1, -1))
ax.set_yticklabels(cities, fontsize=9)
ax.set_xlabel('Wasted Spend (£)', fontsize=11, color=CHARCOAL)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'£{x:,.0f}'))
for i, (bar, cost) in enumerate(zip(bars, geo_costs)):
    ax.text(bar.get_width() + max(geo_costs)*0.02, bar.get_y() + bar.get_height()/2,
            f'£{cost:.2f}', va='center', fontsize=9, color=CHARCOAL, fontweight='bold')
ax.set_xlim(0, max(geo_costs) * 1.3)
ax.spines['left'].set_visible(False)
ax.tick_params(axis='y', length=0)
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, 'geographic_waste.png'), dpi=200, bbox_inches='tight', pad_inches=0.2)
plt.close()

# ─────────────────────────────────────────────
# 9. TOTAL WASTE SUMMARY
# ─────────────────────────────────────────────
# Calculate total identifiable waste
search_term_waste = total_non_converting_spend
adgroup_waste = zero_conv_spend
hour_waste = zero_conv_hour_spend
# Sunday premium over avg weekday CPA
sunday_data = dow_agg[dow_agg['Day of the week'] == 'Sunday'].iloc[0]
sunday_excess = (sunday_cpa - avg_weekday_cpa) * sunday_data['Conversions'] if sunday_cpa > avg_weekday_cpa else 0

# Tablet waste (high CPA relative to others)
tablets = device_agg[device_agg['Device'] == 'Tablets']
tablet_spend = tablets['Cost'].values[0] if len(tablets) > 0 else 0

waste_categories = {
    'Non-Converting\nSearch Terms': search_term_waste,
    'Zero-Conv\nAd Groups': adgroup_waste,
    'Dead Hours\n(0 Conversions)': hour_waste,
    'Geographic\nWaste': total_geo_waste,
    'Sunday\nPremium': sunday_excess,
}

total_waste = sum(waste_categories.values())
waste_pct = (total_waste / total_spend) * 100

print(f"\n{'='*50}")
print(f"TOTAL WASTE SUMMARY")
print(f"{'='*50}")
print(f"Total spend: £{total_spend:,.2f}")
print(f"Total identifiable waste: £{total_waste:,.2f} ({waste_pct:.1f}%)")
for cat, val in waste_categories.items():
    cat_clean = cat.replace('\n', ' ')
    print(f"  {cat_clean}: £{val:,.2f}")

# ── Chart: Waste Waterfall ──
fig, ax = plt.subplots(figsize=(10, 5))
cat_labels = list(waste_categories.keys())
cat_values = list(waste_categories.values())
# Add total bar
cat_labels.append('TOTAL\nWASTE')
cat_values_plot = cat_values + [total_waste]

colors_wf = [RED] * len(cat_values) + [NAVY]
bars = ax.bar(range(len(cat_labels)), cat_values_plot, color=colors_wf, width=0.6, edgecolor='none')
ax.set_xticks(range(len(cat_labels)))
ax.set_xticklabels(cat_labels, fontsize=9, ha='center')
ax.set_ylabel('Wasted Spend (£)', fontsize=11, color=CHARCOAL)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'£{x:,.0f}'))
for bar, val in zip(bars, cat_values_plot):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(cat_values_plot)*0.02,
            f'£{val:,.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold', color=CHARCOAL)
ax.spines['bottom'].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, 'waste_waterfall.png'), dpi=200, bbox_inches='tight', pad_inches=0.2)
plt.close()

# ── Device performance chart ──
fig, ax = plt.subplots(figsize=(8, 4))
devs = device_agg['Device'].values
dev_costs = device_agg['Cost'].values
dev_cpas = [c if c else 0 for c in device_agg['CPA'].values]

x = np.arange(len(devs))
width = 0.35
ax.bar(x - width/2, dev_costs, width, color=NAVY, alpha=0.8, label='Cost (£)')
ax.set_ylabel('Cost (£)', fontsize=11, color=CHARCOAL)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'£{x:,.0f}'))
ax.set_xticks(x)
ax.set_xticklabels(devs, fontsize=10)

ax2 = ax.twinx()
bar_colors_dev = [GREEN if c < 33 else AMBER if c < 36 else RED for c in dev_cpas]
ax2.bar(x + width/2, dev_cpas, width, color=bar_colors_dev, alpha=0.85, label='CPA (£)')
ax2.set_ylabel('CPA (£)', fontsize=11, color=RED)
ax2.spines['right'].set_visible(True)
ax2.spines['top'].set_visible(False)

legend_elements = [Patch(facecolor=NAVY, alpha=0.8, label='Cost'),
                   Patch(facecolor=AMBER, label='CPA')]
fig.legend(handles=legend_elements, loc='lower center', ncol=2, frameon=False, fontsize=9,
           bbox_to_anchor=(0.45, -0.02))
plt.tight_layout()
plt.subplots_adjust(bottom=0.2)
plt.savefig(os.path.join(CHART_DIR, 'device_performance.png'), dpi=200, bbox_inches='tight', pad_inches=0.2)
plt.close()

# ─────────────────────────────────────────────
# OUTPUT JSON FOR PPTX BUILDER
# ─────────────────────────────────────────────
output = {
    'total_spend': round(total_spend, 2),
    'total_conversions': round(total_conversions, 0),
    'total_waste': round(total_waste, 2),
    'waste_pct': round(waste_pct, 1),
    'waste_categories': {k.replace('\n', ' '): round(v, 2) for k, v in waste_categories.items()},
    'search_term_waste': {
        'total': round(total_non_converting_spend, 2),
        'count': len(non_converting),
        'top20': top20_waste[['Search term', 'Clicks', 'Cost', 'Conversions']].to_dict('records'),
        'by_category': waste_by_category.to_dict('records'),
    },
    'negative_keywords': neg_data,
    'ad_groups': {
        'data': ag_agg.to_dict('records'),
        'zero_conv_spend': round(zero_conv_spend, 2),
    },
    'hour_of_day': {
        'data': hour_agg.to_dict('records'),
        'zero_conv_hours': list(zero_conv_hours['Hour of the day'].values),
        'zero_conv_spend': round(zero_conv_hour_spend, 2),
    },
    'day_of_week': {
        'data': [{**r, 'Day of the week': str(r['Day of the week'])} for r in dow_agg.to_dict('records')],
        'sunday_cpa': round(sunday_cpa, 2) if sunday_cpa else None,
        'avg_weekday_cpa': round(avg_weekday_cpa, 2),
        'sunday_excess': round(sunday_excess, 2),
    },
    'device': {
        'data': device_agg.to_dict('records'),
        'bid_adjustments': bid_adj,
    },
    'geographic': {
        'total_waste': round(total_geo_waste, 2),
        'count': len(geo_waste),
        'top15': geo_waste.head(15)[['City (User location)', 'Region (User location)', 'Cost', 'Clicks']].to_dict('records'),
    },
    # Monthly estimates (divide by ~15 months of data)
    'monthly_waste_estimate': round(total_waste / 15, 2),
}

import math

def clean_for_json(obj):
    """Replace NaN/Inf with None for JSON compatibility."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_for_json(i) for i in obj]
    return obj

output = clean_for_json(output)

with open(os.path.join(os.path.dirname(__file__), 'analysis_output.json'), 'w') as f:
    json.dump(output, f, indent=2, default=str)

print(f"\nAnalysis complete. JSON saved. Charts saved to {CHART_DIR}/")
print(f"  Charts: {os.listdir(CHART_DIR)}")
