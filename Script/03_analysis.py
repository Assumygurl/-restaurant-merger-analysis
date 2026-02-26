"""
Step 3: Exploratory Analysis & Visualizations
==============================================
Answers all business questions from the project instructions
and generates charts saved to the outputs/charts folder.

Business Questions Answered:
  1. Spending trends by month, season, gender, region, children
  2. Best and worst selling products
  3. Profitability of products
  4. Summary statistics for all key variables
  5. AM vs PM spending patterns
  6. Purchase method breakdown
  7. Chain comparison (ABC vs XYZ)

Outputs:
  - outputs/charts/*.png  (all visualizations)
  - outputs/summary_stats.csv
"""

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

# ── Paths ──────────────────────────────────────────────────────
DATA_DIR    = r"C:\Users\HP\Desktop\Restruant_Project\data"
OUTPUT_DIR  = r"C:\Users\HP\Desktop\Restruant_Project\outputs"
CHARTS_DIR  = os.path.join(OUTPUT_DIR, "charts")
DB_PATH     = os.path.join(DATA_DIR, "restaurant.db")

os.makedirs(CHARTS_DIR, exist_ok=True)

# ── Style ──────────────────────────────────────────────────────
sns.set_theme(style="white" , palette="muted")
COLORS      = {"ABC": "#2196F3", "XYZ": "#FF5722"}
CAT_COLORS  = sns.color_palette("muted", 8)
plt.rcParams.update({'figure.dpi': 150, 'font.size': 10})

print("=" * 60)
print("STEP 3: EXPLORATORY ANALYSIS & VISUALIZATIONS")
print("=" * 60)

# ── Connect ────────────────────────────────────────────────────
conn = sqlite3.connect(DB_PATH)

def save_chart(fig, filename):
    path = os.path.join(CHARTS_DIR, filename)
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)
    print(f"    ✓ Saved: {filename}")

# ══════════════════════════════════════════════════════════════
# CHART 1: Revenue by Chain (ABC vs XYZ)
# ══════════════════════════════════════════════════════════════
print("\n[1] Chain comparison...")
chain_df = pd.read_sql_query("""
    SELECT chain,
           ROUND(SUM(order_total_cost)/1000000, 2) as revenue_millions,
           ROUND(SUM(profit)/1000000, 2)            as profit_millions,
           COUNT(DISTINCT order_number)             as total_orders
    FROM orders GROUP BY chain
""", conn)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle('ABC vs XYZ: Chain Performance Comparison', fontsize=14, fontweight='bold')

axes[0].bar(chain_df['chain'], chain_df['revenue_millions'],
            color=[COLORS['ABC'], COLORS['XYZ']], edgecolor='white', width=0.5)
axes[0].set_title('Total Revenue (Millions $)')
axes[0].set_ylabel('Revenue ($M)')
for i, v in enumerate(chain_df['revenue_millions']):
    axes[0].text(i, v + 0.5, f'${v}M', ha='center', fontweight='bold')

axes[1].bar(chain_df['chain'], chain_df['profit_millions'],
            color=[COLORS['ABC'], COLORS['XYZ']], edgecolor='white', width=0.5)
axes[1].set_title('Total Profit (Millions $)')
axes[1].set_ylabel('Profit ($M)')
for i, v in enumerate(chain_df['profit_millions']):
    axes[1].text(i, v + 0.5, f'${v}M', ha='center', fontweight='bold')

save_chart(fig, "01_chain_comparison.png")

# ══════════════════════════════════════════════════════════════
# CHART 2: Monthly Revenue Trend
# ══════════════════════════════════════════════════════════════
print("\n[2] Monthly spending trends...")
monthly = pd.read_sql_query("""
    SELECT chain, order_year, order_month, order_month_name,
           ROUND(SUM(order_total_cost)/1000, 2) as revenue_k,
           ROUND(SUM(profit)/1000, 2) as profit_k
    FROM orders
    WHERE order_purchase_date IS NOT NULL
    GROUP BY chain, order_year, order_month
    ORDER BY order_year, order_month
""", conn)

monthly['period'] = monthly['order_month_name'] + ' ' + monthly['order_year'].astype(str)

fig, ax = plt.subplots(figsize=(14, 6))
for chain, grp in monthly.groupby('chain'):
    ax.plot(range(len(grp)), grp['revenue_k'],
            marker='o', label=chain, color=COLORS[chain], linewidth=2)

all_periods = monthly.drop_duplicates(subset=['order_year','order_month'])\
                      .sort_values(['order_year','order_month'])['period'].tolist()
ax.set_xticks(range(len(all_periods)))
ax.set_xticklabels(all_periods, rotation=45, ha='right', fontsize=8)
ax.set_title('Monthly Revenue Trend by Chain', fontsize=14, fontweight='bold')
ax.set_ylabel('Revenue ($K)')
ax.legend()
save_chart(fig, "02_monthly_revenue_trend.png")

# ══════════════════════════════════════════════════════════════
# CHART 3: Spending by Season
# ══════════════════════════════════════════════════════════════
print("\n[3] Seasonal spending...")
season_order = ['Spring', 'Summer', 'Fall', 'Winter']
season_df = pd.read_sql_query("""
    SELECT chain, season,
           ROUND(SUM(order_total_cost)/1000, 2) as revenue_k,
           ROUND(AVG(order_total_cost), 2) as avg_order
    FROM orders WHERE season IS NOT NULL
    GROUP BY chain, season
""", conn)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Spending by Season', fontsize=14, fontweight='bold')

for i, (chain, grp) in enumerate(season_df.groupby('chain')):
    grp = grp.set_index('season').reindex(season_order)
    axes[i].bar(grp.index, grp['revenue_k'], color=COLORS[chain], edgecolor='white')
    axes[i].set_title(f'{chain} — Revenue by Season ($K)')
    axes[i].set_ylabel('Revenue ($K)')
    for j, v in enumerate(grp['revenue_k']):
        if pd.notna(v):
            axes[i].text(j, v + 100, f'${v:.0f}K', ha='center', fontsize=9)

save_chart(fig, "03_seasonal_spending.png")

# ══════════════════════════════════════════════════════════════
# CHART 4: Spending by Gender
# ══════════════════════════════════════════════════════════════
print("\n[4] Gender spending analysis...")
gender_df = pd.read_sql_query("""
    SELECT chain, gender,
           ROUND(SUM(order_total_cost)/1000, 2) as revenue_k,
           ROUND(AVG(order_total_cost), 2) as avg_order,
           COUNT(*) as orders
    FROM orders GROUP BY chain, gender
""", conn)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle('Spending by Gender', fontsize=14, fontweight='bold')

gender_colors = {'M': '#2196F3', 'F': '#E91E63'}
for i, (chain, grp) in enumerate(gender_df.groupby('chain')):
    bars = axes[i].bar(grp['gender'], grp['revenue_k'],
                       color=[gender_colors[g] for g in grp['gender']],
                       edgecolor='white', width=0.4)
    axes[i].set_title(f'{chain} — Revenue by Gender ($K)')
    axes[i].set_ylabel('Revenue ($K)')
    for bar, v in zip(bars, grp['revenue_k']):
        axes[i].text(bar.get_x() + bar.get_width()/2, v + 100,
                     f'${v:.0f}K', ha='center', fontweight='bold')

save_chart(fig, "04_gender_spending.png")

# ══════════════════════════════════════════════════════════════
# CHART 5: Top 10 States by Profit
# ══════════════════════════════════════════════════════════════
print("\n[5] Regional profit analysis...")
state_df = pd.read_sql_query("""
    SELECT r.restaurant_state,
           ROUND(SUM(o.profit)/1000, 2) as profit_k,
           ROUND(SUM(o.order_total_cost)/1000, 2) as revenue_k
    FROM orders o
    JOIN restaurants r ON o.restaurant_id = r.restaurant_id
    GROUP BY r.restaurant_state
    ORDER BY profit_k DESC LIMIT 10
""", conn)

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(state_df['restaurant_state'][::-1],
               state_df['profit_k'][::-1],
               color=sns.color_palette("Blues_d", len(state_df)),
               edgecolor='white')
ax.set_title('Top 10 States by Total Profit ($K)', fontsize=14, fontweight='bold')
ax.set_xlabel('Total Profit ($K)')
for bar, v in zip(bars, state_df['profit_k'][::-1]):
    ax.text(v + 50, bar.get_y() + bar.get_height()/2,
            f'${v:.0f}K', va='center', fontsize=9)
save_chart(fig, "05_top_states_profit.png")

# ══════════════════════════════════════════════════════════════
# CHART 6: Best & Worst Selling Products
# ══════════════════════════════════════════════════════════════
print("\n[6] Product performance...")
products_df = pd.read_sql_query("""
    SELECT item_description, item_category,
           SUM(quantity) as units_sold,
           ROUND(SUM(profit)/1000, 2) as profit_k
    FROM orders
    GROUP BY item_description
    ORDER BY units_sold DESC
""", conn)

top10    = products_df.head(10)
bottom10 = products_df.tail(10)

fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle('Best & Worst Selling Products (by Units Sold)', fontsize=14, fontweight='bold')

axes[0].barh(top10['item_description'][::-1], top10['units_sold'][::-1],
             color='#4CAF50', edgecolor='white')
axes[0].set_title('Top 10 Best Sellers')
axes[0].set_xlabel('Units Sold')

axes[1].barh(bottom10['item_description'][::-1], bottom10['units_sold'][::-1],
             color='#F44336', edgecolor='white')
axes[1].set_title('Bottom 10 Worst Sellers')
axes[1].set_xlabel('Units Sold')

save_chart(fig, "06_best_worst_products.png")

# ══════════════════════════════════════════════════════════════
# CHART 7: Profitability by Category
# ══════════════════════════════════════════════════════════════
print("\n[7] Category profitability...")
cat_df = pd.read_sql_query("""
    SELECT item_category,
           ROUND(SUM(profit)/1000, 2) as profit_k,
           ROUND(AVG(profit), 2) as avg_profit,
           SUM(quantity) as units_sold
    FROM orders
    GROUP BY item_category
    ORDER BY profit_k DESC
""", conn)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Profitability by Food Category', fontsize=14, fontweight='bold')

axes[0].bar(cat_df['item_category'], cat_df['profit_k'],
            color=CAT_COLORS[:len(cat_df)], edgecolor='white')
axes[0].set_title('Total Profit by Category ($K)')
axes[0].set_ylabel('Profit ($K)')
axes[0].tick_params(axis='x', rotation=45)

axes[1].bar(cat_df['item_category'], cat_df['avg_profit'],
            color=CAT_COLORS[:len(cat_df)], edgecolor='white')
axes[1].set_title('Average Profit per Order Line')
axes[1].set_ylabel('Avg Profit ($)')
axes[1].tick_params(axis='x', rotation=45)

save_chart(fig, "07_category_profitability.png")

# ══════════════════════════════════════════════════════════════
# CHART 8: AM vs PM Spending
# ══════════════════════════════════════════════════════════════
print("\n[8] Time of day analysis...")
time_df = pd.read_sql_query("""
    SELECT chain, time_of_day,
           ROUND(SUM(order_total_cost)/1000, 2) as revenue_k,
           ROUND(AVG(order_total_cost), 2) as avg_order,
           COUNT(*) as orders
    FROM orders GROUP BY chain, time_of_day
""", conn)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle('AM vs PM Spending Patterns', fontsize=14, fontweight='bold')

tod_colors = {'AM': '#FF9800', 'PM': '#3F51B5'}
for i, (chain, grp) in enumerate(time_df.groupby('chain')):
    bars = axes[i].bar(grp['time_of_day'], grp['revenue_k'],
                       color=[tod_colors[t] for t in grp['time_of_day']],
                       edgecolor='white', width=0.4)
    axes[i].set_title(f'{chain} — Revenue AM vs PM ($K)')
    axes[i].set_ylabel('Revenue ($K)')
    for bar, v in zip(bars, grp['revenue_k']):
        axes[i].text(bar.get_x() + bar.get_width()/2, v + 100,
                     f'${v:.0f}K', ha='center', fontweight='bold')

save_chart(fig, "08_am_pm_spending.png")

# ══════════════════════════════════════════════════════════════
# CHART 9: Customers With vs Without Children
# ══════════════════════════════════════════════════════════════
print("\n[9] Children vs no children spending...")
children_df = pd.read_sql_query("""
    SELECT chain, has_children,
           ROUND(SUM(order_total_cost)/1000, 2) as revenue_k,
           ROUND(AVG(order_total_cost), 2) as avg_order,
           COUNT(*) as orders
    FROM orders GROUP BY chain, has_children
""", conn)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle('Spending: Customers With vs Without Children', fontsize=14, fontweight='bold')

child_colors = {'Yes': '#9C27B0', 'No': '#009688'}
for i, (chain, grp) in enumerate(children_df.groupby('chain')):
    bars = axes[i].bar(grp['has_children'], grp['revenue_k'],
                       color=[child_colors[c] for c in grp['has_children']],
                       edgecolor='white', width=0.4)
    axes[i].set_title(f'{chain} — Revenue by Children ($K)')
    axes[i].set_xlabel('Has Children')
    axes[i].set_ylabel('Revenue ($K)')
    for bar, v in zip(bars, grp['revenue_k']):
        axes[i].text(bar.get_x() + bar.get_width()/2, v + 100,
                     f'${v:.0f}K', ha='center', fontweight='bold')

save_chart(fig, "09_children_spending.png")

# ══════════════════════════════════════════════════════════════
# CHART 10: Purchase Method Breakdown
# ══════════════════════════════════════════════════════════════
print("\n[10] Purchase method breakdown...")
method_df = pd.read_sql_query("""
    SELECT chain, order_purchase_method,
           COUNT(*) as orders,
           ROUND(SUM(profit)/1000, 2) as profit_k
    FROM orders GROUP BY chain, order_purchase_method
""", conn)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle('Orders by Purchase Method', fontsize=14, fontweight='bold')

method_colors = {'Dine In': '#2196F3', 'Carry Out': '#4CAF50', 'Delivery': '#FF5722'}
for i, (chain, grp) in enumerate(method_df.groupby('chain')):
    axes[i].pie(grp['orders'],
                labels=grp['order_purchase_method'],
                colors=[method_colors[m] for m in grp['order_purchase_method']],
                autopct='%1.1f%%', startangle=90)
    axes[i].set_title(f'{chain}')

save_chart(fig, "10_purchase_method.png")

# ══════════════════════════════════════════════════════════════
# SUMMARY STATISTICS
# ══════════════════════════════════════════════════════════════
print("\n[11] Generating summary statistics...")
summary = pd.read_sql_query("""
    SELECT
        chain,
        COUNT(*) as total_rows,
        ROUND(AVG(order_total_cost), 2) as mean_order_value,
        ROUND(MIN(order_total_cost), 2) as min_order_value,
        ROUND(MAX(order_total_cost), 2) as max_order_value,
        ROUND(AVG(profit), 2) as mean_profit,
        ROUND(MIN(profit), 2) as min_profit,
        ROUND(MAX(profit), 2) as max_profit,
        ROUND(AVG(quantity), 2) as mean_quantity,
        ROUND(AVG(menu_price), 2) as mean_menu_price,
        COUNT(DISTINCT order_number) as unique_orders,
        COUNT(DISTINCT customer_id) as unique_customers,
        COUNT(DISTINCT restaurant_id) as unique_restaurants
    FROM orders GROUP BY chain
""", conn)

summary.to_csv(os.path.join(OUTPUT_DIR, "summary_stats.csv"), index=False)
print(summary.to_string(index=False))

conn.close()

print("\n" + "=" * 60)
print("✅ Step 3 Complete!")
print(f"   10 charts saved to: {CHARTS_DIR}")
print(f"   Summary stats saved to: {OUTPUT_DIR}")
print("=" * 60)