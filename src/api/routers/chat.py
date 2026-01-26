from fastapi import APIRouter, HTTPException
from src.app import load_config
from src.core.classifier import classify_query
from src.core.router import route_query
import logging

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def generate_text(prompt: str):
    try:
        config = load_config("configs/dev.json")

        query_type = classify_query(prompt, config)
        response = route_query(prompt, query_type, config)

        return {
            "type": query_type,
            "response": response
        }

    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal error")
