from contextlib import asynccontextmanager
import logging
from time import perf_counter

from fastapi import FastAPI, Request
from sqlalchemy import text

from app.api.v1 import routes as todo_routes
from app.config import get_settings
from app.db.base import engine


logger = logging.getLogger("todo_api")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="TODO API", version="1.0.0")
    app.include_router(todo_routes.router)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = perf_counter()
        response = await call_next(request)
        duration = (perf_counter() - start) * 1000
        logger.info(
            "method=%s path=%s status=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )
        return response

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
        return {"status": "ok", "database": str(settings.database_url)}

    return app


app = create_app()
