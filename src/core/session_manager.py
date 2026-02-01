# ============================================
# FILE 1: src/core/session_manager.py
# Simple session management with conversation memory
# ============================================

from typing import Dict, List, Optional
from datetime import datetime

class ChatSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages: List[dict] = []
        self.user_info: Dict = {}  # Store user name, preferences
        self.is_authenticated = False
        self.created_at = datetime.now()
    
    def add_message(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        # Keep last 10 messages only
        if len(self.messages) > 10:
            self.messages = self.messages[-10:]
    
    def get_history(self) -> List[dict]:
        """Get conversation history for LLM context"""
        return self.messages
    
    def set_user_info(self, key: str, value: str):
        """Remember user details like name"""
        self.user_info[key] = value
    
    def get_user_info(self, key: str) -> Optional[str]:
        """Get remembered user details"""
        return self.user_info.get(key)


# Global session store
_sessions: Dict[str, ChatSession] = {}

def get_session(session_id: str) -> ChatSession:
    """Get or create session"""
    if session_id not in _sessions:
        _sessions[session_id] = ChatSession(session_id)
    return _sessions[session_id]