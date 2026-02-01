# ============================================
# FILE 6: src/core/orchestrator.py
# MAIN BRAIN - Simple orchestration of all intents
# ============================================

from src.core.session_manager import get_session
from src.core.intent_router import detect_intents, Intent
from src.services.conversation_handler import chat_naturally
from src.services.rag_handler import answer_from_docs
from src.services.workflow_handler import handle_login, handle_profile_update, handle_enrollment
from src.app import get_llm


def process_query(query: str, session_id: str, config: dict) -> str:
    """
    MAIN ENTRY POINT
    
    Simple flow:
    1. Get session (with memory)
    2. Detect what user wants
    3. Handle each intent
    4. Save conversation
    5. Return response
    """
    
    # 1. Get session with memory
    session = get_session(session_id)
    llm = get_llm(config, config["defaults"]["llm"])
    
    # 2. Detect intents
    intents = detect_intents(query, llm)
    
    # 3. Handle each intent sequentially
    responses = []
    
    for intent in intents:
        
        if intent == Intent.CHAT:
            # Natural conversation with memory
            response = chat_naturally(query, session, llm)
            responses.append(response)
        
        elif intent == Intent.RAG_QUERY:
            # Search docs and answer
            response = answer_from_docs(query, session.get_history(), llm, config)
            responses.append(response)
        
        elif intent == Intent.LOGIN:
            response = handle_login(session)
            responses.append(response)
            if not session.is_authenticated:
                break  # Stop if login failed
        
        elif intent == Intent.UPDATE_PROFILE:
            # Detect mobile or email
            if "mobile" in query.lower():
                response = handle_profile_update(session, "mobile")
            else:
                response = handle_profile_update(session, "email")
            responses.append(response)
            if not session.is_authenticated:
                break  # Stop if not authenticated
        
        elif intent == Intent.ENROLL:
            response = handle_enrollment(session)
            responses.append(response)
            if not session.is_authenticated:
                break
        
        elif intent == Intent.OFF_TOPIC:
            responses.append("I specialize in NodeJS, Banking Correspondent, and PMJJBY. Could you ask something related to these topics? 😊")
    
    # 4. Combine responses
    final_response = "\n\n".join(responses)
    
    # 5. Save to conversation history
    session.add_message("user", query)
    session.add_message("assistant", final_response)
    
    return final_response