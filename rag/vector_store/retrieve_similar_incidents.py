import pickle
import faiss

from sentence_transformers import (
    SentenceTransformer
)

# ---------------------------------------------------------
# Load Embedding Model
# ---------------------------------------------------------

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# ---------------------------------------------------------
# Load Vector Store
# ---------------------------------------------------------

index = faiss.read_index(
    "rag/vector_store/index/incidents.index"
)

with open(
    "rag/vector_store/index/metadata.pkl",
    "rb"
) as f:

    store = pickle.load(f)

documents = store["documents"]

metadata = store["metadata"]

# ---------------------------------------------------------
# Similarity Retrieval
# ---------------------------------------------------------

def retrieve_similar_incidents(
    query,
    top_k=2
):

    query_embedding = model.encode(
        [query]
    )

    distances, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for idx in indices[0]:

        results.append({
            "document": documents[idx],
            "metadata": metadata[idx]
        })

    return results
