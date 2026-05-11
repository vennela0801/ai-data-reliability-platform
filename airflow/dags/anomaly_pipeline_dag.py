from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    "owner": "vennela",
    "retries": 1,
}

with DAG(
    dag_id="retail_anomaly_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["anomaly", "llm"],
) as dag:

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="""
cd /home/vennela/anomaly_demo/dbt_project
source /home/vennela/anomaly_demo/.venv/bin/activate
dbt run
"""
    )

    detect_anomalies = BashOperator(
        task_id="detect_anomalies",
        bash_command="""
cd /home/vennela/anomaly_demo
source /home/vennela/anomaly_demo/.venv/bin/activate
python plugins/anomaly_detection/detector.py
"""
    )

    generate_llm_reports = BashOperator(
        task_id="generate_llm_reports",
        bash_command="""
cd /home/vennela/anomaly_demo
source /home/vennela/anomaly_demo/.venv/bin/activate
python plugins/anomaly_detection/llm_explainer.py
"""
    )

    incident_summary = BashOperator(
        task_id="incident_summary",
        bash_command="echo 'Pipeline completed successfully'"
    )

    dbt_run >> detect_anomalies >> generate_llm_reports >> incident_summary
