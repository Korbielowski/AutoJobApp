# TODO: If not used, remove openai-agents from dependencies and add normal OpenAI
# TODO: Use async OpenAI class
import asyncio
from typing import TypeVar

import tiktoken
from openai import AsyncOpenAI, AuthenticationError, RateLimitError
from pydantic import BaseModel

from backend.config import settings
from backend.logger import get_logger

BASE_URL = "https://api.llm7.io/v1"
MODEL = "deepseek-r1-0528"
# OPENAI_MODEL = "gpt-5-nano-2025-08-07"
OPENAI_MODEL = "gpt-5-mini-2025-08-07"
TIK = tiktoken.encoding_for_model("gpt-5-")
T = TypeVar("T", bound=BaseModel)
logger = get_logger()


async def send_req_to_llm(
    prompt: str,
    system_prompt: str = "",
    temperature: float = 1,
    use_openai: bool = True,
    model: type[T] | None = None,
    tools: list[str] | None = None,
    retry: int = 3,
) -> str | T:
    response = ""
    logger.debug(
        f"Prompt token count: {len(TIK.encode(system_prompt + prompt))}, temperature: {temperature}, use_openai: {use_openai}, model: {model}, retry: {retry}, tools: {tools}"
    )

    if use_openai:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        while not response and retry > 0:
            try:
                if model:
                    tools = [{"type": tool} for tool in tools] if tools else []
                    response = await client.responses.parse(
                        model=OPENAI_MODEL,
                        input=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt},
                        ],
                        tools=tools,
                        temperature=temperature,
                        text_format=model,
                    )
                    if response and response.output_parsed:
                        return response.output_parsed
                else:
                    response = await client.responses.create(
                        model=OPENAI_MODEL,
                        input=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt},
                        ],
                        tools=tools,
                        temperature=temperature,
                    )
                    if response:
                        return response.output_text
            except RateLimitError as e:
                logger.info(f"LLM error: {e}")
                logger.error("Too many tokens in 1 minute")
                logger.error(f"Response headers: {e.response.headers}")
                # time = (
                #     e.response.headers.get("x-ratelimit-reset-tokens", "")
                #     .replace("m", "m ")
                #     .replace("s", "")
                #     .split(" ")
                # )
                # delay = 0
                #
                # if "m" in time[0]:
                #     delay += int(time.replace("m", "")) * 60
                # # ERROR: Crashes when time is empty string
                # delay += int(time[-1])
                #
                # logger.info(f"Sleeping for: {delay} seconds")
                delay = 10
                await asyncio.sleep(delay)
            except AuthenticationError as e:
                logger.info(f"LLM error: {e}")
            retry -= 1
    else:
        client = AsyncOpenAI(api_key=settings.API_KEY, base_url=BASE_URL)
        try:
            response = await client.responses.create(
                model=MODEL,
                input=prompt,
                # messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
            )
            return response.output_text
        except Exception as e:
            logger.info(f"LLM error: {e}")
    return ""
