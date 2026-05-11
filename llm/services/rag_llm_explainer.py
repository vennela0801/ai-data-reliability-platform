import os
import duckdb

from groq import Groq
from dotenv import load_dotenv

from rag.vector_store.retrieve_similar_incidents import (
    retrieve_similar_incidents
)

# ---------------------------------------------------------
# Load Environment
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

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ---------------------------------------------------------
# Connect Database
# ---------------------------------------------------------

con = duckdb.connect(DB_PATH)

# ---------------------------------------------------------
# Fetch Latest Incidents
# ---------------------------------------------------------

rows = con.execute("""
SELECT
    check_type,
    metric_name,
    actual_value,
    anomaly_score,
    severity
FROM audit.multi_detector_results
LIMIT 5
""").fetchall()

print(
    f"🧠 Generating RAG explanations "
    f"for {len(rows)} incidents"
)

# ---------------------------------------------------------
# Generate RAG Explanations
# ---------------------------------------------------------

for row in rows:

    check_type = row[0]

    metric_name = row[1]

    actual_value = row[2]

    anomaly_score = row[3]

    severity = row[4]

    # -----------------------------------------------------
    # Retrieve Similar Incidents
    # -----------------------------------------------------

    retrieval_query = f'''
    Incident Type: {check_type}
    Metric: {metric_name}
    Severity: {severity}
    '''

    similar_incidents = retrieve_similar_incidents(
        retrieval_query
    )

    historical_context = ""

    for incident in similar_incidents:

        historical_context += (
            incident["document"]
            + "\n\n"
        )

    # -----------------------------------------------------
    # Build Prompt
    # -----------------------------------------------------

    prompt = f"""
You are a senior AI reliability engineer.

Current Incident:
- Type: {check_type}
- Metric: {metric_name}
- Actual Value: {actual_value}
- Anomaly Score: {anomaly_score}
- Severity: {severity}

Historical Similar Incidents:
{historical_context}

Using the historical incidents above,
generate:
1. probable root cause
2. operational impact
3. recommended investigation steps
4. confidence assessment

Keep explanation concise but intelligent.
"""

    # -----------------------------------------------------
    # Generate LLM Response
    # -----------------------------------------------------

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    explanation = (
        response
        .choices[0]
        .message.content
    )

    print("\n========================")
    print(f"Incident Type: {check_type}")
    print(explanation)

con.close()
