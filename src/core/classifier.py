from enum import Enum
from langchain_qdrant import QdrantVectorStore
from src.db.qdrant_client import get_vector_store


class QueryType(str, Enum):
    NORMAL     = "normal"        # means: NOT RAG / reject
    RAG_NODEJS = "rag_nodejs"
    RAG_BC     = "rag_bc"
    RAG_PMJJBY = "rag_pmjjby"


# -------------------------------
# Configuration
# -------------------------------

RAG_COLLECTION = "combined-ingest"
RAG_SCORE_THRESHOLD = 0.77


# -------------------------------
# RAG Gatekeeper (NO CLASSIFIER)
# -------------------------------

def classify_query(user_query: str, config: dict | None = None) -> QueryType:
    try:
        vs: QdrantVectorStore = get_vector_store(RAG_COLLECTION)

        results = vs.similarity_search_with_relevance_scores(
            query=user_query,
            k=3,
            score_threshold=RAG_SCORE_THRESHOLD,
        )

        if not results:
            return QueryType.NORMAL

        doc, score = results[0]
        source = doc.metadata.get("source", "").lower()

        # ---- Hard domain routing via metadata ----
        if "nodejs" in source:
            return QueryType.RAG_NODEJS

        if "bc" in source or "faq_on_bc" in source or "banking_correspondent" in source:
            return QueryType.RAG_BC

        if "pmjjby" in source:
            return QueryType.RAG_PMJJBY

        # Unknown or noisy document → reject
        return QueryType.NORMAL

    except Exception:
        # Vector DB unavailable → fail closed (NO hallucination)
        return QueryType.NORMAL
