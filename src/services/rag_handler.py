# ============================================
# FILE 3: src/services/rag_handler.py
# Simple RAG - no complex domain tracking
# ============================================

from langchain_qdrant import QdrantVectorStore
from src.db.qdrant_client import get_vector_store

def answer_from_docs(query: str, conversation_history: list, llm, config: dict) -> str:
    """
    Simple RAG: Search docs + Answer with LLM
    """
    
    # 1. Search vector DB
    vs: QdrantVectorStore = get_vector_store("combined-ingest")
    
    results = vs.similarity_search_with_relevance_scores(
        query=query,
        k=5,
        score_threshold=0.75
    )
    
    # 2. Check if relevant docs found
    if not results or results[0][1] < 0.75:
        return "I specialize in NodeJS, Banking Correspondent, and PMJJBY. I couldn't find relevant information for your question in my knowledge base."
    
    # 3. Format context
    context = "\n\n".join([
        f"[Page {doc.metadata.get('page', '?')}]\n{doc.page_content}"
        for doc, score in results
    ])
    
    # 4. Build prompt
    system_prompt = f"""You are a helpful assistant specialized in NodeJS, Banking Correspondent (BC), and PMJJBY.

Answer ONLY using the provided documentation. Include page numbers like [Page X] for citations.

If the answer is not in the documentation, say: "I don't have that information in my current knowledge base."

Documentation:
{context}"""
    
    # 5. Add conversation history for context
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history[-6:])  # Last 6 messages
    messages.append({"role": "user", "content": query})
    
    # 6. Get answer
    response = llm.create(messages=messages)
    return response.choices[0].message.content