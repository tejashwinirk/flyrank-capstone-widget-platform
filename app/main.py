from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.public_widgets import router as public_widgets_router
from app.api.submissions import router as submissions_router
from app.api.widgets import router as widgets_router
from app.services.rate_limit import limiter


MAX_REQUEST_BODY_SIZE = 64 * 1024  # 64 KB


app = FastAPI(
    title="FlyRank Lead Capture Platform",
    version="1.0.0",
)


# -------------------------------------------------------------------
# Rate limiting
# -------------------------------------------------------------------

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


app.add_middleware(
    SlowAPIMiddleware,
)


# -------------------------------------------------------------------
# CORS
# -------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=[
        "GET",
        "POST",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# Request body protection
# -------------------------------------------------------------------

@app.middleware("http")
async def request_size_limit(
    request: Request,
    call_next,
):
    content_length = request.headers.get("content-length")

    if content_length:
        try:
            if int(content_length) > MAX_REQUEST_BODY_SIZE:
                return JSONResponse(
                    status_code=413,
                    content={
                        "detail": "Request body too large"
                    },
                )
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={
                    "detail": "Invalid Content-Length header"
                },
            )

    # For requests without a reliable Content-Length header,
    # inspect the actual body.
    if request.method in {"POST", "PUT", "PATCH"}:
        body = await request.body()

        if len(body) > MAX_REQUEST_BODY_SIZE:
            return JSONResponse(
                status_code=413,
                content={
                    "detail": "Request body too large"
                },
            )

    return await call_next(request)


# -------------------------------------------------------------------
# API routers
# -------------------------------------------------------------------

app.include_router(auth_router)
app.include_router(widgets_router)
app.include_router(public_widgets_router)
app.include_router(submissions_router)
app.include_router(dashboard_router)


# -------------------------------------------------------------------
# Health check
# -------------------------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }