from contextlib import asynccontextmanager
from typing import AsyncGenerator

from agents import set_tracing_disabled
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database.db import init_db
from backend.routes.main import api_router


@asynccontextmanager
async def setup(inner_app: FastAPI) -> AsyncGenerator:
    init_db()

    set_tracing_disabled(disabled=True)

    inner_app.mount(
        "/static",
        StaticFiles(directory=settings.ROOT_DIR / "static"),
        name="static",
    )

    yield
    # TODO: In the future release all resources if needed


app = FastAPI(title=settings.PROJECT_NAME, debug=True, lifespan=setup)
app.include_router(api_router)
