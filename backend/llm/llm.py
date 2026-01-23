from typing import TypeVar, Sequence

from pydantic_ai import (
    Agent,
    UsageLimits,
    UnexpectedModelBehavior,
    UsageLimitExceeded,
)
from pydantic_ai.builtin_tools import AbstractBuiltinTool
from pydantic import BaseModel

from backend.logger import get_logger
from backend.utils import log_agent_run_data

# BASE_URL = "https://api.llm7.io/v1"
# MODEL = "deepseek-r1-0528"
T = TypeVar("T", bound=BaseModel)
logger = get_logger()


class LLMRequestError(Exception):
    pass


async def send_req_to_llm(
    prompt: str,
    response_type: type[T],
    model,
    *,
    system_prompt: str = "",
    agent_name: str = "",
    temperature: float = 1,
    tools: Sequence[AbstractBuiltinTool] | None = None,
    retries: int = 3,
) -> T:
    if tools:
        agent = Agent(
            name="",
            model=model,
            output_type=response_type,
            builtin_tools=tools,
            system_prompt=system_prompt,
        )
    else:
        agent = Agent(
            name="",
            model=model,
            output_type=response_type,
            system_prompt=system_prompt,
        )

    causes = []
    for _ in range(1, retries + 1):
        try:
            result = await agent.run(
                user_prompt=prompt,
                usage_limits=UsageLimits(request_limit=1),
            )
            log_agent_run_data(agent_name, result)
            return result.output
        except (UnexpectedModelBehavior, UsageLimitExceeded) as e:
            logger.exception(
                f"Error occurred: {e}\nCause: {e.__cause__}\nRun {_} of {retries}"
            )
            causes.append(e.__cause__)

    raise LLMRequestError(
        f"Could not get response from LLM, probable causes after {retries} retries: {causes}"
    )
