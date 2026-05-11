import os
import duckdb
import pickle
import faiss

from sentence_transformers import (
    SentenceTransformer
)

# ---------------------------------------------------------
# Database Connection
# ---------------------------------------------------------

DB_PATH = (
    "/home/vennela/ai-data-reliability-platform/"
    "warehouse/database/warehouse.duckdb"
)

con = duckdb.connect(DB_PATH)

# ---------------------------------------------------------
# Load Historical Incidents
# ---------------------------------------------------------

rows = con.execute("""
SELECT
    id,
    check_type,
    severity,
    llm_explanation
FROM audit.anomaly_results
WHERE llm_explanation IS NOT NULL
""").fetchall()

documents = []

metadata = []

for row in rows:

    text = f'''
Incident Type: {row[1]}
Severity: {row[2]}

Explanation:
{row[3]}
'''

    documents.append(text)

    metadata.append({
        "id": row[0],
        "check_type": row[1],
        "severity": row[2]
    })

# ---------------------------------------------------------
# Generate Embeddings
# ---------------------------------------------------------

print("🔍 Loading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("🧠 Generating embeddings...")

embeddings = model.encode(documents)

# ---------------------------------------------------------
# Build FAISS Index
# ---------------------------------------------------------

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

# ---------------------------------------------------------
# Persist Vector Store
# ---------------------------------------------------------

faiss.write_index(
    index,
    "rag/vector_store/index/incidents.index"
)

with open(
    "rag/vector_store/index/metadata.pkl",
    "wb"
) as f:

    pickle.dump(
        {
            "documents": documents,
            "metadata": metadata
        },
        f
    )

print(
    f"✅ Indexed {len(documents)} incidents"
)

con.close()
