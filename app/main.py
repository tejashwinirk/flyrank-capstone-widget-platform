from fastapi import FastAPI

from app.api.widgets import router as widgets_router


app = FastAPI(
    title="FlyRank Lead Capture Platform",
    version="1.0.0",
)


app.include_router(widgets_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}