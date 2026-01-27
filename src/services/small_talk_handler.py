def handle_small_talk(query: str, session_id: str) -> str:
    """Handle casual conversation"""
    query_lower = query.lower().strip()
    
    greetings = ["hi", "hello", "hey"]
    if any(g in query_lower for g in greetings):
        return "Hello! I'm your assistant for NodeJS, Banking Correspondent, and PMJJBY queries. How can I help you today?"
    
    if "how are you" in query_lower:
        return "I'm doing well, thank you! How can I assist you with NodeJS, BC, or PMJJBY?"
    
    if "who are you" in query_lower or "what are you" in query_lower:
        return "I'm a specialized AI assistant for NodeJS, Banking Correspondent (BC), and PMJJBY documentation."
    
    if "what can you do" in query_lower:
        return """I can help you with:
1. NodeJS - JavaScript runtime, npm, async programming
2. Banking Correspondent - BC operations, eligibility
3. PMJJBY - Life insurance scheme details

I can also help you login or update your profile (mobile/email)."""
    
    if "thank" in query_lower:
        return "You're welcome! Let me know if you need anything else."
    
    if "bye" in query_lower or "goodbye" in query_lower:
        return "Goodbye! Feel free to come back anytime."
    
    return "I'm here to help! Ask me about NodeJS, BC, or PMJJBY."