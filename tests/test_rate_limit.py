"""Run with: uv run python -m unittest discover -s tests -v"""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

# Use fake credentials and local counters, even if a real .env exists.
with patch.dict(os.environ, {
    "KAI_API_KEY": "test-kai-key",
    "OPENAI_API_KEY": "test-openai-key",
    "RATELIMIT_STORAGE_URL": "memory://",
}):
    from app.main import app
    from app.rate_limit import limiter


class RateLimitTest(unittest.TestCase):
    def test_sixth_request_is_rejected(self):
        limiter.reset()
        self.addCleanup(limiter.reset)

        # Each accepted request gets a fresh fake model stream.
        def make_stream(**kwargs):
            stream = MagicMock()
            stream.__aiter__.return_value = [
                SimpleNamespace(type="response.completed"),
            ]
            stream.close = AsyncMock()
            return stream

        model_client = MagicMock()
        model_client.__aenter__.return_value = model_client
        model_client.responses.create = AsyncMock(side_effect=make_stream)

        with patch("app.main.AsyncOpenAI", return_value=model_client):
            with TestClient(app) as client:
                responses = [
                    client.post(
                        "/query",
                        headers={"X-KAI-Key": "test-kai-key"},
                        json={"messages": [{"role": "user", "content": "Hi!"}]},
                    )
                    for _ in range(6)
                ]

        self.assertEqual(
            [response.status_code for response in responses],
            [200, 200, 200, 200, 200, 429],
        )
        self.assertIn("5 per 1 minute", responses[-1].json()["error"])
        # Rejected requests must never reach the paid API.
        self.assertEqual(model_client.responses.create.await_count, 5)


if __name__ == "__main__":
    unittest.main()
