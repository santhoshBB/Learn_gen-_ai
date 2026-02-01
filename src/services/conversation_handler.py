# ============================================
# FILE 4: src/services/conversation_handler.py
# Natural conversation with memory
# ============================================

import re

def chat_naturally(query: str, session, llm) -> str:
    """
    Handle casual conversation with personality and memory
    Extracts and remembers user info like name
    """
    
    # Extract name if user introduces themselves
    name_patterns = [
        r"my name is (\w+)",
        r"i'm (\w+)",
        r"i am (\w+)",
        r"this is (\w+)",
        r"call me (\w+)"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, query.lower())
        if match:
            name = match.group(1).capitalize()
            session.set_user_info("name", name)
            return f"Nice to meet you, {name}! 😊 I'm here to help with NodeJS, Banking Correspondent, and PMJJBY queries. How can I assist you today?"
    
    # Check if user asks about their name
    if "my name" in query.lower() or "who am i" in query.lower():
        name = session.get_user_info("name")
        if name:
            return f"You told me your name is {name}! 😊"
        else:
            return "I don't think you've told me your name yet. What's your name?"
    
    # Build conversation prompt with history
    system_prompt = """You are a friendly AI assistant specialized in NodeJS, Banking Correspondent (BC), and PMJJBY.

Personality:
- Warm and conversational
- Remember details from conversation
- Use emojis occasionally 😊
- Be helpful and concise

Your main expertise:
1. NodeJS - JavaScript runtime, npm, async programming
2. Banking Correspondent - BC operations, agents
3. PMJJBY - Life insurance scheme

If asked about other topics, politely redirect to your expertise areas."""
    
    # Get recent conversation history
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(session.get_history()[-6:])
    messages.append({"role": "user", "content": query})
    
    # Generate response
    response = llm.create(messages=messages)
    return response.choices[0].message.content