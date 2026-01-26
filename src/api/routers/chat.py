from fastapi import APIRouter, HTTPException
from src.app import load_config
from src.core.classifier import classify_query
from src.core.router import route_query
import logging
from pydantic import BaseModel


router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    prompt: str
    sessionId: str

@router.post("")
async def generate_text(req: ChatRequest):
    try:
        config = load_config("configs/dev.json")

        query_type = classify_query(req.prompt, config)
        response = route_query(req.prompt, query_type, req.sessionId, config)

        return {
            "type": query_type,
            "response": response
        }

    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal error")
