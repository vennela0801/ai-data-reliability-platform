import os
import duckdb
import pandas as pd
import numpy as np
from scipy.stats import zscore
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/anomaly_demo/.env"))

DB_PATH = os.getenv("DUCKDB_PATH")

con = duckdb.connect(DB_PATH)

# ───────────────────────────────────────────────────────────────
# Detection configuration
# ───────────────────────────────────────────────────────────────

CHECKS = [
    {
        "table": "marts.fct_orders_daily",
        "date_col": "order_date",
        "metric": "total_revenue",
        "type": "revenue_spike"
    },
    {
        "table": "marts.fct_orders_daily",
        "date_col": "order_date",
        "metric": "order_count",
        "type": "row_count_drop"
    },
    {
        "table": "marts.fct_transactions_daily",
        "date_col": "txn_date",
        "metric": "null_payment_rate",
        "type": "null_rate_surge"
    },
    {
        "table": "marts.fct_customers_daily",
        "date_col": "signup_date",
        "metric": "new_signups",
        "type": "signup_flatline"
    },
]

# ───────────────────────────────────────────────────────────────
# Severity logic
# ───────────────────────────────────────────────────────────────

def severity_from_z(z):
    z = abs(z)

    if z >= 5:
        return "critical"
    elif z >= 4:
        return "high"
    elif z >= 3:
        return "medium"
    else:
        return "low"

# ───────────────────────────────────────────────────────────────
# Run checks
# ───────────────────────────────────────────────────────────────

all_results = []

for check in CHECKS:

    query = f"""
        SELECT
            {check['date_col']} AS metric_date,
            {check['metric']} AS metric_value
        FROM {check['table']}
        ORDER BY 1
    """

    df = con.execute(query).df()

    values = df["metric_value"].astype(float)

    df["z_score"] = zscore(values)

    mean_val = values.mean()

    anomalies = df[np.abs(df["z_score"]) >= 3]

    print(f"\n🔍 {check['table']} → {check['metric']}")
    print(f"   Found {len(anomalies)} anomalies")

    for _, row in anomalies.iterrows():

        result = {
            "table_name": check["table"],
            "check_type": check["type"],
            "anomaly_date": row["metric_date"],
            "metric_name": check["metric"],
            "actual_value": float(row["metric_value"]),
            "expected_value": float(mean_val),
            "z_score": float(row["z_score"]),
            "severity": severity_from_z(row["z_score"]),
        }

        all_results.append(result)

# ───────────────────────────────────────────────────────────────
# Write to audit table
# ───────────────────────────────────────────────────────────────

if all_results:

    results_df = pd.DataFrame(all_results)

    max_id = con.execute("""
        SELECT COALESCE(MAX(id), 0)
        FROM audit.anomaly_results
    """).fetchone()[0]

    results_df["id"] = range(max_id + 1, max_id + 1 + len(results_df))

    results_df["llm_explanation"] = None
    results_df["resolved"] = False

    cols = [
        "id",
        "table_name",
        "check_type",
        "anomaly_date",
        "metric_name",
        "actual_value",
        "expected_value",
        "z_score",
        "severity",
        "llm_explanation",
        "resolved",
    ]

    con.register("results_df", results_df[cols])

    con.execute("""
        INSERT INTO audit.anomaly_results
        (
            id,
            table_name,
            check_type,
            anomaly_date,
            metric_name,
            actual_value,
            expected_value,
            z_score,
            severity,
            llm_explanation,
            resolved
        )
        SELECT * FROM results_df
    """)

    print(f"\n✅ Inserted {len(results_df)} anomalies into audit table")

else:
    print("\n✅ No anomalies detected")

con.close()
