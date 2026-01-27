"""
Handle rejected queries - questions outside our specialized domains
"""


def handle_rejection(prompt: str, session_id: str, config: dict) -> str:
    """
    Politely decline off-topic queries and guide user to valid topics
    """
    
    rejection_message = """I apologize, but I'm a specialized assistant focused on three specific topics:

1. **NodeJS** - JavaScript runtime, npm, modules, async programming
2. **Business Correspondent (BC)** - Business agents, financial inclusion
3. **PMJJBY** - Pradhan Mantri Jeevan Jyoti Bima Yojana (life insurance scheme)

Your question appears to be outside these areas. Could you please ask me something related to NodeJS, Business Correspondent, or PMJJBY?

Examples:
- "What is NodeJS event loop?"
- "What are the eligibility criteria for becoming a Business Correspondent?"
- "What is the premium amount for PMJJBY?"
"""
    
    return rejection_message.strip()