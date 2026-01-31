from functools import wraps
from devtools import pformat
import time
from typing import Callable, Any

from starlette.datastructures import URL
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from backend.logger import get_logger


logger = get_logger()


def measure_func_time(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        end = time.perf_counter()
        logger.debug(
            f"Function '{func.__name__}' took: {end - start}[sec] to execute"
        )
        return result

    return wrapper


def return_exception_response(body: str, url: URL, status_code: int = 400, exceptions: Any = None) -> JSONResponse:
    content = {"body": body, "url": str(url)}
    if exceptions:
        logger.info(pformat(exceptions))
        content["exceptions"] = exceptions
    return JSONResponse(status_code=status_code, content=jsonable_encoder(content))
