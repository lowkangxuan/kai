from fastapi import FastAPI
from openai import AsyncOpenAI
from app.routers import chat

app = FastAPI(title="kai API")
client = AsyncOpenAI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(chat.router)