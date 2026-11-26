from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from .config import get_settings
from .logging import configure_logging
from .middleware import RequestContextMiddleware


def create_service_app(service_name: str) -> FastAPI:
    settings = get_settings()
    configure_logging(service_name)
    app = FastAPI(title=f"FinFlow AI {service_name}", version="1.0.0")
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin, "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    Instrumentator().instrument(app).expose(app)

    @app.get("/health", tags=["system"])
    def health():
        return {"service": service_name, "status": "ok"}

    return app

