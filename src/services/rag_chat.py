from src.rag.retriever import retrieve_context
from src.rag.prompts import build_rag_prompt
from src.app import get_llm


def rag_chat(prompt: str, collection: str, config: dict):
    context = retrieve_context(prompt, collection)

    system_prompt = build_rag_prompt(context)
    llm = get_llm(config, config["defaults"]["llm"])

    response = llm.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
    )

    return response.choices[0].message.content
