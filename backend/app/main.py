from fastapi import FastAPI

app = FastAPI(title="CS Assistant API")


@app.get("/api/health")
def health() -> dict[str, str]:
    """ใช้เช็กว่า backend รันอยู่"""
    return {"status": "ok"}
