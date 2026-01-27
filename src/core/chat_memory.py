from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


MAX_TURNS = 6  # last 3 user+assistant turns


@dataclass
class SessionContext:
    """Track conversation context per session"""
    messages: List[dict]
    current_domain: Optional[str] = None  # Track active domain
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()


CHAT_SESSIONS: Dict[str, SessionContext] = {}


def get_session_context(session_id: str) -> SessionContext:
    """Get or create session context"""
    if session_id not in CHAT_SESSIONS:
        CHAT_SESSIONS[session_id] = SessionContext(messages=[])
    return CHAT_SESSIONS[session_id]


def get_session_history(session_id: str) -> List[dict]:
    """Get message history (backward compatible)"""
    context = get_session_context(session_id)
    return context.messages


def get_current_domain(session_id: str) -> Optional[str]:
    """Get the current active domain for this session"""
    context = get_session_context(session_id)
    return context.current_domain


def set_current_domain(session_id: str, domain: str):
    """Set the active domain for this session"""
    context = get_session_context(session_id)
    context.current_domain = domain
    context.last_updated = datetime.now()


def add_message(session_id: str, role: str, content: str):
    """Add message to history"""
    context = get_session_context(session_id)
    context.messages.append({"role": role, "content": content})
    context.last_updated = datetime.now()

    # Keep last N turns only
    if len(context.messages) > MAX_TURNS * 2:
        context.messages = context.messages[-(MAX_TURNS * 2):]


def clear_session(session_id: str):
    """Clear session data"""
    if session_id in CHAT_SESSIONS:
        del CHAT_SESSIONS[session_id]


def reset_domain_context(session_id: str):
    """Reset domain context while keeping message history"""
    context = get_session_context(session_id)
    context.current_domain = None