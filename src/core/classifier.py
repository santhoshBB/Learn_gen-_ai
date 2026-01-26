from enum import Enum
from src.app import get_llm


class QueryType(str, Enum):
    NORMAL = "normal"
    RAG_NODEJS = "rag_nodejs"
    RAG_BC = "rag_bc"
    RAG_PMJJBY = "rag_pmjjby"


CLASSIFIER_PROMPT = """
Classify the user query into ONE of the following categories:

- normal → casual / generic / chit-chat / non-document questions
- rag_nodejs → Node.js documentation or technical Node.js questions
- rag_bc → Banking Correspondent (BC) policy related questions
- rag_pmjjby → PMJJBY insurance scheme questions

Respond ONLY with the category key.
"""


def classify_query(prompt: str, config: dict) -> QueryType:
    llm = get_llm(config, config["defaults"]["llm"])

    response = llm.create(
    messages=[
        {"role": "system", "content": CLASSIFIER_PROMPT},
        {"role": "user", "content": prompt}
    ]
)


    label = response.choices[0].message.content.strip().lower()

    return QueryType(label)
