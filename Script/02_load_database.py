"""
Step 2: Load Clean Data into SQLite Database
=============================================
Loads the cleaned merged dataset into a SQLite database
with proper table structure for efficient querying.

Tables created:
  - orders        : main fact table (all 40,000 rows)
  - restaurants   : unique restaurant locations
  - products      : unique menu items
  - customers     : unique customers

Output:
  - data/restaurant.db
"""

import pandas as pd
import sqlite3
import os

# ── Paths ──────────────────────────────────────────────────────
DATA_DIR    = r"C:\Users\HP\Desktop\Restruant_Project\data"
MERGED_CSV  = os.path.join(DATA_DIR, "merged_clean.csv")
DB_PATH     = os.path.join(DATA_DIR, "restaurant.db")

print("=" * 60)
print("STEP 2: LOADING DATA INTO SQLITE DATABASE")
print("=" * 60)

# ── Load clean CSV ─────────────────────────────────────────────
print("\n[1] Loading merged_clean.csv...")
df = pd.read_csv(MERGED_CSV)
print(f"    Loaded {len(df):,} rows x {len(df.columns)} columns")

# ── Connect to SQLite ──────────────────────────────────────────
print("\n[2] Connecting to SQLite database...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
print(f"    Database created at: {DB_PATH}")

# ── Create Tables ──────────────────────────────────────────────
print("\n[3] Creating tables...")

# Drop tables if they exist (fresh load)
cursor.executescript("""
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS restaurants;
    DROP TABLE IF EXISTS products;
    DROP TABLE IF EXISTS customers;
""")

# Main orders table
cursor.execute("""
    CREATE TABLE orders (
        id                    INTEGER PRIMARY KEY AUTOINCREMENT,
        chain                 TEXT,
        customer_id           TEXT,
        order_number          INTEGER,
        restaurant_id         INTEGER,
        order_purchase_date   TEXT,
        order_purchase_time   TEXT,
        time_of_day           TEXT,
        order_month           INTEGER,
        order_month_name      TEXT,
        order_year            INTEGER,
        season                TEXT,
        order_purchase_method TEXT,
        coupon_used           TEXT,
        alcohol_purchased     TEXT,
        gender                TEXT,
        has_children          TEXT,
        item_number           INTEGER,
        item_description      TEXT,
        item_code             TEXT,
        item_category         TEXT,
        quantity              INTEGER,
        menu_price            REAL,
        item_total_cost       REAL,
        profit                REAL,
        order_total_cost      REAL
    )
""")
print("    ✓ orders table created")

# Restaurants dimension table
cursor.execute("""
    CREATE TABLE restaurants (
        restaurant_id     INTEGER PRIMARY KEY,
        restaurant_city   TEXT,
        restaurant_state  TEXT,
        restaurant_zip    INTEGER,
        chain             TEXT
    )
""")
print("    ✓ restaurants table created")

# Products dimension table
cursor.execute("""
    CREATE TABLE products (
        item_number      INTEGER PRIMARY KEY,
        item_description TEXT,
        item_code        TEXT,
        item_category    TEXT,
        menu_price       REAL,
        chain            TEXT
    )
""")
print("    ✓ products table created")

# Customers dimension table
cursor.execute("""
    CREATE TABLE customers (
        customer_id  TEXT PRIMARY KEY,
        gender       TEXT,
        has_children TEXT,
        chain        TEXT
    )
""")
print("    ✓ customers table created")

# ── Load Data into Tables ──────────────────────────────────────
print("\n[4] Loading data into tables...")

# Load main orders table
orders_cols = [
    'chain', 'customer_id', 'order_number', 'restaurant_id',
    'order_purchase_date', 'order_purchase_time', 'time_of_day',
    'order_month', 'order_month_name', 'order_year', 'season',
    'order_purchase_method', 'coupon_used', 'alcohol_purchased',
    'gender', 'has_children', 'item_number', 'item_description',
    'item_code', 'item_category', 'quantity', 'menu_price',
    'item_total_cost', 'Profit', 'order_total_cost'
]
df[orders_cols].rename(columns={'Profit': 'profit'}).to_sql(
    'orders', conn, if_exists='append', index=False
)
print(f"    ✓ orders table loaded: {len(df):,} rows")

# Load restaurants dimension
restaurants = df[[
    'restaurant_id', 'restaurant_city', 'restaurant_state',
    'restaurant_zip_code', 'chain'
]].drop_duplicates(subset=['restaurant_id'])
restaurants = restaurants.rename(columns={'restaurant_zip_code': 'restaurant_zip'})
restaurants.to_sql('restaurants', conn, if_exists='append', index=False)
print(f"    ✓ restaurants table loaded: {len(restaurants):,} unique restaurants")

# Load products dimension
products = df[[
    'item_number', 'item_description', 'item_code',
    'item_category', 'menu_price', 'chain'
]].drop_duplicates(subset=['item_number', 'chain'])
products.to_sql('products', conn, if_exists='append', index=False)
print(f"    ✓ products table loaded: {len(products):,} unique products")

# Load customers dimension
customers = df[[
    'customer_id', 'gender', 'has_children', 'chain'
]].drop_duplicates(subset=['customer_id'])
customers.to_sql('customers', conn, if_exists='append', index=False)
print(f"    ✓ customers table loaded: {len(customers):,} unique customers")

# ── Verify with test queries ───────────────────────────────────
print("\n[5] Running verification queries...")

queries = {
    "Total orders"          : "SELECT COUNT(*) FROM orders",
    "Orders by chain"       : "SELECT chain, COUNT(*) as total FROM orders GROUP BY chain",
    "Total profit"          : "SELECT ROUND(SUM(profit), 2) as total_profit FROM orders",
    "Unique restaurants"    : "SELECT COUNT(*) FROM restaurants",
    "Unique products"       : "SELECT COUNT(*) FROM products",
    "Unique customers"      : "SELECT COUNT(*) FROM customers",
    "Categories"            : "SELECT DISTINCT item_category FROM orders ORDER BY item_category",
}

for label, query in queries.items():
    result = pd.read_sql_query(query, conn)
    print(f"\n    {label}:")
    print(result.to_string(index=False))

# ── Close connection ───────────────────────────────────────────
conn.commit()
conn.close()

print("\n" + "=" * 60)
print("✅ Step 2 Complete!")
print(f"   Database saved to: {DB_PATH}")
print("=" * 60)