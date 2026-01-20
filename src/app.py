import json
import logging
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config(config_path: str) -> dict:
    """Load JSON configuration file."""
    with open(config_path, "r") as f:
        return json.load(f)

def get_llm(config: dict, model_name: str):
    """Initialize and return the LLM client."""
    # Placeholder: Implement your LLM logic here
    from src.models.llm_client import RemoteLLM, LocalLLM
    model_config = config["llms"][model_name]
    if model_config["type"] == "remote":
        return RemoteLLM(
            api_key=os.getenv(model_config["api_key_env"]),
            base_url=model_config["base_url"],
            model=model_name
        )
    else:
        return LocalLLM(
            url=model_config["url"],
            model=model_name
        )

def get_embedding(config: dict, model_name: str):
    """Initialize and return the embedding client."""
    # Placeholder: Implement your embedding logic here
    from src.models.embedding_client import RemoteEmbedding, LocalEmbedding
    model_config = config["embeddings"][model_name]
    if model_config["type"] == "remote":
        return RemoteEmbedding(
            api_key=os.getenv(model_config["api_key_env"]),
            base_url=model_config["base_url"],
            model=model_name
        )
    else:
        return LocalEmbedding(
            url=model_config["url"],
            model=model_name
        )

def main():
    load_dotenv()
    logger.info("Starting RAG + Agentic AI System (Dev)")

    # Load dev config
    config = load_config("configs/dev.json")
    logger.info(f"Loaded config for: {config['defaults']}")

    # Run the FastAPI server
    from src.main import run_server
    run_server()

if __name__ == "__main__":
    main()
