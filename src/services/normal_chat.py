from src.app import get_llm


def normal_chat(prompt: str, config: dict):
    llm = get_llm(config, config["defaults"]["llm"])

    response = llm.create(
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
