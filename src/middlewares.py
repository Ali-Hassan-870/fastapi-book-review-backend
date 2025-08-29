from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
import time

logger = logging.getLogger("uvicorn.access")
logger.disabled = True


def register_middlewares(app: FastAPI):
    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        request_procesing_time = time.time() - start_time
        message = (
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
            f"{request.client.host}:{request.client.port} "
            f'"{request.method} {request.url.path}" '
            f"{response.status_code} "
            f"- {request_procesing_time:.4f}s"
        )
        print(message)
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1"],
    )