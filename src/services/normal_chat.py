from src.app import get_llm


# def normal_chat(prompt: str, config: dict):
#     llm = get_llm(config, config["defaults"]["llm"])

#     response = llm.create(
#         messages=[
#             {"role": "user", "content": prompt}
#         ]
#     )

#     return response.choices[0].message.content

def normal_chat(prompt: str, config: dict):
    return (
        "I can assist only with queries related to Node.js, "
        "Banking Correspondent (BC/CSP), and PMJJBY. "
        "Please ask a question related to these topics."
    )

