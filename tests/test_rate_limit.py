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
    "REDIS_URL": "memory://",
    "TRUST_RAILWAY_PROXY": "false",
    "QUERY_REQUESTS_PER_MINUTE": "2",
    "GENERATION_REQUESTS_PER_DAY": "3",
}):
    from app.main import app
    from app.rate_limit import limiter


class RateLimitTest(unittest.TestCase):
    def setUp(self):
        limiter.reset()
        self.addCleanup(limiter.reset)

    def make_requests(self, hosts):
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

        responses = []
        with patch("app.main.AsyncOpenAI", return_value=model_client):
            for host in hosts:
                with TestClient(app, client=(host, 50000)) as client:
                    responses.append(client.post(
                        "/query",
                        headers={"X-KAI-Key": "test-kai-key"},
                        json={"messages": [{"role": "user", "content": "Hi!"}]},
                    ))

        return responses, model_client.responses.create.await_count

    def test_configured_minute_limit_is_enforced(self):
        responses, model_calls = self.make_requests(["192.0.2.1"] * 3)

        self.assertEqual(
            [response.status_code for response in responses],
            [200, 200, 429],
        )
        self.assertIn("2 per 1 minute", responses[-1].json()["error"])
        # Rejected requests must never reach the paid API.
        self.assertEqual(model_calls, 2)

    def test_configured_daily_limit_is_shared_across_visitors(self):
        responses, model_calls = self.make_requests(
            [f"192.0.2.{number}" for number in range(1, 5)]
        )

        self.assertEqual(
            [response.status_code for response in responses],
            [200, 200, 200, 429],
        )
        self.assertIn("daily limit", responses[-1].json()["error"])
        self.assertEqual(model_calls, 3)


if __name__ == "__main__":
    unittest.main()
