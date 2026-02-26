"""
Step 1: Data Cleaning & Merging Pipeline
=========================================
Cleans ABC.xlsx and XYZ.xlsx and produces a single merged dataset.

Issues addressed:
  ABC:
    - 1,952 rows with corrupted dates (stored as Excel serial numbers → 1970-01-01)
    - Inconsistent item_category casing/naming vs XYZ
    - order_number stored as object (string) instead of int

  XYZ:
    - item_product_cost column entirely null (20,000 missing values) — dropped
    - Has an extra column (item_product_cost) not present in ABC
    - Inconsistent item_category naming vs ABC

  Both:
    - item_category names differ between files (e.g. 'salad' vs 'Salads')
    - No 'source' column to distinguish ABC from XYZ after merging

Outputs:
  - data/abc_clean.csv
  - data/xyz_clean.csv
  - data/merged_clean.csv
  - data/cleaning_log.txt
"""

import pandas as pd
import numpy as np
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ABC_PATH = r"C:\Users\HP\Desktop\Restruant_Project\raw\ABC.xlsx"
XYZ_PATH = r"C:\Users\HP\Desktop\Restruant_Project\raw\XYZ.xlsx"
DATA_OUT = r"C:\Users\HP\Desktop\Restruant_Project\data"
os.makedirs(DATA_OUT, exist_ok=True)

log_lines = []

def log(msg):
    print(msg)
    log_lines.append(msg)

log("=" * 60)
log("DATA CLEANING PIPELINE — ABC & XYZ Restaurant Chains")
log("=" * 60)

# ══════════════════════════════════════════════════════════════
# 1. LOAD RAW DATA
# ══════════════════════════════════════════════════════════════
log("\n[1] Loading raw data...")
abc_raw = pd.read_excel(ABC_PATH)
xyz_raw = pd.read_excel(XYZ_PATH)
log(f"    ABC raw shape : {abc_raw.shape}")
log(f"    XYZ raw shape : {xyz_raw.shape}")

# Work on copies
abc = abc_raw.copy()
xyz = xyz_raw.copy()

# ══════════════════════════════════════════════════════════════
# 2. ADD SOURCE COLUMN FIRST (before any changes)
# ══════════════════════════════════════════════════════════════
log("\n[2] Adding source identifier column...")
abc['chain'] = 'ABC'
xyz['chain'] = 'XYZ'

# ══════════════════════════════════════════════════════════════
# 3. CLEAN ABC
# ══════════════════════════════════════════════════════════════
log("\n[3] Cleaning ABC dataset...")

# 3a. Fix dates — convert to datetime, flag corrupt 1970 rows as NaT
abc['order_purchase_date'] = pd.to_datetime(abc['order_purchase_date'], errors='coerce')
bad_date_mask = abc['order_purchase_date'].dt.year == 1970
abc.loc[bad_date_mask, 'order_purchase_date'] = pd.NaT
n_bad = bad_date_mask.sum()
log(f"    [DATE] {n_bad} corrupt dates (1970 epoch errors) set to NaT.")
log(f"    [DATE] These represent {round(n_bad/len(abc)*100,2)}% of ABC rows — documented as data integrity issue.")

# 3b. Fix order_number dtype
abc['order_number'] = pd.to_numeric(abc['order_number'], errors='coerce').astype('Int64')
log(f"    [DTYPE] order_number converted from object → Int64")

# 3c. Standardise item_category (title case, fix plurals to match XYZ)
category_map_abc = {
    'salad'     : 'Salads',
    'Pasta'     : 'Pasta',
    'Pizza'     : 'Pizza',
    'Sandwich'  : 'Sandwiches',
    'Appetizers': 'Appetizers',
    'Beverages' : 'Beverages',
}
abc['item_category'] = abc['item_category'].map(category_map_abc).fillna(abc['item_category'])
log(f"    [CATEGORY] ABC item_category standardised: {sorted(abc['item_category'].unique())}")

# 3d. Standardise time column to string HH:MM
abc['order_purchase_time'] = pd.to_datetime(
    abc['order_purchase_time'].astype(str), format='%H:%M:%S', errors='coerce'
).dt.strftime('%H:%M')

# 3e. Add derived time-of-day flag (AM / PM)
abc['time_of_day'] = abc['order_purchase_time'].apply(
    lambda t: 'AM' if pd.notna(t) and int(t.split(':')[0]) < 12 else 'PM'
)

# 3f. Add month, month_name, season, year columns (only for valid dates)
abc['order_month']      = abc['order_purchase_date'].dt.month
abc['order_month_name'] = abc['order_purchase_date'].dt.strftime('%B')
abc['order_year']       = abc['order_purchase_date'].dt.year

def get_season(month):
    if pd.isna(month): return np.nan
    m = int(month)
    if m in [12, 1, 2]: return 'Winter'
    elif m in [3, 4, 5]: return 'Spring'
    elif m in [6, 7, 8]: return 'Summer'
    else:                return 'Fall'

abc['season'] = abc['order_month'].apply(get_season)

# 3g. Rename binary columns to descriptive strings for readability
abc['coupon_used']          = abc['coupon_y_n'].map({'Y': 'Yes', 'N': 'No'})
abc['alcohol_purchased']    = abc['order_alcohol_purchased'].map({1: 'Yes', 0: 'No'})
abc['has_children']         = abc['customer_with_children'].map({1: 'Yes', 0: 'No'})
abc['gender']               = abc['gender_customer_payee']  # already M/F

log(f"    [DERIVED] Added: time_of_day, order_month, order_month_name, order_year, season")
log(f"    [DERIVED] Added readable labels: coupon_used, alcohol_purchased, has_children, gender")

# ══════════════════════════════════════════════════════════════
# 4. CLEAN XYZ
# ══════════════════════════════════════════════════════════════
log("\n[4] Cleaning XYZ dataset...")

# 4a. Drop item_product_cost — entirely null (100% missing)
xyz = xyz.drop(columns=['item_product_cost'])
log(f"    [DROP] 'item_product_cost' dropped — 100% null (20,000 missing values).")

# 4b. Parse dates
xyz['order_purchase_date'] = pd.to_datetime(xyz['order_purchase_date'], errors='coerce')
bad_xyz = (xyz['order_purchase_date'].dt.year < 2015).sum()
log(f"    [DATE] XYZ date range: {xyz['order_purchase_date'].min().date()} → {xyz['order_purchase_date'].max().date()}")
log(f"    [DATE] Suspicious dates (pre-2015): {bad_xyz}")

# 4c. Standardise item_category
category_map_xyz = {
    'Pizza'     : 'Pizza',
    'Dessert'   : 'Dessert',
    'Appetizers': 'Appetizers',
    'Salads'    : 'Salads',
    'Pasta'     : 'Pasta',
    'Sandwiches': 'Sandwiches',
    'Beverage'  : 'Beverages',  # standardise singular → plural
}
xyz['item_category'] = xyz['item_category'].map(category_map_xyz).fillna(xyz['item_category'])
log(f"    [CATEGORY] XYZ item_category standardised: {sorted(xyz['item_category'].unique())}")

# 4d. Standardise time column
xyz['order_purchase_time'] = pd.to_datetime(
    xyz['order_purchase_time'].astype(str), format='%H:%M:%S', errors='coerce'
).dt.strftime('%H:%M')

# 4e. Derived columns (same as ABC)
xyz['time_of_day']       = xyz['order_purchase_time'].apply(
    lambda t: 'AM' if pd.notna(t) and int(t.split(':')[0]) < 12 else 'PM'
)
xyz['order_month']       = xyz['order_purchase_date'].dt.month
xyz['order_month_name']  = xyz['order_purchase_date'].dt.strftime('%B')
xyz['order_year']        = xyz['order_purchase_date'].dt.year
xyz['season']            = xyz['order_month'].apply(get_season)

xyz['coupon_used']       = xyz['coupon_y_n'].map({'Y': 'Yes', 'N': 'No'})
xyz['alcohol_purchased'] = xyz['order_alcohol_purchased'].map({1: 'Yes', 0: 'No'})
xyz['has_children']      = xyz['customer_with_children'].map({1: 'Yes', 0: 'No'})
xyz['gender']            = xyz['gender_customer_payee']

log(f"    [DERIVED] Added same derived columns as ABC")

# ══════════════════════════════════════════════════════════════
# 5. ALIGN COLUMNS BEFORE MERGING
# ══════════════════════════════════════════════════════════════
log("\n[5] Aligning columns for merge...")

# Define the unified column set (ABC has no item_product_cost, XYZ dropped it)
# Reorder both to same column order
shared_cols = [
    'chain', 'customer_id', 'order_number', 'restaurant_id',
    'restaurant_city', 'restaurant_state', 'restaurant_zip_code',
    'order_purchase_date', 'order_purchase_time', 'time_of_day',
    'order_month', 'order_month_name', 'order_year', 'season',
    'order_purchase_method', 'coupon_used', 'alcohol_purchased',
    'gender', 'has_children',
    'item_number', 'item_description', 'item_code', 'item_category',
    'quantity', 'menu_price', 'item_total_cost', 'Profit',
    'order_total_cost',
]

abc_clean = abc[shared_cols].copy()
xyz_clean = xyz[shared_cols].copy()

log(f"    ABC clean columns: {abc_clean.shape[1]}")
log(f"    XYZ clean columns: {xyz_clean.shape[1]}")

# ══════════════════════════════════════════════════════════════
# 6. MERGE
# ══════════════════════════════════════════════════════════════
log("\n[6] Merging ABC + XYZ into single dataset...")
merged = pd.concat([abc_clean, xyz_clean], ignore_index=True)
log(f"    Merged shape: {merged.shape}")
log(f"    ABC rows: {(merged['chain']=='ABC').sum()} | XYZ rows: {(merged['chain']=='XYZ').sum()}")

# ══════════════════════════════════════════════════════════════
# 7. FINAL VALIDATION
# ══════════════════════════════════════════════════════════════
log("\n[7] Final validation of merged dataset...")
log(f"    Total null values per column:")
nulls = merged.isnull().sum()
nulls = nulls[nulls > 0]
for col, n in nulls.items():
    log(f"      {col}: {n} nulls ({round(n/len(merged)*100,2)}%)")

log(f"\n    item_category values in merged: {sorted(merged['item_category'].unique())}")
log(f"    chain values: {merged['chain'].unique()}")
log(f"    Date range: {merged['order_purchase_date'].min()} → {merged['order_purchase_date'].max()}")
log(f"    Total rows: {len(merged):,}")
log(f"    Total columns: {len(merged.columns)}")

# ══════════════════════════════════════════════════════════════
# 8. SAVE OUTPUTS
# ══════════════════════════════════════════════════════════════
log("\n[8] Saving outputs...")
abc_clean.to_csv(os.path.join(DATA_OUT, "abc_clean.csv"), index=False)
xyz_clean.to_csv(os.path.join(DATA_OUT, "xyz_clean.csv"), index=False)
merged.to_csv(os.path.join(DATA_OUT, "merged_clean.csv"), index=False)

with open(os.path.join(DATA_OUT, "cleaning_log.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

log("\n✅ Pipeline complete!")
log(f"   → data/abc_clean.csv")
log(f"   → data/xyz_clean.csv")
log(f"   → data/merged_clean.csv")
log(f"   → data/cleaning_log.txt")