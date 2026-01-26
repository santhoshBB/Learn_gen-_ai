from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from uuid import uuid4
from pathlib import Path
import tempfile
import logging
from datetime import datetime

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore

from src.app import load_config, get_embedding

router = APIRouter(prefix="/upload", tags=["ingest"])

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 300
ALLOWED_EXTENSIONS = {".pdf"}


@router.post("/and-ingest")
async def upload_and_ingest(
    files: List[UploadFile] = File(..., description="Upload one or more PDF files")
):
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
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(await file.read())
                temp_path = Path(tmp.name)

            loader = PyPDFLoader(str(temp_path))
            documents = loader.load()

            document_id = str(uuid4())
            upload_time = datetime.utcnow().isoformat() + "Z"

            for doc in documents:
                doc.metadata.update({
                    "document_id": document_id,
                    "source": filename,
                    "file_type": "pdf",
                    "upload_timestamp": upload_time,
                })

            chunks = text_splitter.split_documents(documents)

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