from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
from uuid import uuid4
from pathlib import Path
import tempfile
import logging
from datetime import datetime
import uvicorn
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from src.app import load_config, get_llm, get_embedding
from src.db.qdrant_client import get_vector_store

app = FastAPI(title="RAG + Agentic AI System")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 300
ALLOWED_EXTENSIONS = {".pdf"}


@app.get("/")
def read_root():
    return {"message": "Welcome to RAG + Agentic AI System"}


# @app.post("/similarity-search")
# def similarity_search(user_query: str):
#     vector_store = get_vector_store()
#     search_result = vector_store.similarity_search(query=user_query)
#     context_str = "\n".join(
#         [f"File: {doc.metadata.get('source', 'N/A')}, "
#          f"Page: {doc.metadata.get('page', 'N/A')}\n{doc.page_content}"
#          for doc in search_result]
#     )
#     return context_str
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


@app.post("/chat")
async def generate_text(prompt: str):
    try:
        config = load_config("configs/dev.json")
        context_str=retrieve_context(prompt)
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


@app.post("/upload-and-ingest")
async def upload_and_ingest(
    files: List[UploadFile] = File(..., description="Upload one or more PDF files")
):
    """
    Upload PDF files → automatically chunk, embed and store in Qdrant collection 'ingested_files'
    Returns success count and any errors (partial success supported)
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    config = load_config("configs/dev.json")
    embedder = get_embedding(config, config["defaults"]["embedding"])

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        add_start_index=True,
    )

    total_ingested_chunks = 0
    errors = []

    for file in files:
        filename = file.filename or "unnamed.pdf"
        ext = Path(filename).suffix.lower()

        if ext not in ALLOWED_EXTENSIONS:
            errors.append(f"Unsupported file type: {filename}")
            continue

        temp_path = None
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(await file.read())
                temp_path = Path(tmp.name)

            # Load PDF
            loader = PyPDFLoader(str(temp_path))
            documents = loader.load()

            # Add metadata
            document_id = str(uuid4())
            upload_time = datetime.utcnow().isoformat() + "Z"

            for doc in documents:
                doc.metadata.update({
                    "document_id": document_id,
                    "source": filename,
                    "file_type": "pdf",
                    "upload_timestamp": upload_time,
                    # Add more fields later if needed (user_id, tags, etc.)
                })

            # Split into chunks
            chunks = text_splitter.split_documents(documents)

            # Store in Qdrant (same collection for all files)
            QdrantVectorStore.from_documents(
                documents=chunks,
                embedding=embedder,
                url=config["databases"]["qdrant"]["url"],
                collection_name=config["databases"]["qdrant"]["collection"],
            )

            total_ingested_chunks += len(chunks)
            logging.info(f"Ingested {len(chunks)} chunks from {filename} (id: {document_id})")

        except Exception as exc:
            err_msg = f"{filename}: {str(exc)}"
            logging.error(err_msg, exc_info=True)
            errors.append(err_msg)
        finally:
            if temp_path and temp_path.exists():
                temp_path.unlink(missing_ok=True)

    # Response
    if errors:
        return JSONResponse(
            status_code=207,
            content={
                "message": f"Ingested {total_ingested_chunks} chunks with some errors",
                "ingested_chunks": total_ingested_chunks,
                "errors": errors
            }
        )

    return {
        "message": "All files successfully ingested",
        "ingested_chunks": total_ingested_chunks,
        "collection": config["databases"]["qdrant"]["collection"]
    }


def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run_server()