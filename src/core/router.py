from src.core.classifier import QueryType
from src.services.normal_chat import normal_chat
from src.services.rag_chat import rag_chat


def route_query(prompt: str, query_type: QueryType,  session_id: str,config: dict):
    match query_type:
        case QueryType.NORMAL:
            return normal_chat(prompt,session_id ,config)

        case QueryType.RAG_PMJJBY | QueryType.RAG_NODEJS | QueryType.RAG_BC:
            return rag_chat(prompt, "combined-ingest", session_id, config)

        case _:
            return "Unable to classify the query."
