from fastapi import FastAPI

app = FastAPI(title="kai API")

@app.get("/health")
def health():
    return {"status": "ok"}

