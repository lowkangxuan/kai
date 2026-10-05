# kai

## Deployment

Deploy from the repository root. `railpack.json` starts the FastAPI app with:

```sh
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Set `KAI_API_KEY` and `OPENAI_API_KEY` in the deployment environment. The server
uses the platform-provided `PORT`, defaulting to `8000` locally. Use `/health`
as the health check endpoint.
