from src.core.classifier import QueryType
# from src.services.normal_chat import normal_chat
from src.services.rag_chat import rag_chat
from src.services.rejection_handler import handle_rejection
from src.core.intent_classifier import classify_intent, IntentType
from src.services.small_talk_handler import handle_small_talk
from src.services.langgraph_workflows import run_login_flow, run_form_flow

def route_query(prompt: str, query_type: QueryType, session_id: str, config: dict):
    """
    Route queries with proper rejection handling
    """
    match query_type:
        case QueryType.REJECTED:
            # User asked something off-topic - politely decline
            return handle_rejection(prompt, session_id, config)

        case QueryType.RAG_PMJJBY | QueryType.RAG_NODEJS | QueryType.RAG_BC:
            # Valid domain query - use RAG
            return rag_chat(prompt, "combined-ingest", session_id, query_type, config)

        case _:
            # Fallback - should not reach here
            return "Unable to classify the query. Please ask about NodeJS, Banking Correspondent, or PMJJBY."
        
# ===== ADD TO: src/core/router.py =====



def master_route_query(prompt: str, session_id: str, config: dict):
    """Master router with intent classification"""
    
    # Step 1: Classify intent
    intent = classify_intent(prompt)
    
    # Step 2: Route based on intent
    if intent == IntentType.SMALL_TALK:
        return handle_small_talk(prompt, session_id)
    
    elif intent == IntentType.LOGIN:
        result = run_login_flow(session_id)
        if result["is_authenticated"]:
            return "Login successful! How can I help you?"
        else:
            return "Please provide your credentials to login."
    
    elif intent == IntentType.FORM_MOBILE:
        result = run_form_flow(session_id, "mobile")
        return "Mobile number change initiated. Please follow the steps."
    
    elif intent == IntentType.FORM_EMAIL:
        result = run_form_flow(session_id, "email")
        return "Email change initiated. Please follow the steps."
    
    elif intent == IntentType.ENROLL_PMJJBY:
        # TODO: Add enrollment workflow
        return "PMJJBY enrollment coming soon!"
    
    elif intent == IntentType.RAG:
        # Existing RAG flow
        from src.core.chat_memory import get_current_domain
        from src.core.classifier import classify_query, QueryType
        
        current_domain = get_current_domain(session_id)
        current_domain_enum = QueryType(current_domain) if current_domain else None
        
        query_type = classify_query(prompt, config, current_domain=current_domain_enum)
        return route_query(prompt, query_type, session_id, config)
    
    else:  # REJECTED
        return route_query(prompt, QueryType.REJECTED, session_id, config)