"""
Step 7a: Generate Realistic 2024-2025 Dataset
===============================================
Generates a synthetic but realistic dataset based on the
original ABC & XYZ patterns, updated to 2024-2025 dates.

Changes from original:
  - Dates shifted to January 2024 - June 2025
  - Revenue growth of ~8% built in (post-COVID recovery trend)
  - Seasonal patterns preserved
  - Same restaurants, items, customers structure
  - Slight delivery growth trend (reflects 2024 market)

Output:
  - data/abc_2025.csv
  - data/xyz_2025.csv
  - data/merged_2025.csv
"""

import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime, timedelta

# ── Paths ──────────────────────────────────────────────────────
DATA_DIR  = r"C:\Users\HP\Desktop\Restruant_Project\data"
ABC_CSV   = os.path.join(DATA_DIR, "abc_clean.csv")
XYZ_CSV   = os.path.join(DATA_DIR, "xyz_clean.csv")
DB_PATH   = os.path.join(DATA_DIR, "restaurant_2025.db")

np.random.seed(42)

print("=" * 60)
print("GENERATING 2024-2025 DATASET")
print("=" * 60)

# ── Load original clean data ───────────────────────────────────
print("\n[1] Loading original clean data...")
abc = pd.read_csv(ABC_CSV)
xyz = pd.read_csv(XYZ_CSV)
print(f"    ABC: {len(abc):,} rows | XYZ: {len(xyz):,} rows")

# ── Function to update dataset ─────────────────────────────────
def update_to_2025(df, chain_name, growth_rate=0.08):
    print(f"\n[2] Updating {chain_name} to 2024-2025...")
    df = df.copy()

    # ── Date shifting ──────────────────────────────────────────
    # Original: 2018-2019 → New: 2024-2025 (shift by 6 years)
    df['order_purchase_date'] = pd.to_datetime(df['order_purchase_date'], errors='coerce')

    def shift_date(dt):
        if pd.isna(dt):
            return pd.NaT
        try:
            return dt.replace(year=dt.year + 6)
        except ValueError:
            # Handle Feb 29 leap year edge case
            return dt.replace(year=dt.year + 6, day=28)

    df['order_purchase_date'] = df['order_purchase_date'].apply(shift_date)
    print(f"    Dates shifted: {df['order_purchase_date'].min()} → {df['order_purchase_date'].max()}")

    # ── Update derived date columns ────────────────────────────
    df['order_month']      = df['order_purchase_date'].dt.month
    df['order_month_name'] = df['order_purchase_date'].dt.strftime('%B')
    df['order_year']       = df['order_purchase_date'].dt.year

    # ── Apply revenue growth (8% uplift) ──────────────────────
    growth_factor = 1 + growth_rate
    df['menu_price']       = (df['menu_price'] * growth_factor).round(0).astype(int)
    df['item_total_cost']  = (df['item_total_cost'] * growth_factor).round(0).astype(int)
    df['order_total_cost'] = (df['order_total_cost'] * growth_factor).round(0).astype(int)
    df['profit']           = (df['Profit'] * growth_factor).round(0).astype(int)
    print(f"    Revenue growth of {growth_rate*100:.0f}% applied")

    # ── Reflect 2024 delivery trend (delivery up ~15%) ─────────
    # Increase delivery orders proportion slightly
    delivery_mask = df['order_purchase_method'] == 'Delivery'
    df.loc[delivery_mask, 'order_total_cost'] = (
        df.loc[delivery_mask, 'order_total_cost'] * 1.05
    ).round(0).astype(int)
    print(f"    Delivery uplift of 5% applied (reflecting 2024 trend)")

    # ── Update customer IDs to look fresh ─────────────────────
    prefix = 'ABC2024' if chain_name == 'ABC' else 'XYZ2024'
    df['customer_id'] = [f"{prefix}{str(i).zfill(6)}" for i in range(len(df))]

    # ── Drop old Profit column, keep new profit ────────────────
    if 'Profit' in df.columns:
        df = df.drop(columns=['Profit'])
    df = df.rename(columns={'profit': 'Profit'})

    print(f"    Total revenue: ${df['order_total_cost'].sum()/1e6:.1f}M")
    print(f"    Total profit:  ${df['Profit'].sum()/1e6:.1f}M")

    return df

# ── Update both chains ─────────────────────────────────────────
abc_2025 = update_to_2025(abc, 'ABC', growth_rate=0.08)
xyz_2025 = update_to_2025(xyz, 'XYZ', growth_rate=0.07)

# ── Merge ──────────────────────────────────────────────────────
print("\n[3] Merging into single 2024-2025 dataset...")

# Align columns
shared_cols = [
    'chain', 'customer_id', 'order_number', 'restaurant_id',
    'restaurant_city', 'restaurant_state', 'restaurant_zip_code',
    'order_purchase_date', 'order_purchase_time', 'time_of_day',
    'order_month', 'order_month_name', 'order_year', 'season',
    'order_purchase_method', 'coupon_used', 'alcohol_purchased',
    'gender', 'has_children', 'item_number', 'item_description',
    'item_code', 'item_category', 'quantity', 'menu_price',
    'item_total_cost', 'Profit', 'order_total_cost',
]

# Only keep columns that exist
abc_cols = [c for c in shared_cols if c in abc_2025.columns]
xyz_cols = [c for c in shared_cols if c in xyz_2025.columns]

merged_2025 = pd.concat([
    abc_2025[abc_cols],
    xyz_2025[xyz_cols]
], ignore_index=True)

print(f"    Merged shape: {merged_2025.shape}")
print(f"    Date range: {merged_2025['order_purchase_date'].min()} → {merged_2025['order_purchase_date'].max()}")
print(f"    Total revenue: ${merged_2025['order_total_cost'].sum()/1e6:.1f}M")
print(f"    Total profit:  ${merged_2025['Profit'].sum()/1e6:.1f}M")

# ── Save CSVs ──────────────────────────────────────────────────
print("\n[4] Saving CSV files...")
abc_2025[abc_cols].to_csv(os.path.join(DATA_DIR, "abc_2025.csv"), index=False)
xyz_2025[xyz_cols].to_csv(os.path.join(DATA_DIR, "xyz_2025.csv"), index=False)
merged_2025.to_csv(os.path.join(DATA_DIR, "merged_2025.csv"), index=False)
print("    ✓ abc_2025.csv")
print("    ✓ xyz_2025.csv")
print("    ✓ merged_2025.csv")

# ── Load into new SQLite database ─────────────────────────────
print("\n[5] Loading into SQLite database (restaurant_2025.db)...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.executescript("""
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS restaurants;
    DROP TABLE IF EXISTS products;
    DROP TABLE IF EXISTS customers;
""")

# Orders table
orders_cols = [c for c in shared_cols if c in merged_2025.columns]
merged_2025[orders_cols].rename(columns={'Profit':'profit'}).to_sql(
    'orders', conn, if_exists='append', index=False
)
print(f"    ✓ orders table: {len(merged_2025):,} rows")

# Restaurants
restaurants = merged_2025[[
    'restaurant_id','restaurant_city','restaurant_state',
    'restaurant_zip_code','chain'
]].drop_duplicates(subset=['restaurant_id']).rename(
    columns={'restaurant_zip_code':'restaurant_zip'}
)
restaurants.to_sql('restaurants', conn, if_exists='append', index=False)
print(f"    ✓ restaurants table: {len(restaurants):,} rows")

# Products
products = merged_2025[[
    'item_number','item_description','item_code',
    'item_category','menu_price','chain'
]].drop_duplicates(subset=['item_number','chain'])
products.to_sql('products', conn, if_exists='append', index=False)
print(f"    ✓ products table: {len(products):,} rows")

# Customers
customers = merged_2025[[
    'customer_id','gender','has_children','chain'
]].drop_duplicates(subset=['customer_id'])
customers.to_sql('customers', conn, if_exists='append', index=False)
print(f"    ✓ customers table: {len(customers):,} rows")

# ── Verify ─────────────────────────────────────────────────────
print("\n[6] Verification queries...")
verify = pd.read_sql_query("""
    SELECT chain,
           COUNT(*) as rows,
           MIN(order_purchase_date) as start_date,
           MAX(order_purchase_date) as end_date,
           ROUND(SUM(order_total_cost)/1000000,2) as revenue_M,
           ROUND(SUM(profit)/1000000,2) as profit_M
    FROM orders GROUP BY chain
""", conn)
print(verify.to_string(index=False))

conn.commit()
conn.close()

print("\n" + "=" * 60)
print("✅ 2024-2025 Dataset Generation Complete!")
print(f"   → data/abc_2025.csv")
print(f"   → data/xyz_2025.csv")
print(f"   → data/merged_2025.csv")
print(f"   → data/restaurant_2025.db")
print("=" * 60)