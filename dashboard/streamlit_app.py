import os
import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px

# ---------------------------------------------------
# Streamlit Page Config
# ---------------------------------------------------

st.set_page_config(
    page_title="AI Data Reliability Platform",
    layout="wide"
)

st.title("🚀 AI Data Reliability Platform")

st.markdown("""
Real-time anomaly intelligence dashboard powered by:
- DuckDB
- Streamlit
- ML anomaly detection
- RAG incident intelligence
""")

# ---------------------------------------------------
# Database Configuration
# ---------------------------------------------------

DB_PATH = "warehouse.duckdb"

# ---------------------------------------------------
# Create Lightweight Demo DB if Missing
# ---------------------------------------------------

if not os.path.exists(DB_PATH):

    con = duckdb.connect(DB_PATH)

    con.execute("""
    CREATE TABLE anomalies (
        id INTEGER,
        metric_name VARCHAR,
        anomaly_score DOUBLE,
        severity VARCHAR
    )
    """)

    con.execute("""
    INSERT INTO anomalies VALUES
    (1, 'revenue_spike', 0.98, 'HIGH'),
    (2, 'null_payment_rate', 0.87, 'MEDIUM'),
    (3, 'duplicate_transactions', 0.91, 'HIGH')
    """)

    con.close()

# ---------------------------------------------------
# Connect Database
# ---------------------------------------------------

con = duckdb.connect(DB_PATH)

# ---------------------------------------------------
# Load Anomaly Data
# ---------------------------------------------------

df = con.execute("""
SELECT * FROM anomalies
""").df()

# ---------------------------------------------------
# KPI Metrics
# ---------------------------------------------------

total_anomalies = len(df)

high_severity = len(
    df[df["severity"] == "HIGH"]
)

avg_score = round(
    df["anomaly_score"].mean(),
    2
)

# ---------------------------------------------------
# KPI Cards
# ---------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Anomalies",
        total_anomalies
    )

with col2:
    st.metric(
        "High Severity",
        high_severity
    )

with col3:
    st.metric(
        "Average Score",
        avg_score
    )

# ---------------------------------------------------
# Anomaly Table
# ---------------------------------------------------

st.subheader("📊 Detected Anomalies")

st.dataframe(
    df,
    use_container_width=True
)

# ---------------------------------------------------
# Severity Distribution Chart
# ---------------------------------------------------

st.subheader("📈 Severity Distribution")

severity_counts = (
    df["severity"]
    .value_counts()
    .reset_index()
)

severity_counts.columns = [
    "severity",
    "count"
]

fig = px.bar(
    severity_counts,
    x="severity",
    y="count",
    title="Anomaly Severity Distribution"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ---------------------------------------------------
# Anomaly Scores
# ---------------------------------------------------

st.subheader("🧠 Anomaly Scores")

fig2 = px.scatter(
    df,
    x="metric_name",
    y="anomaly_score",
    color="severity",
    size="anomaly_score",
    title="Anomaly Score Analysis"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# ---------------------------------------------------
# Footer
# ---------------------------------------------------

st.markdown("---")

st.markdown("""
✅ Production-style AI reliability observability platform  
✅ Multi-detector anomaly intelligence  
✅ RAG-enhanced incident analysis  
✅ Streamlit cloud deployment
""")

con.close()
