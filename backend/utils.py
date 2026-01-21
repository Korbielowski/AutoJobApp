from functools import wraps
import time
from typing import Callable, TypeVar

from pydantic_ai import AgentRunResult
from pydantic import BaseModel
from devtools import pformat

from backend.logger import get_logger


T = TypeVar("T", bound=BaseModel)
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


def log_agent_run_data(result: AgentRunResult[T]):
    input_tokens = result.usage().input_tokens
    output_tokens = result.usage().output_tokens
    logger.info(
        f"Agent name: {result.response.model_name}\nTotal cost: {
            result.response.cost()
        }\nTotal tokens used: {
            input_tokens + output_tokens
        }\nInput tokens used: {input_tokens}\nOutput tokens used: {
            output_tokens
        }\nFinal agent output{pformat(result.output)}\nFinish reason: {
            result.response.finish_reason
        }"
    )
