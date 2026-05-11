import duckdb
import pandas as pd
import numpy as np
from datetime import date, timedelta
import os
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/anomaly_demo/.env"))

DB_PATH = os.getenv("DUCKDB_PATH")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

np.random.seed(42)
START_DATE = date(2024, 1, 1)
DAYS = 90

def date_range(days):
    return [START_DATE + timedelta(d) for d in range(days)]

dates = date_range(DAYS)

# ── 1. ORDERS ──────────────────────────────────────────────────────────────
order_rows = []
order_id = 1
for i, d in enumerate(dates):
    # Normal: 80-120 orders/day, revenue $50-$300 each
    n_orders = np.random.randint(80, 120)

    # ANOMALY 1: Revenue spike on day 45 (flash sale / pricing bug)
    revenue_multiplier = 8.0 if i == 45 else 1.0

    # ANOMALY 2: Row count drop on day 67 (ETL failure — only 12 orders)
    if i == 67:
        n_orders = 12

    for _ in range(n_orders):
        revenue = round(np.random.uniform(50, 300) * revenue_multiplier, 2)
        order_rows.append({
            "order_id":    order_id,
            "customer_id": np.random.randint(1000, 9999),
            "order_date":  d,
            "revenue":     revenue,
            "status":      np.random.choice(
                               ["completed","pending","cancelled"],
                               p=[0.85, 0.10, 0.05]
                           ),
            "channel":     np.random.choice(
                               ["web","mobile","store"],
                               p=[0.55, 0.35, 0.10]
                           ),
        })
        order_id += 1

orders_df = pd.DataFrame(order_rows)

# ── 2. TRANSACTIONS ────────────────────────────────────────────────────────
txn_rows = []
txn_id = 1
for i, d in enumerate(dates):
    n_txns = np.random.randint(90, 130)
    for _ in range(n_txns):
        # ANOMALY 3: Null payment_method surge on day 55 (checkout API change)
        if i == 55:
            payment = None if np.random.random() < 0.47 else \
                      np.random.choice(["card","upi","netbanking","wallet"])
        else:
            payment = np.random.choice(
                          ["card","upi","netbanking","wallet"],
                          p=[0.50, 0.25, 0.15, 0.10]
                      ) if np.random.random() > 0.08 else None

        txn_rows.append({
            "txn_id":         txn_id,
            "order_id":       np.random.randint(1, order_id),
            "txn_date":       d,
            "amount":         round(np.random.uniform(50, 500), 2),
            "payment_method": payment,
            "gateway":        np.random.choice(["razorpay","stripe","paypal"]),
            "status":         np.random.choice(
                                  ["success","failed","pending"],
                                  p=[0.92, 0.05, 0.03]
                              ),
        })
        txn_id += 1

txns_df = pd.DataFrame(txn_rows)

# ── 3. CUSTOMERS ───────────────────────────────────────────────────────────
cust_rows = []
cust_id = 1
for i, d in enumerate(dates):
    # Normal: 15-30 new signups/day
    # ANOMALY 4: Flatline days 30-32 (registration form outage)
    n_signups = 0 if i in [30, 31, 32] else np.random.randint(15, 30)
    for _ in range(n_signups):
        cust_rows.append({
            "customer_id":  cust_id,
            "signup_date":  d,
            "city":         np.random.choice(
                                ["Mumbai","Delhi","Bangalore","Chennai",
                                 "Hyderabad","Pune","Kolkata"],
                                p=[0.20,0.18,0.17,0.12,0.12,0.11,0.10]
                            ),
            "age_group":    np.random.choice(
                                ["18-25","26-35","36-45","46+"],
                                p=[0.30, 0.40, 0.20, 0.10]
                            ),
            "segment":      np.random.choice(
                                ["new","returning","vip"],
                                p=[0.60, 0.30, 0.10]
                            ),
        })
        cust_id += 1

customers_df = pd.DataFrame(cust_rows)

# ── 4. INVENTORY ───────────────────────────────────────────────────────────
skus = [f"SKU-{i:04d}" for i in range(1, 101)]
inv_rows = []
for i, d in enumerate(dates):
    for sku in skus:
        # ANOMALY 5: 12 SKUs drop to zero on day 72 (missed replenishment)
        if i == 72 and sku in skus[:12]:
            stock = 0
        else:
            stock = np.random.randint(10, 500)
        inv_rows.append({
            "sku":        sku,
            "snap_date":  d,
            "stock_qty":  stock,
            "warehouse":  np.random.choice(["WH-North","WH-South","WH-West"]),
            "reorder_pt": 20,
        })

inventory_df = pd.DataFrame(inv_rows)

# ── 5. RETURNS ─────────────────────────────────────────────────────────────
ret_rows = []
ret_id = 1
for i, d in enumerate(dates):
    n_orders_today = len(orders_df[orders_df["order_date"] == d])
    # Normal return rate: ~4%
    # ANOMALY 6: Return spike on day 78 (bad batch from flash sale day 45)
    rate = 0.28 if i == 78 else 0.04
    n_returns = max(1, int(n_orders_today * rate))
    for _ in range(n_returns):
        ret_rows.append({
            "return_id":  ret_id,
            "order_id":   np.random.randint(1, order_id),
            "return_date": d,
            "reason":     np.random.choice(
                              ["defective","wrong_item","changed_mind","damaged"],
                              p=[0.35, 0.25, 0.25, 0.15]
                          ),
            "refund_amt": round(np.random.uniform(50, 300), 2),
        })
        ret_id += 1

returns_df = pd.DataFrame(ret_rows)

# ── WRITE TO DUCKDB ────────────────────────────────────────────────────────
con = duckdb.connect(DB_PATH)

con.execute("CREATE SCHEMA IF NOT EXISTS raw")
con.execute("CREATE SCHEMA IF NOT EXISTS audit")

tables = {
    "raw.orders":     orders_df,
    "raw.transactions": txns_df,
    "raw.customers":  customers_df,
    "raw.inventory":  inventory_df,
    "raw.returns":    returns_df,
}

for tbl, df in tables.items():
    con.execute(f"DROP TABLE IF EXISTS {tbl}")
    con.execute(f"CREATE TABLE {tbl} AS SELECT * FROM df")
    count = con.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
    print(f"✅ {tbl:<25} {count:>7,} rows")

# ── AUDIT TABLE ────────────────────────────────────────────────────────────
con.execute("""
    CREATE TABLE IF NOT EXISTS audit.anomaly_results (
        id              INTEGER,
        detected_at     TIMESTAMP DEFAULT current_timestamp,
        table_name      VARCHAR,
        check_type      VARCHAR,
        anomaly_date    DATE,
        metric_name     VARCHAR,
        actual_value    DOUBLE,
        expected_value  DOUBLE,
        z_score         DOUBLE,
        severity        VARCHAR,
        llm_explanation TEXT,
        resolved        BOOLEAN DEFAULT FALSE
    )
""")
print("✅ audit.anomaly_results   table ready")

con.close()
print("\n🎉 DuckDB warehouse seeded at:", DB_PATH)
