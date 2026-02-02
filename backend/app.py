from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncio

from agents import set_tracing_disabled
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database.db import init_db
from backend.logger import get_logger
from backend.routes.main import api_router

logger = get_logger()


def handle_asyncio_exception(loop, context):
    logger.info("Ending job scraping process")


@asynccontextmanager
async def setup(inner_app: FastAPI) -> AsyncGenerator:
    init_db()

    set_tracing_disabled(disabled=True)

    inner_app.mount(
        "/static",
        StaticFiles(directory=settings.ROOT_DIR / "static"),
        name="static",
    )

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_asyncio_exception)

    yield


app = FastAPI(title=settings.PROJECT_NAME, debug=True, lifespan=setup)
app.include_router(api_router)
