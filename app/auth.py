import secrets
from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED

api_key_header = APIKeyHeader(
    name="X-KAI-Key",
    description="Your KAI access key. Keep it private; do not use your OpenAI key.",
    auto_error=False,
)

def validate_api_key(
        request: Request,
        api_key_header: str = Security(api_key_header)
    ):
    expected = request.app.state.settings.KAI_API_KEY.get_secret_value()

    if not api_key_header or not secrets.compare_digest(
        api_key_header.encode("utf-8"),
        expected.encode("utf-8"),
    ):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )

    return api_key_header