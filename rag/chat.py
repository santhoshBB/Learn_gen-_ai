from langchain_community.embeddings import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI


COLLECTION = "nodejs_pdf"
QDRANT = "http://localhost:6333"

embedder = OllamaEmbeddings(model="nomic-embed-text")
client = OpenAI(base_url="http://localhost:11434/v1", api_key="none")

vector_store = QdrantVectorStore.from_existing_collection(
    collection_name= COLLECTION,
    url=QDRANT,
    embedding=embedder
)

user_query = input("Ask Something:")

# gives relevant chunks
search_result= vector_store.similarity_search(query=user_query)
context_str = "\n".join(
    [f"File: {doc.metadata.get('source', 'N/A')}, "
     f"Page: {doc.metadata.get('page', 'N/A')}\n{doc.page_content}"
     for doc in search_result]
)

SYSTEM_PROMPT = f"""
You are a strict technical Q&A assistant that answers from Node.js documentation only.

STRICT RULES:
1. Use ONLY information from the provided context excerpts
2. ALWAYS mention the exact page number(s) for every piece of information you use
3. Use format: [Page X] right after the relevant sentence
4. If no clear answer exists in context → reply ONLY with:
   "Information not sufficiently covered in the provided documentation sections."

Example of good answer:
Node.js allows customizing HTTP requests using various options and callbacks [Page 42].
The 'request' library provides json parsing support [Pages 38-39].

Context from Node.js documentation:
{context_str}
"""

response = client.chat.completions.create(
    model="gemma2:2b",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]
)

print(response.choices[0].message.content)