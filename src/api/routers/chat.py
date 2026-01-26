from fastapi import APIRouter, HTTPException
from src.app import load_config, get_llm
from src.db.qdrant_client import get_vector_store
import logging

router = APIRouter(prefix="/chat", tags=["chat"])


def retrieve_context(query: str, k: int = 5) -> str:
    vector_store = get_vector_store()
    docs = vector_store.similarity_search(query=query, k=k)

    if not docs:
        return ""

    context = "\n\n".join(
        [
            f"[Source: {doc.metadata.get('source', 'N/A')}, "
            f"Page: {doc.metadata.get('page', 'N/A')}]\n"
            f"{doc.page_content}"
            for doc in docs
        ]
    )
    return context


@router.post("")
async def generate_text(prompt: str):
    try:
        config = load_config("configs/dev.json")
        context_str = retrieve_context(prompt)

        SYSTEM_PROMPT = f"""
You are a strict technical Q&A assistant that answers from Node.js documentation only.

STRICT RULES:
1. Use ONLY information from the provided context excerpts
2. ALWAYS mention the exact page number(s) for every piece of information you use
3. Use format: [Page X] right after the relevant sentence
4. If no clear answer exists in context → reply ONLY with:
   "Information not sufficiently covered in the provided documentation sections."

Context from Node.js documentation:
{context_str}
        """

        llm = get_llm(config, config["defaults"]["llm"])

        response = llm.chat.completions.create(
            model="gemma2:2b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )

        return {"response": response}

    except Exception as e:
        logging.error(f"Error generating text: {e}")
        raise HTTPException(status_code=500, detail=str(e))