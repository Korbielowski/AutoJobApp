from contextlib import asynccontextmanager
from typing import AsyncGenerator

from agents import set_tracing_disabled
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse

from backend.config import settings
from backend.database.db import init_db
from backend.logger import get_logger
from backend.routes.main import api_router
from backend.utils import return_exception_response

logger = get_logger()


@asynccontextmanager
async def setup(inner_app: FastAPI) -> AsyncGenerator:
    init_db()

    set_tracing_disabled(disabled=True)

    inner_app.mount(
        path="/",
        app=StaticFiles(directory=settings.ROOT_DIR / "_static", html=True),
        name="static",
    )

    yield


app = FastAPI(title=settings.PROJECT_NAME, debug=True, lifespan=setup)
app.include_router(api_router)

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    return return_exception_response(body=exception.body, url=request.url, exceptions=exception.errors())
