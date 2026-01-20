from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.app import load_config, get_llm, get_embedding
import logging
import uvicorn

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to RAG + Agentic AI System"}

@app.post("/generate")
async def generate_text(prompt: str):
    try:
        config = load_config("configs/dev.json")
        llm = get_llm(config, config["defaults"]["llm"])
        response = llm.generate(prompt)
        return {"response": response}
    except Exception as e:
        logging.error(f"Error generating text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/embed")
async def generate_embedding(text: str):
    try:
        config = load_config("configs/dev.json")
        embedding = get_embedding(config, config["defaults"]["embedding"])
        embedding_vector = embedding.embed(text)
        return {"embedding": embedding_vector}
    except Exception as e:
        logging.error(f"Error generating embedding: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run_server()
