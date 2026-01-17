from functools import wraps
import time
from typing import Callable

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
