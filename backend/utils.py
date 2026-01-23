from functools import wraps
import time
from typing import Callable, TypeVar

from pydantic_ai import AgentRunResult
from pydantic import BaseModel
from devtools import pformat

from backend.logger import get_logger


_LOG_STRING = """
Agent name: {agent_name}
Model name: {model_name}
Agent provider: {provider_name}
===============================================================
Input tokens used: {input_tokens}\tInput price: {input_price}$
---------------------------------------------------------------
Output tokens used: {output_tokens}\tOutput price: {output_price}$
---------------------------------------------------------------
Total tokens used: {total_tokens}\tTotal price: {total_price}$
===============================================================
Finish reason: {finish_reason}
Final agent output: {final_output}
"""
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


def log_agent_run_data(agent_name: str, result: AgentRunResult[T]):
    input_tokens = result.usage().input_tokens
    output_tokens = result.usage().output_tokens
    costs = result.response.cost()

    d = {
        "agent_name": agent_name,
        "model_name": result.response.model_name,
        "provider_name": result.response.provider_name,
        "input_tokens": input_tokens,
        "input_price": float(costs.input_price),
        "output_tokens": output_tokens,
        "output_price": float(costs.output_price),
        "total_tokens": input_tokens + output_tokens,
        "total_price": float(costs.total_price),
        "final_output": pformat(result.output),
        "finish_reason": result.response.finish_reason,
    }

    logger.info(_LOG_STRING.format_map(d))
