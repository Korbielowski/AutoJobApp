from contextlib import asynccontextmanager
from typing import AsyncGenerator, TypeVar

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database.init_db import init_db
from backend.exceptions import ApplicationException
from backend.logger import get_logger
from backend.routes.main import api_router

logger = get_logger()
T = TypeVar("T", bound=ApplicationException)


@asynccontextmanager
async def setup(inner_app: FastAPI) -> AsyncGenerator:
    init_db()

    inner_app.mount(
        "/static",
        StaticFiles(directory=settings.ROOT_DIR / "static"),
        name="static",
    )

    yield


app = FastAPI(title=settings.PROJECT_NAME, debug=True, lifespan=setup)
app.include_router(api_router)


@app.exception_handler(ApplicationException)
async def catch_application_exceptions(
    request: Request, exc: T
) -> JSONResponse:
    response_data = {
        "message": exc.message,
        "causes": exc.causes,
        "retries": exc.retries,
    }
    return JSONResponse(
        content=jsonable_encoder(response_data), status_code=400
    )
