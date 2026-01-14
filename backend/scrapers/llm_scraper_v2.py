import asyncio
import datetime
from collections import deque
from typing import Deque

import tiktoken
from agents import (
    Agent,
    MaxTurnsExceeded,
    OpenAIResponsesModel,
    RunErrorDetails,
    Runner,
    RunResult,
    SessionABC,
    TResponseInputItem,
)
from agents.run import DEFAULT_MAX_TURNS
from devtools import pformat
from openai import AsyncOpenAI
from playwright.async_api import Locator, Page

from backend.config import settings
from backend.llm.llm import send_req_to_llm
from backend.llm.prompts import load_prompt
from backend.logger import get_logger
from backend.schemas.llm_responses import (
    ContextForLLM,
    JobEntryResponse,
    TaskState,
    TextResponse,
)
from backend.schemas.models import JobEntry
from backend.scrapers.base_scraper import BaseScraper
from backend.scrapers.page_actions import goto
from backend.scrapers.page_processing import (
    get_page_content,
    read_key_from_mapping_store,
)
from backend.scrapers.tools import click_element, fill_element, get_page_data

TOOL_CALL_TYPE = "function_call"
TOOL_RESPONSE_TYPE = "function_call_output"
OPENAI_MODEL = "gpt-5-mini-2025-08-07"
TIK = tiktoken.encoding_for_model("gpt-5-")
logger = get_logger()


def _log_agent_run_data(result: RunResult | RunErrorDetails | None):
    if isinstance(result, RunResult):
        logger.info(
            f"Agent name: {
                result.context_wrapper.context.agent_name
            }\nTotal tokens used: {
                result.context_wrapper.usage.total_tokens
            }\nInput tokens used: {
                result.context_wrapper.usage.input_tokens
            }\nOutput tokens used: {
                result.context_wrapper.usage.output_tokens
            }\nFinal agent output{pformat(result.final_output)}"
        )
    elif isinstance(result, RunErrorDetails):
        logger.error(
            f"Agent name: {
                result.context_wrapper.context.agent_name
            }\nTotal tokens used: {
                result.context_wrapper.usage.total_tokens
            }\nInput tokens used: {
                result.context_wrapper.usage.input_tokens
            }\nOutput tokens used: {result.context_wrapper.usage.output_tokens}"
        )


def _is_tool_call_or_result(item: TResponseInputItem) -> bool:
    if isinstance(item, dict):
        t = item.get("type", "")
        return t == TOOL_CALL_TYPE or t == TOOL_RESPONSE_TYPE
    t = getattr(item, "type", "")
    return t == TOOL_CALL_TYPE or t == TOOL_RESPONSE_TYPE


class TrimmingSession(SessionABC):
    def __init__(self, turns: int):
        self.turns = max(1, turns)
        self._items: Deque[TResponseInputItem] = deque()
        self._lock = asyncio.Lock()

    def _trim_messages(
        self, items: list[TResponseInputItem]
    ) -> list[TResponseInputItem]:
        if not items:
            return items

        count = 0
        start_idx = 0

        for i in range(len(items) - 1, -1, -1):
            if _is_tool_call_or_result(items[i]):
                count += 1
                if count == self.turns:
                    start_idx = i
                    break

        return items[start_idx:]

    async def get_items(
        self, limit: int | None = None
    ) -> list[TResponseInputItem]:
        async with self._lock:
            trimmed = self._trim_messages(list(self._items))
            return (
                trimmed[-limit:]
                if (limit is not None and limit >= 0)
                else trimmed
            )

    async def add_items(self, items: list[TResponseInputItem]) -> None:
        if not items:
            return
        async with self._lock:
            self._items.extend(items)
            trimmed = self._trim_messages(list(self._items))
            self._items.clear()
            self._items.extend(trimmed)

    async def pop_item(self) -> TResponseInputItem | None:
        async with self._lock:
            return self._items.pop() if self._items else None

    async def clear_session(self) -> None:
        async with self._lock:
            self._items.clear()


class LLMScraperV2(BaseScraper):
    _model = OpenAIResponsesModel(
        model=OPENAI_MODEL,
        openai_client=AsyncOpenAI(api_key=settings.OPENAI_API_KEY),
    )
    # run_config = RunConfig(session_input_callback=)

    async def _agent_loop(self, agent: Agent) -> bool:
        logger.debug(f"Running agent loop for '{agent.name}'")

        start_url = self.page.url
        max_turns = (
            DEFAULT_MAX_TURNS + 5
        )  # TODO: Test what happens if we have too little turns for a given agent
        for _ in range(self.retries):
            try:
                result = await Runner.run(
                    starting_agent=agent,
                    input="",
                    session=TrimmingSession(turns=2),
                    context=ContextForLLM(
                        page=self.page,
                        website_info=self.website_info,
                        agent_name=agent.name,
                    ),
                    max_turns=max_turns,
                    # run_config=self.run_config,
                )
                _log_agent_run_data(result)
            except MaxTurnsExceeded as e:
                logger.error(
                    f"Agent '{agent.name}' could not finish task, {max_turns=}"
                )
                _log_agent_run_data(e.run_data)
                max_turns += 5
                await goto(page=self.page, link=start_url)
                continue

            if result.final_output.state == "done":
                return True
            elif result.final_output.state == "failed":
                return False
        return False

    async def login_to_page(self) -> None:
        await goto(self.page, self.url)

        login_agent = Agent(
            name="login_agent",
            instructions=await load_prompt("scraping:system:login_to_page"),
            tools=[click_element, fill_element, get_page_data],
            model=self._model,
            output_type=TaskState,
        )

        await self._agent_loop(login_agent)

    async def navigate_to_job_listing_page(self) -> None:
        job_list_page_agent = Agent(
            name="job_list_page_agent",
            instructions=await load_prompt(
                "scraping:system:navigate_to_job_listing_page"
            ),
            tools=[click_element, get_page_data],
            model=self._model,
            output_type=TaskState,
        )

        await self._agent_loop(job_list_page_agent)

    async def get_job_entries(self) -> tuple[Locator, ...]:
        for _ in range(3):
            text = await send_req_to_llm(
                system_prompt=await load_prompt(
                    "scraping:system:job_offer_links"
                ),
                prompt=await get_page_content(self.page),
                model=TextResponse,
            )
            logger.debug(f"This was chosen: {pformat(text)}")
            tag = await read_key_from_mapping_store(text.text)
            if not tag.class_list:
                continue
            class_selector = f".{'.'.join(tag.class_list)}"
            locator = self.page.locator(class_selector)
            logger.debug(f"Locator count: {await locator.count()}")
            logger.debug(pformat(await locator.all()))
            return tuple(await locator.all())
        logger.warning("Could not find link locators")
        return tuple()

    async def navigate_to_next_page(self) -> bool:
        next_page_agent = Agent(
            name="next_page_agent",
            instructions=await load_prompt("scraping:system:next_page_button"),
            tools=[click_element, get_page_data],
            model=self._model,
            output_type=TaskState,
        )

        return await self._agent_loop(next_page_agent)

    async def _apply_for_job(self):
        pass

    async def _get_job_information(self, url: str) -> JobEntry | None:
        job_page: Page = await self.context.new_page()
        await goto(job_page, url)

        response = await send_req_to_llm(
            prompt=await load_prompt(
                prompt_path="scraping:user:job_offer_info",
                page=await get_page_content(job_page),
            ),
            use_openai=True,
            model=JobEntryResponse,
        )

        attributes = response.model_dump()
        attributes["discovery_date"] = datetime.date.today()
        attributes["job_url"] = url

        await job_page.close()

        try:
            job_entry = JobEntry.model_validate(attributes)
            logger.info(f"JobEntry model data: {pformat(job_entry)}")
            return job_entry
        except Exception as e:
            logger.exception(e)
        return None
