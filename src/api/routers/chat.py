from fastapi import APIRouter, HTTPException
from src.app import load_config
from src.core.classifier import classify_query, QueryType
from src.core.router import master_route_query
import logging
from pydantic import BaseModel
from src.core.chat_memory import get_current_domain


router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    prompt: str
    sessionId: str



@router.post("")
async def generate_text(req: ChatRequest):
    """
    Main endpoint with improved classification and routing
    """
    try:
        config = load_config("configs/dev.json")
        
        # Get current conversation domain (if any)
        current_domain = get_current_domain(req.sessionId)
        
        # Convert string domain back to QueryType enum if needed
        current_domain_enum = None
        if current_domain:
            try:
                current_domain_enum = QueryType(current_domain)
            except ValueError:
                current_domain_enum = None
        
        # Classify query with context awareness
        query_type = classify_query(
            req.prompt, 
            config,
            current_domain=current_domain_enum
        )
        
        # Route to appropriate service
        response = master_route_query(req.prompt, req.sessionId, config)
        
        return {
            "type": query_type.value,
            "response": response,
            "current_domain": current_domain  # Return for debugging
        }

    except Exception as e:
        logging.error(f"Error in generate_text: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error")