from typing import Dict, List

MAX_TURNS = 3  # last 3 user+assistant turns

CHAT_SESSIONS: Dict[str, List[dict]] = {}


def get_session_history(session_id: str) -> List[dict]:
    if session_id not in CHAT_SESSIONS:
        CHAT_SESSIONS[session_id] = []
    return CHAT_SESSIONS[session_id]


def add_message(session_id: str, role: str, content: str):
    history = get_session_history(session_id)
    history.append({"role": role, "content": content})

    # keep last N turns only
    del history[:-MAX_TURNS * 2]
