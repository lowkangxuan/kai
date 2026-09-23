from pathlib import Path
from fastapi import FastAPI
from openai import AsyncOpenAI
from app.routers import query
from app.settings import settings

PROJECT_ROOT = Path(__file__).resolve().parent.parent

async def lifespan(app: FastAPI):
    print("open")
    app.state.profile = (
        (PROJECT_ROOT / "content/profile.md").read_text(encoding="utf-8").strip()
    )
    app.state.system_prompt = (
        (PROJECT_ROOT / "prompts/system.md").read_text(encoding="utf-8").strip()
    )
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

app.include_router(query.router)