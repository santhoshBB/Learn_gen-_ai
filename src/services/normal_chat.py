from src.app import get_llm
from src.core.chat_memory import add_message, get_session_history


def normal_chat(prompt: str, session_id: str, config: dict):
    add_message(session_id, "user", prompt)

    llm = get_llm(config, config["defaults"]["llm"])
    response = llm.create(
        messages=get_session_history(session_id)
    )

    answer = response.choices[0].message.content
    add_message(session_id, "assistant", answer)

    return answer
