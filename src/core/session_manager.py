# ============================================
# FILE: src/core/session_manager.py
# Redis-based session management with conversation memory
# ============================================

from typing import Dict, List, Optional
from datetime import datetime
import json
import redis
from redis.exceptions import RedisError

class ChatSession:
    def __init__(self, session_id: str, redis_client: redis.Redis):
        self.session_id = session_id
        self.redis_client = redis_client
        self._redis_key = f"session:{session_id}"
        
        # Initialize session in Redis if it doesn't exist
        if not self.redis_client.exists(self._redis_key):
            initial_data = {
                "messages": [],
                "user_info": {},
                "is_authenticated": False,
                "created_at": datetime.now().isoformat()
            }
            self.redis_client.set(
                self._redis_key,
                json.dumps(initial_data),
                ex=86400  # 24 hour expiry
            )
    
    def _get_session_data(self) -> Dict:
        """Retrieve session data from Redis"""
        data = self.redis_client.get(self._redis_key)
        if data:
            return json.loads(data)
        # Return default if not found
        return {
            "messages": [],
            "user_info": {},
            "is_authenticated": False,
            "created_at": datetime.now().isoformat()
        }
    
    def _save_session_data(self, data: Dict):
        """Save session data to Redis"""
        self.redis_client.set(
            self._redis_key,
            json.dumps(data),
            ex=86400  # 24 hour expiry
        )
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        data = self._get_session_data()
        
        data["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep last 10 messages only
        if len(data["messages"]) > 10:
            data["messages"] = data["messages"][-10:]
        
        self._save_session_data(data)
    
    def get_history(self) -> List[dict]:
        """Get conversation history for LLM context"""
        data = self._get_session_data()
        return data.get("messages", [])
    
    def set_user_info(self, key: str, value: str):
        """Remember user details like name"""
        data = self._get_session_data()
        data["user_info"][key] = value
        self._save_session_data(data)
    
    def get_user_info(self, key: str) -> Optional[str]:
        """Get remembered user details"""
        data = self._get_session_data()
        return data.get("user_info", {}).get(key)
    
    @property
    def messages(self) -> List[dict]:
        """Property to access messages (for backward compatibility)"""
        return self.get_history()
    
    @property
    def user_info(self) -> Dict:
        """Property to access user_info (for backward compatibility)"""
        data = self._get_session_data()
        return data.get("user_info", {})
    
    @property
    def is_authenticated(self) -> bool:
        """Property to access authentication status"""
        data = self._get_session_data()
        return data.get("is_authenticated", False)
    
    @is_authenticated.setter
    def is_authenticated(self, value: bool):
        """Set authentication status"""
        data = self._get_session_data()
        data["is_authenticated"] = value
        self._save_session_data(data)
    
    @property
    def created_at(self) -> datetime:
        """Property to access creation time"""
        data = self._get_session_data()
        created_str = data.get("created_at", datetime.now().isoformat())
        return datetime.fromisoformat(created_str)
    
    def delete(self):
        """Delete session from Redis"""
        self.redis_client.delete(self._redis_key)


# Redis connection pool (singleton)
_redis_pool = None

def get_redis_client() -> redis.Redis:
    """Get or create Redis client with connection pooling"""
    global _redis_pool
    
    if _redis_pool is None:
        _redis_pool = redis.ConnectionPool(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True,
            max_connections=10
        )
    
    return redis.Redis(connection_pool=_redis_pool)


def get_session(session_id: str) -> ChatSession:
    """Get or create session (now Redis-backed)"""
    try:
        redis_client = get_redis_client()
        return ChatSession(session_id, redis_client)
    except RedisError as e:
        # Fallback to in-memory session if Redis fails
        print(f"Redis connection failed: {e}. Using in-memory fallback.")
        # You could implement a fallback to dict here if needed
        raise


# ============================================
# Utility functions for session management
# ============================================

def list_active_sessions(pattern: str = "session:*") -> List[str]:
    """List all active session IDs"""
    redis_client = get_redis_client()
    keys = redis_client.keys(pattern)
    return [key.replace("session:", "") for key in keys]


def delete_session(session_id: str):
    """Delete a specific session"""
    redis_client = get_redis_client()
    redis_client.delete(f"session:{session_id}")


def clear_all_sessions():
    """Clear all sessions (use with caution!)"""
    redis_client = get_redis_client()
    keys = redis_client.keys("session:*")
    if keys:
        redis_client.delete(*keys)


def get_session_count() -> int:
    """Get count of active sessions"""
    redis_client = get_redis_client()
    return len(redis_client.keys("session:*"))