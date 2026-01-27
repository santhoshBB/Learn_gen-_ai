from src.rag.retriever import retrieve_context
from src.rag.prompts import build_rag_prompt
from src.app import get_llm
from src.core.chat_memory import (
    add_message, 
    get_session_history, 
    set_current_domain,
    # get_current_domain
)
from src.core.classifier import QueryType


def rag_chat(
    prompt: str, 
    collection: str, 
    session_id: str, 
    query_type: QueryType,
    config: dict
):
    """
    RAG-based chat with domain context tracking
    """
    # Store user message
    add_message(session_id, "user", prompt)
    
    # Update current domain context
    set_current_domain(session_id, query_type.value)
    
    # Retrieve context from the appropriate domain
    # The retriever can optionally filter by domain metadata
    context = retrieve_context(
        prompt, 
        collection,
        domain_filter=query_type.value  # Pass domain for filtering
    )
    
    # Build system prompt with domain-specific instructions
    system_prompt = build_rag_prompt(context, query_type)
    
    # Build messages with context
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(get_session_history(session_id))
    
    # Get LLM response
    llm = get_llm(config, config["defaults"]["llm"])
    response = llm.create(messages=messages)
    
    answer = response.choices[0].message.content
    
    # Store assistant response
    add_message(session_id, "assistant", answer)
    
    return answer