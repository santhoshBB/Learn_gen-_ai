from enum import Enum

class IntentType(str, Enum):
    SMALL_TALK = "small_talk"
    LOGIN = "login"
    FORM_MOBILE = "form_mobile"
    FORM_EMAIL = "form_email"
    ENROLL_PMJJBY = "enroll_pmjjby"
    RAG = "rag"
    REJECTED = "rejected"


def classify_intent(query: str, current_domain: str = None) -> IntentType:
    """Route to appropriate flow"""
    query_lower = query.lower().strip()
    
    # 1. Small talk patterns
    small_talk_patterns = [
        "hi", "hello", "hey", "how are you", "what's up", "good morning",
        "good evening", "thanks", "thank you", "bye", "goodbye",
        "who are you", "what are you", "what can you do"
    ]
    if any(pattern in query_lower for pattern in small_talk_patterns):
        return IntentType.SMALL_TALK
    
    # 2. Login intent
    login_patterns = ["login", "log in", "sign in", "authenticate"]
    if any(pattern in query_lower for pattern in login_patterns):
        return IntentType.LOGIN
    
    # 3. Form intents
    if "change mobile" in query_lower or "update mobile" in query_lower or "mobile number" in query_lower:
        return IntentType.FORM_MOBILE
    
    if "change email" in query_lower or "update email" in query_lower:
        return IntentType.FORM_EMAIL
    
    # 4. Enrollment
    if "enroll" in query_lower and "pmjjby" in query_lower:
        return IntentType.ENROLL_PMJJBY
    
    # 5. Default to RAG
    return IntentType.RAG