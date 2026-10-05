import json
import logging
import openai
from fastapi import APIRouter, Request
from fastapi.sse import EventSourceResponse
from openai import AsyncOpenAI
from app.rate_limit import limiter, daily_budget
from app.errors import upstream_error
from app.schemas.openai import PromptRequest
from app.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()

def sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"

@router.post("/query")
@limiter.limit(f"{settings.QUERY_REQUESTS_PER_MINUTE}/minute")
@daily_budget
async def query(body: PromptRequest, request: Request):
    profile: str = request.app.state.profile
    system_prompt: str = request.app.state.system_prompt
    instructions = f"{system_prompt}\n\n<profile>\n{profile}\n</profile>"
    client: AsyncOpenAI = request.app.state.openai_client

    # Open the stream before responding so connection, auth and rate-limit
    # failures still come back as a proper HTTP error status
    try:
        stream = await client.responses.create(
                model="gpt-5-mini",
                input=body.messages,
                instructions=instructions,
                max_output_tokens=1500,
                timeout=30.0,
                stream=True,
            )
    except openai.OpenAIError as exc:
        raise upstream_error(exc) from exc

    # Past this point the 200 is already sent, so failures become `error` events
    async def events():
        try:
            async for event in stream:
                if event.type == "response.output_text.delta":
                    yield sse("delta", event.delta)
                elif event.type == "response.completed":
                    yield sse("done", {"status": "completed"})
                elif event.type == "response.incomplete":
                    details = event.response.incomplete_details
                    yield sse("done", {
                        "status": "incomplete",
                        "reason": details.reason if details else None,
                    })
                elif event.type in ("response.failed", "error"):
                    logger.error("OpenAI stream reported failure: %s", event)
                    yield sse("error", {"message": "Model request failed"})
        except Exception:
            logger.exception("OpenAI stream failed")
            yield sse("error", {"message": "Model request failed"})
        finally:
            await stream.close()

    return EventSourceResponse(events())
