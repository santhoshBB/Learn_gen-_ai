from langchain_qdrant import QdrantVectorStore
from src.app import load_config, get_embedding


def get_vector_store(collection_name: str | None = None):
    config = load_config("configs/dev.json")

    qdrant_cfg = config["databases"]["qdrant"]
    qdrant_model= config['defaults']['embedding']
    embedder = get_embedding(config, qdrant_model )

    return QdrantVectorStore.from_existing_collection(
        collection_name=collection_name or qdrant_cfg["collection"],
        url=qdrant_cfg["url"],
        embedding=embedder
    )
