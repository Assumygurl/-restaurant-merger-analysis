"""
Step 7b: Revenue Forecasting Model
====================================
Uses Facebook Prophet to forecast monthly revenue
for the merged ABC & XYZ restaurant entity.

Produces:
  - 12-month revenue forecast (Jul 2025 - Jun 2026)
  - Seasonal decomposition chart
  - Trend analysis
  - Chain-level individual forecasts
  - All charts saved to outputs/charts/

Run:
  python script/07b_forecasting.py
"""

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from prophet import Prophet
import os
import warnings
warnings.filterwarnings('ignore')

# ── Paths ──────────────────────────────────────────────────────
DATA_DIR   = r"C:\Users\HP\Desktop\Restruant_Project\data"
OUTPUT_DIR = r"C:\Users\HP\Desktop\Restruant_Project\outputs"
CHARTS_DIR = os.path.join(OUTPUT_DIR, "charts")
DB_PATH    = os.path.join(DATA_DIR, "restaurant_2025.db")

os.makedirs(CHARTS_DIR, exist_ok=True)

print("=" * 60)
print("STEP 7b: REVENUE FORECASTING MODEL (Prophet)")
print("=" * 60)

# ── Load monthly revenue from database ────────────────────────
print("\n[1] Loading monthly revenue data...")
conn = sqlite3.connect(DB_PATH)

monthly = pd.read_sql_query("""
    SELECT
        chain,
        CAST(CAST(order_year AS INTEGER) AS TEXT) || '-' || printf('%02d', CAST(order_month AS INTEGER)) || '-01' as ds,
        SUM(order_total_cost) as y
    FROM orders
    WHERE order_purchase_date IS NOT NULL
    GROUP BY chain, order_year, order_month
    ORDER BY ds
""", conn)

combined = pd.read_sql_query("""
    SELECT
        CAST(CAST(order_year AS INTEGER) AS TEXT) || '-' || printf('%02d', CAST(order_month AS INTEGER)) || '-01' as ds,
        SUM(order_total_cost) as y
    FROM orders
    WHERE order_purchase_date IS NOT NULL
    GROUP BY order_year, order_month
    ORDER BY ds
""", conn)

conn.close()

monthly['ds'] = pd.to_datetime(monthly['ds'])
combined['ds'] = pd.to_datetime(combined['ds'])

print(f"    Combined monthly data: {len(combined)} months")
print(f"    Date range: {combined['ds'].min().strftime('%b %Y')} → {combined['ds'].max().strftime('%b %Y')}")
print(f"    Total revenue in data: ${combined['y'].sum()/1e6:.1f}M")

# ── Helper: save chart ─────────────────────────────────────────
def save_chart(fig, filename):
    path = os.path.join(CHARTS_DIR, filename)
    fig.savefig(path, bbox_inches='tight', dpi=150)
    plt.close(fig)
    print(f"    ✓ Saved: {filename}")

# ══════════════════════════════════════════════════════════════
# FORECAST 1: COMBINED ENTITY (ABC + XYZ)
# ══════════════════════════════════════════════════════════════
print("\n[2] Running combined forecast (ABC + XYZ)...")

model_combined = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=False,
    daily_seasonality=False,
    seasonality_mode='multiplicative',
    interval_width=0.95,
    changepoint_prior_scale=0.05
)
model_combined.fit(combined)

# Forecast 12 months ahead
future_combined = model_combined.make_future_dataframe(periods=12, freq='MS')
forecast_combined = model_combined.predict(future_combined)

# ── Chart 1: Combined Forecast ─────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# Historical data
ax.plot(combined['ds'], combined['y']/1e6,
        color='#1E2761', linewidth=2.5, marker='o', markersize=5,
        label='Historical Revenue', zorder=3)

# Forecast line
forecast_future = forecast_combined[forecast_combined['ds'] > combined['ds'].max()]
ax.plot(forecast_future['ds'], forecast_future['yhat']/1e6,
        color='#F4A261', linewidth=2.5, linestyle='--',
        marker='s', markersize=5, label='Forecasted Revenue', zorder=3)

# Confidence interval
ax.fill_between(forecast_future['ds'],
                forecast_future['yhat_lower']/1e6,
                forecast_future['yhat_upper']/1e6,
                alpha=0.2, color='#F4A261', label='95% Confidence Interval')

# Divider line
ax.axvline(x=combined['ds'].max(), color='gray', linestyle=':', linewidth=1.5, alpha=0.7)
ax.text(combined['ds'].max(), ax.get_ylim()[1] * 0.95,
        ' Forecast\n starts', fontsize=9, color='gray')

ax.set_title('ABC & XYZ Combined — Monthly Revenue Forecast (Jul 2025 – Jun 2026)',
             fontsize=14, fontweight='bold', color='#1E2761', pad=15)
ax.set_xlabel('Month', fontsize=11)
ax.set_ylabel('Revenue ($M)', fontsize=11)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.1f}M'))
ax.legend(loc='upper left', fontsize=10)
ax.grid(False)

plt.tight_layout()
save_chart(fig, "11_combined_forecast.png")

# ── Chart 2: Forecast Components (Trend + Seasonality) ────────
print("\n[3] Generating seasonal decomposition charts...")
fig2 = model_combined.plot_components(forecast_combined)
fig2.suptitle('Revenue Forecast Components — Trend & Seasonality',
              fontsize=13, fontweight='bold', color='#1E2761', y=1.01)
fig2.patch.set_facecolor('white')
for ax in fig2.axes:
    ax.set_facecolor('white')
    ax.grid(False)
plt.tight_layout()
save_chart(fig2, "12_forecast_components.png")

# ══════════════════════════════════════════════════════════════
# FORECAST 2: INDIVIDUAL CHAIN FORECASTS
# ══════════════════════════════════════════════════════════════
print("\n[4] Running individual chain forecasts...")

chain_colors  = {'ABC': '#2196F3', 'XYZ': '#FF5722'}
chain_forecasts = {}

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Individual Chain Revenue Forecasts (Jul 2025 – Jun 2026)',
             fontsize=14, fontweight='bold', color='#1E2761')
fig.patch.set_facecolor('white')

for i, chain in enumerate(['ABC', 'XYZ']):
    chain_data = monthly[monthly['chain'] == chain][['ds', 'y']].reset_index(drop=True)

    m = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode='multiplicative',
        interval_width=0.95,
        changepoint_prior_scale=0.05
    )
    m.fit(chain_data)

    future = m.make_future_dataframe(periods=12, freq='MS')
    forecast = m.predict(future)
    chain_forecasts[chain] = forecast

    ax = axes[i]
    ax.set_facecolor('white')
    color = chain_colors[chain]

    # Historical
    ax.plot(chain_data['ds'], chain_data['y']/1e6,
            color=color, linewidth=2.5, marker='o', markersize=5,
            label='Historical', zorder=3)

    # Forecast
    fc_future = forecast[forecast['ds'] > chain_data['ds'].max()]
    ax.plot(fc_future['ds'], fc_future['yhat']/1e6,
            color=color, linewidth=2, linestyle='--',
            marker='s', markersize=4, alpha=0.8, label='Forecast', zorder=3)

    ax.fill_between(fc_future['ds'],
                    fc_future['yhat_lower']/1e6,
                    fc_future['yhat_upper']/1e6,
                    alpha=0.15, color=color)

    ax.axvline(x=chain_data['ds'].max(), color='gray', linestyle=':', linewidth=1.2, alpha=0.7)
    ax.set_title(f'{chain} Chain Forecast', fontsize=13, fontweight='bold', color=color)
    ax.set_xlabel('Month', fontsize=10)
    ax.set_ylabel('Revenue ($M)', fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.1f}M'))
    ax.legend(fontsize=9)
    ax.grid(False)
    ax.tick_params(axis='x', rotation=45)

plt.tight_layout()
save_chart(fig, "13_chain_forecasts.png")

# ══════════════════════════════════════════════════════════════
# FORECAST SUMMARY TABLE
# ══════════════════════════════════════════════════════════════
print("\n[5] Generating forecast summary...")

future_months = forecast_combined[forecast_combined['ds'] > combined['ds'].max()].copy()
future_months['Month']         = future_months['ds'].dt.strftime('%B %Y')
future_months['Forecast_M']    = (future_months['yhat'] / 1e6).round(2)
future_months['Lower_M']       = (future_months['yhat_lower'] / 1e6).round(2)
future_months['Upper_M']       = (future_months['yhat_upper'] / 1e6).round(2)

summary_table = future_months[['Month','Forecast_M','Lower_M','Upper_M']].reset_index(drop=True)
summary_table.columns = ['Month', 'Forecast ($M)', 'Lower Bound ($M)', 'Upper Bound ($M)']

print("\n    12-Month Revenue Forecast:")
print("    " + "─" * 55)
for _, row in summary_table.iterrows():
    print(f"    {row['Month']:<18} ${row['Forecast ($M)']:.2f}M   "
          f"[${row['Lower Bound ($M)']:.2f}M – ${row['Upper Bound ($M)']:.2f}M]")

total_forecast = summary_table['Forecast ($M)'].sum()
print("    " + "─" * 55)
print(f"    {'TOTAL (12 months)':<18} ${total_forecast:.2f}M")

# ── Chart 3: Forecast Bar Chart ────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

bars = ax.bar(summary_table['Month'], summary_table['Forecast ($M)'],
              color='#1E2761', edgecolor='white', alpha=0.85)

ax.errorbar(
    x=range(len(summary_table)),
    y=summary_table['Forecast ($M)'],
    yerr=[
        summary_table['Forecast ($M)'] - summary_table['Lower Bound ($M)'],
        summary_table['Upper Bound ($M)'] - summary_table['Forecast ($M)']
    ],
    fmt='none', color='#F4A261', capsize=5, linewidth=1.5
)

for bar, val in zip(bars, summary_table['Forecast ($M)']):
    ax.text(bar.get_x() + bar.get_width()/2, val + 0.1,
            f'${val:.1f}M', ha='center', fontsize=9, color='#1E2761', fontweight='bold')

ax.set_title('12-Month Revenue Forecast — Combined Entity (Jul 2025 – Jun 2026)',
             fontsize=14, fontweight='bold', color='#1E2761', pad=15)
ax.set_xlabel('Month', fontsize=11)
ax.set_ylabel('Forecasted Revenue ($M)', fontsize=11)
ax.tick_params(axis='x', rotation=45)
ax.grid(False)

plt.tight_layout()
save_chart(fig, "14_forecast_bar.png")

# ── Save forecast table to CSV ─────────────────────────────────
summary_table.to_csv(os.path.join(OUTPUT_DIR, "revenue_forecast_2025_2026.csv"), index=False)
print(f"\n    ✓ Forecast table saved to outputs/revenue_forecast_2025_2026.csv")

print("\n" + "=" * 60)
print("✅ Step 7b Complete!")
print(f"   Total forecasted revenue (next 12 months): ${total_forecast:.1f}M")
print("   Charts saved:")
print("   → 11_combined_forecast.png")
print("   → 12_forecast_components.png")
print("   → 13_chain_forecasts.png")
print("   → 14_forecast_bar.png")
print("=" * 60)