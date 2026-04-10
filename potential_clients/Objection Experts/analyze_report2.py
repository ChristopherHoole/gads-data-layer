"""
Data analysis and chart generation for Report 2: Account Structure & Issues.
"""
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import numpy as np
import json, os, math

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CHART_DIR = os.path.join(os.path.dirname(__file__), 'charts')
os.makedirs(CHART_DIR, exist_ok=True)

# ── Colours (ACT logo / Google brand) ──
NAVY = '#1A237E'
BLUE = '#4285F4'
RED = '#EA4335'
AMBER = '#FBBC05'
GREEN = '#34A853'
BLACK = '#1A1A1A'
WHITE = '#FFFFFF'
L_GREY = '#F5F6FA'

plt.rcParams.update({
    'font.family': 'Calibri', 'font.size': 11,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.edgecolor': '#CBD5E1', 'axes.labelcolor': BLACK,
    'xtick.color': BLACK, 'ytick.color': BLACK,
    'figure.facecolor': WHITE, 'axes.facecolor': WHITE,
    'savefig.facecolor': WHITE, 'savefig.bbox': 'tight', 'savefig.dpi': 200,
})

from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# ─────────────────────────────────────────────
# 1. CAMPAIGN WEEKLY DATA
# ─────────────────────────────────────────────
camp = pd.read_csv(os.path.join(DATA_DIR, '01_campaign_weekly.csv'), skiprows=2, thousands=',')
camp['Clicks'] = pd.to_numeric(camp['Clicks'], errors='coerce')
camp['Avg. CPC'] = pd.to_numeric(camp['Avg. CPC'], errors='coerce')
camp['Conversions'] = pd.to_numeric(camp['Conversions'], errors='coerce')
camp['Cost'] = camp['Clicks'] * camp['Avg. CPC']
camp['Week'] = pd.to_datetime(camp['Week'])
camp['Impr.'] = pd.to_numeric(camp['Impr.'], errors='coerce')

glo = camp[camp['Campaign'] == 'GLO Campaign'].sort_values('Week').copy()
glo['CPA'] = glo.apply(lambda r: r['Cost']/r['Conversions'] if r['Conversions'] > 0 else None, axis=1)
glo['Conv Rate'] = glo.apply(lambda r: (r['Conversions']/r['Clicks']*100) if r['Clicks'] > 0 else 0, axis=1)

cutoff = pd.Timestamp('2025-10-01')
pre = glo[glo['Week'] < cutoff]
post = glo[glo['Week'] >= cutoff]

# ── Chart: CPA Over Time ──
fig, ax = plt.subplots(figsize=(10, 4.5))
weeks = glo['Week'].values
cpas = glo['CPA'].values

ax.plot(weeks, cpas, color=BLUE, linewidth=2, marker='o', markersize=3, zorder=3)
ax.axvline(x=cutoff, color=RED, linestyle='--', linewidth=2, alpha=0.8, zorder=2)
ax.text(cutoff + pd.Timedelta(days=5), max([c for c in cpas if c is not None and not np.isnan(c)]) * 0.95,
        'Agency Change\nOctober 2025', fontsize=11, color=RED, fontweight='bold', va='top')

# Pre/post average lines
pre_cpa = pre['Cost'].sum() / pre['Conversions'].sum()
post_cpa = post['Cost'].sum() / post['Conversions'].sum()
ax.axhline(y=pre_cpa, xmin=0, xmax=0.6, color=GREEN, linestyle='-', linewidth=1.5, alpha=0.6)
ax.axhline(y=post_cpa, xmin=0.6, xmax=1, color=RED, linestyle='-', linewidth=1.5, alpha=0.6)
ax.text(glo['Week'].iloc[5], pre_cpa + 2, f'Pre-Oct avg: £{pre_cpa:.0f}', fontsize=11, color=GREEN, fontweight='bold')
ax.text(glo['Week'].iloc[-5], post_cpa + 2, f'Post-Oct avg: £{post_cpa:.0f}', fontsize=11, color=RED, fontweight='bold')

ax.set_ylabel('Cost Per Conversion (£)', fontsize=11, color=BLACK)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'£{x:.0f}'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, 'cpa_over_time.png'), dpi=200, bbox_inches='tight', pad_inches=0.2)
plt.close()

# ── Chart: Conversion Rate Over Time ──
fig, ax = plt.subplots(figsize=(10, 4.5))
conv_rates = glo['Conv Rate'].values

ax.plot(weeks, conv_rates, color=GREEN, linewidth=2, marker='o', markersize=3, zorder=3)
ax.axvline(x=cutoff, color=RED, linestyle='--', linewidth=2, alpha=0.8, zorder=2)
ax.text(cutoff + pd.Timedelta(days=5), max(conv_rates) * 0.95,
        'Agency Change\nOctober 2025', fontsize=11, color=RED, fontweight='bold', va='top')

pre_cr = pre['Conversions'].sum() / pre['Clicks'].sum() * 100
post_cr = post['Conversions'].sum() / post['Clicks'].sum() * 100
ax.axhline(y=pre_cr, xmin=0, xmax=0.6, color=GREEN, linestyle='-', linewidth=1.5, alpha=0.6)
ax.axhline(y=post_cr, xmin=0.6, xmax=1, color=RED, linestyle='-', linewidth=1.5, alpha=0.6)
ax.text(glo['Week'].iloc[5], pre_cr + 0.5, f'Pre-Oct avg: {pre_cr:.1f}%', fontsize=11, color=GREEN, fontweight='bold')
ax.text(glo['Week'].iloc[-5], post_cr + 0.5, f'Post-Oct avg: {post_cr:.1f}%', fontsize=11, color=RED, fontweight='bold')

ax.set_ylabel('Conversion Rate (%)', fontsize=11, color=BLACK)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}%'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, 'conv_rate_over_time.png'), dpi=200, bbox_inches='tight', pad_inches=0.2)
plt.close()

# ── Chart: Weekly Spend Over Time ──
fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(weeks, glo['Cost'].values, width=5, color=BLUE, alpha=0.7)
ax.axvline(x=cutoff, color=RED, linestyle='--', linewidth=2, alpha=0.8)
ax.set_ylabel('Weekly Spend (£)', fontsize=11, color=BLACK)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'£{x:.0f}'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, 'weekly_spend.png'), dpi=200, bbox_inches='tight', pad_inches=0.2)
plt.close()

# ─────────────────────────────────────────────
# 2. QUALITY SCORE DISTRIBUTION
# ─────────────────────────────────────────────
kw = pd.read_csv(os.path.join(DATA_DIR, '03_keywords_weekly.csv'), skiprows=2, sep='\t', encoding='utf-16', thousands=',')
kw['Quality Score'] = pd.to_numeric(kw['Quality Score'], errors='coerce')
kw['Cost'] = pd.to_numeric(kw['Cost'], errors='coerce')
kw['Clicks'] = pd.to_numeric(kw['Clicks'], errors='coerce')

# Get latest QS per keyword (use most recent week with a QS value)
kw_with_qs = kw[kw['Quality Score'].notna()].copy()
kw_with_qs['Week'] = pd.to_datetime(kw_with_qs['Week'])
latest_qs = kw_with_qs.sort_values('Week').groupby('Search keyword').last().reset_index()

qs_dist = latest_qs['Quality Score'].value_counts().sort_index()
print("QS Distribution (unique keywords):")
print(qs_dist)

fig, ax = plt.subplots(figsize=(7, 4))
qs_vals = qs_dist.index.astype(int)
qs_counts = qs_dist.values
colors_qs = [RED if v <= 3 else AMBER if v <= 5 else GREEN for v in qs_vals]
bars = ax.bar(qs_vals, qs_counts, color=colors_qs, width=0.7, edgecolor='none')
for bar, count in zip(bars, qs_counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            str(count), ha='center', va='bottom', fontsize=12, fontweight='bold', color=BLACK)
ax.set_xlabel('Quality Score', fontsize=11, color=BLACK)
ax.set_ylabel('Number of Keywords', fontsize=11, color=BLACK)
ax.set_xticks(range(1, 11))
ax.set_xticklabels([str(i) for i in range(1, 11)])

legend_elements = [Patch(facecolor=RED, label='Poor (1-3)'),
                   Patch(facecolor=AMBER, label='Average (4-5)'),
                   Patch(facecolor=GREEN, label='Good (6-10)')]
fig.legend(handles=legend_elements, loc='lower center', ncol=3, frameon=False, fontsize=11,
           bbox_to_anchor=(0.5, -0.02))
plt.tight_layout()
plt.subplots_adjust(bottom=0.18)
plt.savefig(os.path.join(CHART_DIR, 'quality_score_dist.png'), dpi=200, bbox_inches='tight', pad_inches=0.2)
plt.close()

# ─────────────────────────────────────────────
# 3. AD COPY PERFORMANCE
# ─────────────────────────────────────────────
ads = pd.read_csv(os.path.join(DATA_DIR, '05_ad_copy_weekly.csv'), skiprows=2, thousands=',')
ads['Cost'] = pd.to_numeric(ads['Cost'], errors='coerce')
ads['Clicks'] = pd.to_numeric(ads['Clicks'], errors='coerce')
ads['Conversions'] = pd.to_numeric(ads['Conversions'], errors='coerce')

po_ads = ads[ads['Ad group'] == 'Planning Objections']
ad_perf = po_ads.groupby(['Headline 1', 'Ad type']).agg({
    'Cost': 'sum', 'Clicks': 'sum', 'Conversions': 'sum'
}).reset_index()
ad_perf['CPA'] = ad_perf.apply(lambda r: r['Cost']/r['Conversions'] if r['Conversions'] > 0 else None, axis=1)
ad_perf['CTR_proxy'] = ad_perf['Clicks']  # proxy
ad_perf = ad_perf.sort_values('Cost', ascending=False)

# ── Chart: Ad spend distribution ──
fig, ax = plt.subplots(figsize=(8, 4))
rsa_only = ad_perf[ad_perf['Ad type'] == 'Responsive search ad'].copy()
labels = [h[:30] + '...' if len(h) > 30 else h for h in rsa_only['Headline 1']]
costs = rsa_only['Cost'].values
cpas_ad = [c if c and not np.isnan(c) else 0 for c in rsa_only['CPA'].values]

x = np.arange(len(labels))
width = 0.35
bars1 = ax.bar(x - width/2, costs, width, color=BLUE, alpha=0.8, label='Spend (£)')
ax.set_ylabel('Spend (£)', fontsize=11, color=BLACK)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'£{x:,.0f}'))
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=11, rotation=15, ha='right')

ax2 = ax.twinx()
bars2 = ax2.bar(x + width/2, cpas_ad, width, color=RED, alpha=0.7, label='CPA (£)')
ax2.set_ylabel('CPA (£)', fontsize=11, color=RED)
ax2.spines['right'].set_visible(True)
ax2.spines['top'].set_visible(False)

legend_elements = [Patch(facecolor=BLUE, alpha=0.8, label='Spend'),
                   Patch(facecolor=RED, alpha=0.7, label='CPA')]
fig.legend(handles=legend_elements, loc='lower center', ncol=2, frameon=False, fontsize=11,
           bbox_to_anchor=(0.5, -0.02))
plt.tight_layout()
plt.subplots_adjust(bottom=0.18)
plt.savefig(os.path.join(CHART_DIR, 'ad_spend_distribution.png'), dpi=200, bbox_inches='tight', pad_inches=0.2)
plt.close()

# ─────────────────────────────────────────────
# OUTPUT JSON
# ─────────────────────────────────────────────
def clean(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return float(obj)
    if isinstance(obj, dict):
        return {k: clean(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean(i) for i in obj]
    return obj

output = {
    'before_after': {
        'pre': {
            'weeks': len(pre), 'spend': round(pre['Cost'].sum(), 2),
            'clicks': int(pre['Clicks'].sum()), 'conversions': int(pre['Conversions'].sum()),
            'avg_weekly_spend': round(pre['Cost'].mean(), 2),
            'avg_cpc': round(pre['Cost'].sum() / pre['Clicks'].sum(), 2),
            'cpa': round(pre['Cost'].sum() / pre['Conversions'].sum(), 2),
            'conv_rate': round(pre['Conversions'].sum() / pre['Clicks'].sum() * 100, 2),
        },
        'post': {
            'weeks': len(post), 'spend': round(post['Cost'].sum(), 2),
            'clicks': int(post['Clicks'].sum()), 'conversions': int(post['Conversions'].sum()),
            'avg_weekly_spend': round(post['Cost'].mean(), 2),
            'avg_cpc': round(post['Cost'].sum() / post['Clicks'].sum(), 2),
            'cpa': round(post['Cost'].sum() / post['Conversions'].sum(), 2),
            'conv_rate': round(post['Conversions'].sum() / post['Clicks'].sum() * 100, 2),
        },
    },
    'quality_scores': {
        'distribution': {str(int(k)): int(v) for k, v in qs_dist.items()},
        'mean': round(latest_qs['Quality Score'].mean(), 1),
        'total_keywords': len(latest_qs),
        'poor_count': int(len(latest_qs[latest_qs['Quality Score'] <= 3])),
        'poor_pct': round(len(latest_qs[latest_qs['Quality Score'] <= 3]) / len(latest_qs) * 100, 0),
    },
    'ad_performance': clean(ad_perf.to_dict('records')),
    'conversion_actions': {
        'form_submissions': 464.0,
        'google_forwarding': 26.0,
        'email_click': 17.0,
        'phone_number_click': 45.0,
        'total_reported': 552.0,
        'real_conversions': 490.0,
        'inflated_by': 62.0,
    },
    'change_history': {
        'total_changes': 372,
        'flex_digital': 137,
        'generate_leads': 90,
        'client_owen': 119,
        'auto_apply': 1,
    },
    'bid_strategy': 'Maximise Conversions (no target CPA)',
    'audiences_total': 1066,
    'audiences_with_clicks': 434,
}

with open(os.path.join(os.path.dirname(__file__), 'analysis_report2.json'), 'w') as f:
    json.dump(output, f, indent=2, default=str)

print("Report 2 analysis complete. Charts and JSON saved.")
print(f"Charts: {[f for f in os.listdir(CHART_DIR) if 'cpa_' in f or 'conv_rate' in f or 'quality' in f or 'ad_spend' in f or 'weekly_spend' in f]}")
