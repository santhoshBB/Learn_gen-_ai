from src.db.qdrant_client import get_vector_store


def retrieve_context(
    query: str,
    collection_name: str,
    k: int = 5
) -> str:
    vector_store = get_vector_store(collection_name=collection_name)
    docs = vector_store.similarity_search(query=query, k=k)

    if not docs:
        return ""

    return "\n\n".join(
        f"[Page {doc.metadata.get('page', 'N/A')}] {doc.page_content}"
        for doc in docs
    )
