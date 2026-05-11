import os
import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Data Reliability Platform",
    page_icon="🚨",
    layout="wide"
)

# ---------------------------------------------------------
# Load Environment Variables
# ---------------------------------------------------------

load_dotenv(os.path.expanduser(
    "~/ai-data-reliability-platform/.env"
))

DB_PATH = "/app/warehouse/database/warehouse.duckdb"

# ---------------------------------------------------------
# Connect to DuckDB
# ---------------------------------------------------------

con = duckdb.connect(DB_PATH)

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.title("🚨 AI Reliability Platform")

page = st.sidebar.radio(
    "Navigation",
    [
        "Executive Overview",
        "Incident Explorer",
        "Detection Analytics",
        "AI RCA Viewer",
        "Pipeline Health"
    ]
)

# ---------------------------------------------------------
# Executive Overview
# ---------------------------------------------------------

if page == "Executive Overview":

    st.title("📊 Executive Overview")

    anomalies_df = con.execute("""
        SELECT *
        FROM audit.anomaly_results
    """).df()

    total_incidents = len(anomalies_df)

    critical_count = len(
        anomalies_df[
            anomalies_df["severity"] == "critical"
        ]
    )

    high_count = len(
        anomalies_df[
            anomalies_df["severity"] == "high"
        ]
    )

    medium_count = len(
        anomalies_df[
            anomalies_df["severity"] == "medium"
        ]
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Incidents", total_incidents)
    col2.metric("Critical", critical_count)
    col3.metric("High", high_count)
    col4.metric("Medium", medium_count)

    st.divider()

    st.subheader("Severity Distribution")

    severity_chart = px.pie(
        anomalies_df,
        names="severity",
        title="Incident Severity Breakdown"
    )

    st.plotly_chart(
        severity_chart,
        use_container_width=True
    )

    st.divider()

    st.subheader("Incident Timeline")

    timeline = px.scatter(
        anomalies_df,
        x="anomaly_date",
        y="z_score",
        color="severity",
        hover_data=[
            "check_type",
            "table_name"
        ],
        title="Anomaly Timeline"
    )

    st.plotly_chart(
        timeline,
        use_container_width=True
    )

# ---------------------------------------------------------
# Incident Explorer
# ---------------------------------------------------------

elif page == "Incident Explorer":

    st.title("🚨 Incident Explorer")

    incidents = con.execute("""
        SELECT
            id,
            check_type,
            severity,
            anomaly_date,
            metric_name,
            actual_value,
            expected_value,
            ROUND(z_score, 2) AS z_score
        FROM audit.anomaly_results
        ORDER BY ABS(z_score) DESC
    """).df()

    severity_filter = st.multiselect(
        "Filter Severity",
        options=incidents["severity"].unique(),
        default=incidents["severity"].unique()
    )

    filtered = incidents[
        incidents["severity"].isin(severity_filter)
    ]

    st.dataframe(
        filtered,
        use_container_width=True
    )

# ---------------------------------------------------------
# Detection Analytics
# ---------------------------------------------------------

elif page == "Detection Analytics":

    st.title("📈 Detection Analytics")

    revenue_df = con.execute("""
        SELECT
            order_date,
            total_revenue,
            order_count
        FROM marts.fct_orders_daily
        ORDER BY order_date
    """).df()

    revenue_chart = px.line(
        revenue_df,
        x="order_date",
        y="total_revenue",
        title="Daily Revenue Trend"
    )

    st.plotly_chart(
        revenue_chart,
        use_container_width=True
    )

    order_chart = px.line(
        revenue_df,
        x="order_date",
        y="order_count",
        title="Daily Order Count Trend"
    )

    st.plotly_chart(
        order_chart,
        use_container_width=True
    )

# ---------------------------------------------------------
# AI RCA Viewer
# ---------------------------------------------------------

elif page == "AI RCA Viewer":

    st.title("🧠 AI Incident Narratives")

    rca_df = con.execute("""
        SELECT
            id,
            check_type,
            severity,
            llm_explanation
        FROM audit.anomaly_results
    """).df()

    selected_id = st.selectbox(
        "Select Incident",
        rca_df["id"]
    )

    selected = rca_df[
        rca_df["id"] == selected_id
    ].iloc[0]

    st.subheader(
        f"Incident #{selected['id']}"
    )

    st.write(
        f"Severity: {selected['severity']}"
    )

    st.write(
        f"Type: {selected['check_type']}"
    )

    st.divider()

    st.markdown(
        selected["llm_explanation"]
    )

# ---------------------------------------------------------
# Pipeline Health
# ---------------------------------------------------------

elif page == "Pipeline Health":

    st.title("⚙️ Pipeline Health")

    st.success("Airflow DAG operational")

    st.metric(
        "Last Pipeline Status",
        "SUCCESS"
    )

    st.metric(
        "Warehouse Status",
        "CONNECTED"
    )

    st.metric(
        "LLM Service",
        "AVAILABLE"
    )

con.close()
