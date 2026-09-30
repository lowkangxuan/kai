import logging
import openai
from fastapi import HTTPException
from starlette.status import (
    HTTP_502_BAD_GATEWAY,
    HTTP_503_SERVICE_UNAVAILABLE,
    HTTP_504_GATEWAY_TIMEOUT,
)

logger = logging.getLogger(__name__)

def upstream_error(exc: Exception) -> HTTPException:
    """Map an OpenAI SDK error to a client-safe HTTPException, logging the details."""
    logger.error("OpenAI request failed", exc_info=exc)

    # APITimeoutError subclasses APIConnectionError, so check it first
    if isinstance(exc, openai.APITimeoutError):
        return HTTPException(HTTP_504_GATEWAY_TIMEOUT, "Model request timed out")
    if isinstance(exc, openai.RateLimitError):
        return HTTPException(HTTP_503_SERVICE_UNAVAILABLE, "Model is busy, try again later")
    return HTTPException(HTTP_502_BAD_GATEWAY, "Model request failed")
