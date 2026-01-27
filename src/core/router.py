from src.core.classifier import QueryType
# from src.services.normal_chat import normal_chat
from src.services.rag_chat import rag_chat
from src.services.rejection_handler import handle_rejection
from src.core.intent_classifier import IntentType
from src.services.small_talk_handler import handle_small_talk
from src.services.langgraph_workflows import run_login_flow, run_form_flow
from src.core.intent_classifier import extract_multiple_intents
from src.app import get_llm

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
            return "Unable to classify the query. Please ask about NodeJS, Business Correspondent, or PMJJBY."
        
# ===== ADD TO: src/core/router.py ====

def master_route_query(prompt: str, session_id: str, config: dict):
    """Master router with multi-intent sequential execution"""
    
    # Step 1: Extract ALL intents
    llm = get_llm(config, config["defaults"]["llm"])
    intents = extract_multiple_intents(prompt, llm)
    
    # Step 2: Execute intents sequentially
    responses = []
    auth_required = False
    
    for intent in intents:
        
        # SMALL TALK
        if intent == IntentType.SMALL_TALK:
            responses.append(handle_small_talk(prompt, session_id))
        
        # RAG - Answer questions
        elif intent == IntentType.RAG:
            from src.core.chat_memory import get_current_domain
            from src.core.classifier import classify_query, QueryType
            
            current_domain = get_current_domain(session_id)
            current_domain_enum = QueryType(current_domain) if current_domain else None
            
            query_type = classify_query(prompt, config, current_domain=current_domain_enum)
            rag_response = route_query(prompt, query_type, session_id, config)
            responses.append(rag_response)
        
        # LOGIN - Check auth
        elif intent == IntentType.LOGIN:
            result = run_login_flow(session_id)
            if result["is_authenticated"]:
                responses.append("✓ Login successful!")
            else:
                responses.append("Please provide your credentials to login.")
                auth_required = True
                break  # Stop here, need auth first
        
        # FORM CHANGES - Require auth
        elif intent in [IntentType.FORM_MOBILE, IntentType.FORM_EMAIL]:
            # Check if user is authenticated
            from src.services.langgraph_workflows import is_user_authenticated
            
            if not is_user_authenticated(session_id):
                responses.append("⚠ To update your profile, please login first.")
                auth_required = True
                break  # Stop, need login
            
            # User is authenticated, proceed
            form_type = "mobile" if intent == IntentType.FORM_MOBILE else "email"
            result = run_form_flow(session_id, form_type)
            responses.append(f"✓ {form_type.title()} change initiated. Please follow the steps.")
        
        # ENROLLMENT - Require auth
        elif intent == IntentType.ENROLL_PMJJBY:
            from src.services.langgraph_workflows import is_user_authenticated
            
            if not is_user_authenticated(session_id):
                responses.append("⚠ To enroll in PMJJBY, please login first.")
                auth_required = True
                break
            
            responses.append("✓ PMJJBY enrollment initiated.")
        
        # REJECTED
        elif intent == IntentType.REJECTED:
            responses.append(route_query(prompt, QueryType.REJECTED, session_id, config))
    
    # Step 3: Combine responses
    final_response = "\n\n".join(responses)
    
    # Add follow-up prompt if auth required
    if auth_required:
        final_response += "\n\nWould you like to login now? (Type 'login' to proceed)"
    
    return final_response
