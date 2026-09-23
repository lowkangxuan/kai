from fastapi import APIRouter, Request
from openai import AsyncOpenAI
from app.settings import settings
from app.schemas.openai import PromptRequest

router = APIRouter()

@router.post("/query")
async def query(body: PromptRequest, request: Request):
    client: AsyncOpenAI = request.app.state.openai_client
    try:
        response = await client.responses.create(
                model="gpt-5-mini",
                input=body.messages
            )
    except Exception as exc:
        print(exc)

    return response.output_text