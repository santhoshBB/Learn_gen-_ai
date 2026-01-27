from typing import Optional
from langchain_qdrant import QdrantVectorStore
# from qdrant_client.models import Filter, FieldCondition, MatchValue
from src.db.qdrant_client import get_vector_store


def retrieve_context(
    query: str, 
    collection: str,
    domain_filter: Optional[str] = None,
    k: int = 5
) -> str:
    """
    Retrieve relevant context from vector store with optional domain filtering
    
    Args:
        query: User's question
        collection: Vector store collection name
        domain_filter: Optional domain to filter by (e.g., "rag_nodejs")
        k: Number of documents to retrieve
    
    Returns:
        Formatted context string with page numbers
    """
    try:
        vs: QdrantVectorStore = get_vector_store(collection)
        
        # Build filter if domain is specified
        search_kwargs = {"k": k}
        
        if domain_filter:
            # Create a filter to only get documents from the specified domain
            # This assumes your documents have a 'source' or 'domain' metadata field
            domain_mapping = {
                "rag_nodejs": "nodejs",
                "rag_bc": "bc",
                "rag_pmjjby": "pmjjby"
            }
            
            filter_value = domain_mapping.get(domain_filter, domain_filter)
            
            # Option 1: Filter by source field (adjust based on your metadata structure)
            search_kwargs["filter"] = {
                "source": {"$regex": filter_value}
            }
        
        # Retrieve documents
        results = vs.similarity_search(
            query=query,
            **search_kwargs
        )
        
        if not results:
            return "No relevant documentation found."
        
        # Format context with page numbers
        context_parts = []
        for i, doc in enumerate(results, 1):
            page_num = doc.metadata.get("page", "Unknown")
            source = doc.metadata.get("source", "Unknown")
            content = doc.page_content
            
            context_parts.append(
                f"[Document {i} - Page {page_num} - Source: {source}]\n{content}"
            )
        
        return "\n\n".join(context_parts)
    
    except Exception as e:
        return f"Error retrieving context: {str(e)}"


def retrieve_context_with_scores(
    query: str,
    collection: str,
    domain_filter: Optional[str] = None,
    k: int = 5,
    score_threshold: float = 0.7
):
    """
    Retrieve context with relevance scores
    Useful for debugging and confidence assessment
    """
    try:
        vs: QdrantVectorStore = get_vector_store(collection)
        
        search_kwargs = {"k": k, "score_threshold": score_threshold}
        
        if domain_filter:
            domain_mapping = {
                "rag_nodejs": "nodejs",
                "rag_bc": "bc",
                "rag_pmjjby": "pmjjby"
            }
            filter_value = domain_mapping.get(domain_filter, domain_filter)
            search_kwargs["filter"] = {
                "source": {"$regex": filter_value}
            }
        
        results = vs.similarity_search_with_relevance_scores(
            query=query,
            **search_kwargs
        )
        
        return results
    
    except Exception as e:
        print(e)
        return []