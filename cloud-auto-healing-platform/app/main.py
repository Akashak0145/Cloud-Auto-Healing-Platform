from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="Cloud Infrastructure Monitoring Platform",
    version="1.0.0"
)

Instrumentator().instrument(app).expose(app)


@app.get("/")
def home():
    return {
        "message": "Cloud Monitoring Platform Running",
        "status": "success"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "demo-app"
    }
