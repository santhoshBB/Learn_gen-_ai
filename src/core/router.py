from src.core.classifier import QueryType
from src.services.normal_chat import normal_chat
from src.services.rag_chat import rag_chat


def route_query(prompt: str, query_type: QueryType, config: dict):
    match query_type:
        case QueryType.NORMAL:
            return normal_chat(prompt, config)

        case QueryType.RAG_NODEJS:
            return rag_chat(prompt, "nodejs", config)

        case QueryType.RAG_BC:
            return rag_chat(prompt, "bc", config)

        case QueryType.RAG_PMJJBY:
            return rag_chat(prompt, "pmjjby", config)

        case _:
            return "Unable to classify the query."
