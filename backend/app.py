from contextlib import asynccontextmanager
from typing import AsyncGenerator

from agents import set_tracing_disabled
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database.db import init_db
from backend.logger import get_logger
from backend.routes.main import api_router

logger = get_logger()


@asynccontextmanager
async def setup(inner_app: FastAPI) -> AsyncGenerator:
    init_db()
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.exception("Exception message")
    logger.error("Error message")
    logger.success("Success message")

    set_tracing_disabled(disabled=True)

    inner_app.mount(
        "/static",
        StaticFiles(directory=settings.ROOT_DIR / "static"),
        name="static",
    )

    yield


app = FastAPI(title=settings.PROJECT_NAME, debug=True, lifespan=setup)
app.include_router(api_router)
