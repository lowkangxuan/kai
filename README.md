# kai

## Deployment

Deploy from the repository root. `railpack.json` starts the FastAPI app with:

```sh
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Set `KAI_API_KEY` and `OPENAI_API_KEY` in the deployment environment. The server
uses the platform-provided `PORT`, defaulting to `8000` locally. Use `/health`
as the health check endpoint.

Rate limits can be configured in the deployment environment or a local `.env`:

```env
QUERY_REQUESTS_PER_MINUTE=5
TOTAL_QUERY_REQUESTS_PER_DAY=30=30
```

These are the defaults when unset. Both values must be positive integers. The
minute limit applies per client IP; the daily generation limit is shared across
all visitors. Restart or redeploy the app after changing either value.
