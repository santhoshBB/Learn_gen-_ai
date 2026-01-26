import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from src.api.routers import root, chat, upload

app = FastAPI(title="RAG + Agentic AI System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(root.router)
app.include_router(chat.router)
app.include_router(upload.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)