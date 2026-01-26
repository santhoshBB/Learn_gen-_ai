from src.rag.retriever import retrieve_context
from src.rag.prompts import build_rag_prompt
from src.app import get_llm
from src.core.chat_memory import add_message, get_session_history


def rag_chat(prompt: str, collection: str, session_id: str, config: dict):
    # store user message
    add_message(session_id, "user", prompt)

    context = retrieve_context(prompt, collection)
    system_prompt = build_rag_prompt(context)

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(get_session_history(session_id))

    llm = get_llm(config, config["defaults"]["llm"])
    response = llm.create(messages=messages)

    answer = response.choices[0].message.content
    add_message(session_id, "assistant", answer)

    return answer
