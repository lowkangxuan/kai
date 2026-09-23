from fastapi import APIRouter
from openai import AsyncOpenAI
from app.settings import settings

router = APIRouter()

@router.post("/prompt")
async def query(message: str):
    async with AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY.get_secret_value()
    ) as client: 
        response = await client.responses.create(
            model="gpt-5-mini",
            input=message
        )

    return response.output_text