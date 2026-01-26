from enum import Enum
import re
from src.app import get_llm, load_config
from langchain_qdrant import QdrantVectorStore
# Assuming this function exists in your db.qdrant_client or similar module
from src.db.qdrant_client import get_vector_store

class QueryType(str, Enum):
    NORMAL     = "normal"
    RAG_NODEJS = "rag_nodejs"
    RAG_BC     = "rag_bc"
    RAG_PMJJBY = "rag_pmjjby"


CLASSIFIER_PROMPT = """Classify into ONE only. Reply with exactly the key:

- normal       → casual chat, general questions
- rag_nodejs   → Node.js, async, npm, event loop...
- rag_bc       → Banking Correspondent, BC, CSP
- rag_pmjjby   → PMJJBY, Jeevan Jyoti Bima

Prefer RAG if technical term or scheme appears.
Only return the category name."""


# def classify_query(user_query: str, config: dict | None = None) -> QueryType:
#     """
#     1. Fast keyword rules
#     2. LLM (short prompt)
#     3. If normal → semantic check in combined-ingest
#     """
#     text = user_query.lower().strip()

#     # ── 1. Keyword fast path ───────────────────────────────────────
#     if re.search(r'\b(node\.?js|nodejs|npm|async|await|event ?loop)\b', text):
#         return QueryType.RAG_NODEJS

#     if re.search(r'\b(bc|banking correspondent|csp)\b', text):
#         return QueryType.RAG_BC

#     if re.search(r'\b(pmjjby|jeevan ?jyoti)\b', text):
#         return QueryType.RAG_PMJJBY

#     # ── 2. LLM classification ──────────────────────────────────────
#     if config is None:
#         config = load_config("configs/dev.json")

#     llm = get_llm(config, config["defaults"]["llm"])

#     resp = llm.create(
#         messages=[
#             {"role": "system", "content": CLASSIFIER_PROMPT},
#             {"role": "user", "content": user_query}
#         ],
#         temperature=0.0,
#         max_tokens=10,
#     )

#     label = resp.choices[0].message.content.strip().lower()
#     try:
#         category = QueryType(label)
#     except ValueError:
#         category = QueryType.NORMAL

#     if category != QueryType.NORMAL:
#         return category

#     # ── 3. Semantic rescue only if classified as normal ────────────
#     try:
#         # Use your existing helper function
#         vs: QdrantVectorStore = get_vector_store(collection_name="combined-ingest")

#         results = vs.similarity_search_with_relevance_scores(
#             query=user_query,
#             k=2,
#             score_threshold=0.70,          # ← tune between 0.68–0.78
#         )

#         if not results:
#             return QueryType.NORMAL

#         doc, _score = results[0]
#         source = doc.metadata.get("source", "").lower()

#         if "nodejs" in source:
#             return QueryType.RAG_NODEJS
#         if "bc" in source or "faq_on_bc" in source:
#             return QueryType.RAG_BC
#         if "pmjjby" in source:
#             return QueryType.RAG_PMJJBY

#     except Exception:
#         # If vector store is unreachable → keep LLM decision
#         pass

#     return QueryType.NORMAL

def classify_query(user_query: str, config: dict | None = None) -> QueryType:
    text = user_query.lower().strip()

    has_domain_hint = False

    # Very light keyword check – just existence, not full classification
    if re.search(r'\b(node\.?js|nodejs|callback|async|await|npm|event ?loop|promise)\b', text):
        has_domain_hint = True
    elif re.search(r'\b(bc|banking correspondent|csp|pmjjby|jeevan ?jyoti)\b', text):
        has_domain_hint = True

    if not has_domain_hint:
        # Skip vector search entirely for obvious chit-chat / unrelated
        return QueryType.NORMAL

    # Only now do vector search
    try:
        vs = get_vector_store("combined-ingest")
        results = vs.similarity_search_with_relevance_scores(
            query=user_query,
            k=5,
            score_threshold=0.77,
        )

        if not results:
            return QueryType.NORMAL

        doc, score = results[0]
        source = doc.metadata.get("source", "").lower()

        if "nodejs" in source:
            return QueryType.RAG_NODEJS
        if "bc" in source or "faq_on_bc" in source:
            return QueryType.RAG_BC
        if "pmjjby" in source:
            return QueryType.RAG_PMJJBY

        return QueryType.NORMAL

    except Exception:
        return QueryType.NORMAL