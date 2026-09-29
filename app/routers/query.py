from fastapi import APIRouter, Request, Depends
from openai import AsyncOpenAI
from app.schemas.openai import PromptRequest

router = APIRouter()

@router.post("/query")
async def query(body: PromptRequest, request: Request):
    profile: str = request.app.state.profile
    system_prompt: str = request.app.state.system_prompt
    instructions = f"{system_prompt}\n\n<profile>\n{profile}\n</profile>"
    client: AsyncOpenAI = request.app.state.openai_client
    try:
        response = await client.responses.create(
                model="gpt-5-mini",
                input=body.messages,
                instructions=instructions
            )
    except Exception as exc:
        print(exc)

    return response.output_text