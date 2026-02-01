# ============================================
# FILE 2: src/core/intent_router.py
# Simple intent detection and routing
# ============================================

from enum import Enum
from typing import List
import json

class Intent(str, Enum):
    CHAT = "chat"              # Casual conversation, greetings
    RAG_QUERY = "rag_query"    # Questions about NodeJS/BC/PMJJBY
    LOGIN = "login"
    UPDATE_PROFILE = "update_profile"
    ENROLL = "enroll"
    OFF_TOPIC = "off_topic"


def detect_intents(query: str, llm) -> List[Intent]:
    """
    Simple LLM-based intent detection
    Returns list of intents in order
    """
    
    system_prompt = """You are an intent classifier. Analyze the user query and identify intents.

Intents:
- chat: Greetings, personal conversation (hi, how are you, my name is, remember me)
- rag_query: Questions about NodeJS, Banking Correspondent, or PMJJBY
- login: User wants to login
- update_profile: Change mobile/email
- enroll: Enroll in PMJJBY
- off_topic: Unrelated topics

Return JSON array of intents in order: ["intent1", "intent2"]
Example: ["chat", "rag_query", "login"]"""

    user_prompt = f'Query: "{query}"\n\nIntents:'
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    response = llm.create(messages=messages)
    content = response.choices[0].message.content.strip()
    
    try:
        # Parse JSON
        if "```" in content:
            content = content.split("```")[1].replace("json", "").strip()
        intents_list = json.loads(content)
        return [Intent(i) for i in intents_list]
    except:
        # Fallback
        return [Intent.CHAT]