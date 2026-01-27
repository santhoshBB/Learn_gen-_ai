from enum import Enum
from typing import List
import json

class IntentType(str, Enum):
    SMALL_TALK = "small_talk"
    LOGIN = "login"
    FORM_MOBILE = "form_mobile"
    FORM_EMAIL = "form_email"
    ENROLL_PMJJBY = "enroll_pmjjby"
    RAG = "rag"
    REJECTED = "rejected"


def extract_multiple_intents(query: str, llm) -> List[IntentType]:
    """Use LLM to extract all intents"""
    
    prompt = f"""Analyze this query and identify ALL intents present.

Query: "{query}"

Available intents:
- small_talk: greetings (hi, hello, how are you)
- login: wants to login/authenticate
- form_mobile: change/update mobile number
- form_email: change/update email
- enroll_pmjjby: enroll in PMJJBY
- rag: questions about NodeJS, BC, or PMJJBY
- rejected: off-topic

Return ONLY a JSON array: ["intent1", "intent2"]

Response:"""

    response = llm.create(messages=[{"role": "user", "content": prompt}])
    content = response.choices[0].message.content.strip()
    
    try:
        if "```" in content:
            content = content.split("```")[1].replace("json", "").strip()
        intents_list = json.loads(content)
        return [IntentType(intent) for intent in intents_list]
    except Exception as e:
        print(e)
        return [classify_single_intent(query)]


def classify_single_intent(query: str) -> IntentType:
    """Fallback single intent"""
    query_lower = query.lower().strip()
    
    if any(x in query_lower for x in ["hi", "hello", "hey", "how are you", "thanks", "bye"]):
        return IntentType.SMALL_TALK
    if any(x in query_lower for x in ["login", "log in", "sign in"]):
        return IntentType.LOGIN
    if "mobile" in query_lower:
        return IntentType.FORM_MOBILE
    if "email" in query_lower:
        return IntentType.FORM_EMAIL
    if "enroll" in query_lower and "pmjjby" in query_lower:
        return IntentType.ENROLL_PMJJBY
    
    return IntentType.RAG