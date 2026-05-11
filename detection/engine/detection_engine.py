import os
import duckdb
import pandas as pd
from dotenv import load_dotenv

from detection.engine.detector_registry import DETECTORS

from alerts.slack.slack_alert_service import (
    send_slack_alert
)

# ---------------------------------------------------------
# Load Environment Variables
# ---------------------------------------------------------

load_dotenv(
    os.path.expanduser(
        "~/ai-data-reliability-platform/.env"
    )
)

DB_PATH = (
    "/home/vennela/ai-data-reliability-platform/"
    "warehouse/database/warehouse.duckdb"
)

# ---------------------------------------------------------
# Connect DuckDB
# ---------------------------------------------------------

con = duckdb.connect(DB_PATH)

# ---------------------------------------------------------
# Detection Checks
# ---------------------------------------------------------

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
        "type": "order_drop"
    }
]

# ---------------------------------------------------------
# Severity Classification
# ---------------------------------------------------------

def classify_severity(score):

    score = abs(float(score))

    if score >= 5:
        return "critical"

    elif score >= 4:
        return "high"

    elif score >= 3:
        return "medium"

    return "low"

# ---------------------------------------------------------
# Execute Detection
# ---------------------------------------------------------

all_results = []

for check in CHECKS:

    query = f'''
    SELECT
        {check["date_col"]} AS metric_date,
        {check["metric"]} AS metric_value
    FROM {check["table"]}
    ORDER BY 1
    '''

    df = con.execute(query).df()

    print(
        f"\\n🔍 Running checks for "
        f"{check['metric']}"
    )

    for detector_name, detector in DETECTORS.items():

        try:

            anomalies = detector.detect(
                df.copy(),
                "metric_value"
            )

            print(
                f"   {detector_name:<20}"
                f"{len(anomalies)} anomalies"
            )

            for _, row in anomalies.iterrows():

                anomaly_score = float(
                    row["anomaly_score"]
                )

                severity = classify_severity(
                    anomaly_score
                )

                result = {
                    "table_name": check["table"],
                    "check_type": check["type"],
                    "detector_name": detector_name,
                    "anomaly_date": row["metric_date"],
                    "metric_name": check["metric"],
                    "actual_value": float(
                        row["metric_value"]
                    ),
                    "anomaly_score": anomaly_score,
                    "severity": severity
                }

                all_results.append(result)

                # -------------------------------------------------
                # Slack Alert Trigger
                # -------------------------------------------------

                if severity in [
                    "critical",
                    "high"
                ]:

                    send_slack_alert(
                        severity=severity,
                        detector=detector_name,
                        metric=check["metric"],
                        score=anomaly_score,
                        explanation=(
                            f"Anomaly detected in "
                            f"{check['metric']} "
                            f"using {detector_name}"
                        )
                    )

        except Exception as e:

            print(
                f"❌ {detector_name} failed: {e}"
            )

# ---------------------------------------------------------
# Persist Results
# ---------------------------------------------------------

results_df = pd.DataFrame(all_results)

if len(results_df) > 0:

    con.execute("""
    CREATE TABLE IF NOT EXISTS audit.multi_detector_results (
        table_name VARCHAR,
        check_type VARCHAR,
        detector_name VARCHAR,
        anomaly_date DATE,
        metric_name VARCHAR,
        actual_value DOUBLE,
        anomaly_score DOUBLE,
        severity VARCHAR
    )
    """)

    con.register(
        "results_df",
        results_df
    )

    con.execute("""
    INSERT INTO audit.multi_detector_results
    SELECT * FROM results_df
    """)

    print(
        f"\\n✅ Stored {len(results_df)} "
        f"multi-detector anomalies"
    )

else:

    print("\\nNo anomalies found")

con.close()
