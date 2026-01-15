from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings   # ⬅️ add this
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from langchain_community.vectorstores import Qdrant

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

# 4. Qdrant connection + collection
client = QdrantClient(url=QDRANT)
client.recreate_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(size=768, distance=Distance.COSINE)
)

# 5. Store in Qdrant
Qdrant.from_documents(
    chunks,
    embedder,
    url=QDRANT,
    collection_name=COLLECTION
)

print(f"Stored {len(chunks)} chunks in Qdrant 🚀")
