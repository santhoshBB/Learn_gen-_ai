from fastapi import APIRouter, HTTPException
from src.app import load_config
import logging
from pydantic import BaseModel
from src.core.orchestrator import process_query

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
        
        # ONE FUNCTION CALL - that's it!
        response = process_query(
            query=req.prompt,
            session_id=req.sessionId,
            config=config
        )
        
        return {
            "type": "query_type.value",
            "response": response,
            "sessionId": req.sessionId,
            "current_domain": "current_domain"  # Return for debugging
        }

    except Exception as e:
        logging.error(f"Error in generate_text: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error")