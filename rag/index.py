from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from langchain_ollama import OllamaEmbeddings

# === CONFIG ===
COLLECTION = "nodejs_pdf"
QDRANT = "http://localhost:6333"
# ===============

# 1. Load PDF
pdf_path = Path(__file__).parent / "nodejs.pdf"
docs = PyPDFLoader(str(pdf_path)).load()

# 2. Split into chunks
chunks = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=400
).split_documents(docs)

# 3. Ollama Nomic embedder
embedder = OllamaEmbeddings(model="nomic-embed-text")

vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedder,
    url=QDRANT,
    collection_name=COLLECTION
)


print(f"Stored {len(chunks)} chunks in Qdrant 🚀")
