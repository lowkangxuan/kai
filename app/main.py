from fastapi import FastAPI
from openai import AsyncOpenAI
from app.routers import prompt
from app.settings import settings

async def lifespan(app: FastAPI):
    print("open")
    app.state.settings = settings
    async with AsyncOpenAI(
        api_key=app.state.settings.OPENAI_API_KEY.get_secret_value(),
        max_retries=0,
    ) as client:
        app.state.openai_client = client
        yield
    print("close")

app = FastAPI(title="kai API", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(prompt.router)