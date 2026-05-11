import os
import duckdb
from dotenv import load_dotenv
from groq import Groq

load_dotenv(os.path.expanduser("~/anomaly_demo/.env"))

DB_PATH = os.getenv("DUCKDB_PATH")

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL = "llama-3.3-70b-versatile"

con = duckdb.connect(DB_PATH)

# ───────────────────────────────────────────────────────────────
# Fetch unexplained anomalies
# ───────────────────────────────────────────────────────────────

rows = con.execute("""
    SELECT
        id,
        table_name,
        check_type,
        anomaly_date,
        metric_name,
        actual_value,
        expected_value,
        z_score,
        severity
    FROM audit.anomaly_results
    WHERE llm_explanation IS NULL
    ORDER BY ABS(z_score) DESC
""").fetchall()

print(f"\n🧠 Generating explanations for {len(rows)} anomalies\n")

# ───────────────────────────────────────────────────────────────
# Generate narratives
# ───────────────────────────────────────────────────────────────

for row in rows:

    (
        anomaly_id,
        table_name,
        check_type,
        anomaly_date,
        metric_name,
        actual_value,
        expected_value,
        z_score,
        severity
    ) = row

    prompt = f"""
You are a senior data platform reliability engineer.

Analyze the anomaly below.

Provide:
1. Executive summary
2. Likely root causes
3. Business impact
4. Recommended next investigation steps

Be realistic and concise.

Anomaly Details:
- Table: {table_name}
- Check Type: {check_type}
- Date: {anomaly_date}
- Metric: {metric_name}
- Actual Value: {actual_value}
- Expected Value: {expected_value}
- Z-Score: {z_score:.2f}
- Severity: {severity}
"""

    print(f"🔍 Explaining anomaly #{anomaly_id} ({check_type})")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an expert incident investigation AI."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=500
    )

    explanation = response.choices[0].message.content

    con.execute("""
        UPDATE audit.anomaly_results
        SET llm_explanation = ?
        WHERE id = ?
    """, [explanation, anomaly_id])

    print("   ✅ explanation saved")

print("\n🎉 All anomaly narratives generated")

con.close()
