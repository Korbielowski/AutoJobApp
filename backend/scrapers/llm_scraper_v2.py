import asyncio
import datetime
import random
from collections import deque
from copy import deepcopy
from dataclasses import dataclass
from typing import Deque, Literal, Optional

import tiktoken
import toon
from agents import (
    Agent,
    MaxTurnsExceeded,
    OpenAIResponsesModel,
    RunContextWrapper,
    RunErrorDetails,
    Runner,
    RunResult,
    SessionABC,
    TResponseInputItem,
    function_tool,
)
from agents.run import DEFAULT_MAX_TURNS
from devtools import pformat
from openai import AsyncOpenAI
from playwright.async_api import Locator, Page
from pydantic import BaseModel

from backend.config import settings
from backend.database.models import WebsiteModel
from backend.llm.llm import send_req_to_llm
from backend.llm.prompts import load_prompt
from backend.logger import get_logger
from backend.schemas.llm_responses import (
    HTMLElement,
    InputFieldTypeEnum,
    JobEntryResponse,
    TaskState,
)
from backend.schemas.models import JobEntry
from backend.scrapers.base_scraper import BaseScraper
from backend.scrapers.utils import get_page_content, goto

TOOL_CALL_TYPE = "function_call"
TOOL_RESPONSE_TYPE = "function_call_output"
OPENAI_MODEL = "gpt-5-mini-2025-08-07"
TIK = tiktoken.encoding_for_model("gpt-5-")
logger = get_logger()


@dataclass
class ContextForLLM:
    page: Page
    website_info: WebsiteModel
    agent_name: str


class ToolResult(BaseModel):
    success: bool
    result: Optional[str] = None
    error_code: Optional[
        Literal["ELEMENT_NOT_FOUND", "TIMEOUT", "NOT_VISIBLE", "WRONG_INPUT"]
    ] = None


async def find_html_tag(page: Page, element: HTMLElement) -> Locator | None:
    locator = None

    if element.id:
        logger.warning(f"{element.id=}")
        locator = page.locator(f"#{element.id}")
        count = await locator.count()

        if 0 < count < 2:
            return locator.last
        logger.error(f"Count: {count}")

    if element.role:
        logger.warning(f"{element.role=}")
        if locator and await locator.count() >= 2:
            locator = locator.and_(page.get_by_role(element.role, exact=True))
        else:
            locator = page.get_by_role(element.role, exact=True)

        count = await locator.count()
        if 0 < count < 2:
            return locator.last
        logger.error(f"Count: {count}")

    if element.text:
        logger.warning(f"{element.text=}")
        if locator and await locator.count() >= 2:
            locator = locator.and_(page.get_by_text(element.text, exact=True))
        else:
            locator = page.get_by_text(element.text, exact=True)

        count = await locator.count()
        if 0 < count < 2:
            return locator.last
        logger.error(f"Count: {count}")

    if element.aria_label:
        logger.warning(f"{element.aria_label=}")
        if locator and await locator.count() >= 2:
            locator = locator.and_(
                page.get_by_label(element.aria_label, exact=True)
            )
        else:
            locator = page.get_by_label(element.aria_label, exact=True)
        count = await locator.count()
        if 0 < count < 2:
            return locator.last
        logger.error(f"Count: {count}")

    if element.name:
        logger.warning(f"{element.name=}")
        if locator and await locator.count() >= 2:
            locator = locator.and_(page.locator(f'[name="{element.name}"]'))
        else:
            locator = page.locator(f'[name="{element.name}"]')
        count = await locator.count()
        if 0 < count < 2:
            return locator.last
        logger.error(f"Count: {count}")

    if element.placeholder:
        logger.warning(f"{element.placeholder=}")
        if locator and await locator.count() >= 2:
            locator = locator.and_(
                page.get_by_placeholder(element.placeholder, exact=True)
            )
        else:
            locator = page.get_by_placeholder(element.placeholder, exact=True)

        count = await locator.count()
        if 0 < count < 2:
            return locator.last
        logger.error(f"Count: {count}")

    if element.element_type:
        logger.warning(f"{element.element_type=}")
        if locator and await locator.count() >= 2:
            locator = locator.and_(
                page.locator(f'[type="{element.element_type}"]')
            )
        else:
            locator = page.locator(f'[type="{element.element_type}"]')

        count = await locator.count()
        if 0 < count < 2:
            return locator.last
        logger.error(f"Count: {count}")

    # FIXME: playwright._impl._errors.Error: Locator.count: SyntaxError: Failed to execute 'querySelectorAll' on 'Document': '.tw-w-[120px]' is not a valid selector.
    if element.class_list:
        class_selector = f".{'.'.join(element.class_list)}"
        logger.warning(f"{element.class_list=}, {class_selector}")
        if locator and await locator.count() >= 2:
            locator = locator.and_(page.locator(class_selector))
        else:
            locator = page.locator(class_selector)
        count = await locator.count()
        if 0 < count < 2:
            return locator.last
        logger.error(f"Count: {count}")

    if locator:  # TODO: Add step where LLM selects from multiple elements, if code above could not select single one element
        return locator.last

    return locator


@function_tool
async def click(
    wrapper: RunContextWrapper[ContextForLLM], element: HTMLElement
) -> ToolResult:
    """
    Click a given element on the page.
    :param element: Element to click
    :type element: HTMLElement
    :return: Result of the click action
    :rtype: ToolResult
    """
    logger.debug(
        f"'{wrapper.context.agent_name}' invoked 'click' tool call with params: element=\n{pformat(element)}"
    )
    tag = await find_html_tag(page=wrapper.context.page, element=element)
    if not tag:
        return ToolResult(success=False, error_code="ELEMENT_NOT_FOUND")

    try:
        await tag.highlight()
        await asyncio.sleep(3)
        await tag.click()
        # await page.wait_for_load_state("load")
        await asyncio.sleep(3)
    except TimeoutError:
        return ToolResult(success=False, error_code="TIMEOUT")
    return ToolResult(success=True)


@function_tool
async def fill(
    wrapper: RunContextWrapper[ContextForLLM],
    element: HTMLElement,
    input_type: Literal["email", "password"],
) -> ToolResult:
    """
    Fill a given input field.
    :param element: Input field to fill
    :type element: HTMLElement
    :param input_type: Whether the input, that should be passed to input filed should be user email or password. Password and email will be read from database by function.
    :type input_type: InputFieldTypeEnum
    :return: Result of the action
    :rtype: ToolResult
    """
    logger.debug(
        f"'{wrapper.context.agent_name}' invoked 'fill' tool call with params: input_type= {input_type}\nelement= {pformat(element)}"
    )
    tag = await find_html_tag(page=wrapper.context.page, element=element)
    if not tag:
        return ToolResult(success=False, error_code="ELEMENT_NOT_FOUND")

    if input_type == InputFieldTypeEnum.email:
        value = wrapper.context.website_info.user_email
    elif input_type == InputFieldTypeEnum.password:
        value = wrapper.context.website_info.user_password
    else:
        return ToolResult(success=False, error_code="WRONG_INPUT")

    try:
        await tag.highlight()
        await asyncio.sleep(3)
        await tag.press_sequentially(value, delay=random.randint(5, 10) * 100)
    except TimeoutError:
        return ToolResult(success=False, error_code="TIMEOUT")
    return ToolResult(success=True)


@function_tool
async def get_page_data(
    wrapper: RunContextWrapper[ContextForLLM],
) -> ToolResult:
    """
    Get data about all page HTML elements in a simplified form of JSON and page url
    :return: Page elements in JSON-like form and url
    :rtype: ToolResult
    """
    logger.debug(
        f"'{wrapper.context.agent_name}' invoked 'get_page_data' tool call"
    )
    tag_list = await get_page_content(wrapper.context.page)
    # FIXME: openai.BadRequestError: Error code: 400 - {'error': {'message': 'Your input exceeds the context window of this model. Please adjust your input and try again.', 'type': 'invalid_request_error', 'param': 'input', 'code': 'context_length_exceeded'}}

    processed_tag_list: list[dict] = []
    for tag in tag_list:
        x: dict = deepcopy(tag)
        x.pop("parents")
        processed_tag_list.append(x)

    for index, tag in enumerate(processed_tag_list):
        if not tag.get("text"):
            processed_tag_list.pop(index)
        else:
            processed_text = tag.get("text", "")
            if len(processed_text) >= 100:
                processed_text = processed_text[0:101] + "..."
            processed_tag_list[index] = {"text": processed_text}

    logger.warning(
        f"New new way: {len(TIK.encode(toon.encode(processed_tag_list)))}"
    )

    return ToolResult(
        success=True,
        result=f"url: {wrapper.context.page.url}\npage elements representation: {toon.encode(processed_tag_list)}",
    )


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
    model = OpenAIResponsesModel(
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
            tools=[click, fill, get_page_data],
            model=self.model,
            output_type=TaskState,
        )

        await self._agent_loop(login_agent)

    async def navigate_to_job_listing_page(self) -> None:
        job_list_page_agent = Agent(
            name="job_list_page_agent",
            instructions=await load_prompt(
                "scraping:system:navigate_to_job_listing_page"
            ),
            tools=[click, get_page_data],
            model=self.model,
            output_type=TaskState,
        )

        await self._agent_loop(job_list_page_agent)

    async def get_job_entries(self) -> tuple[Locator, ...]:
        element = await send_req_to_llm(
            system_prompt=await load_prompt("scraping:user:job_offer_links"),
            prompt=await get_page_content(self.page),
            model=HTMLElement,
        )
        if element.class_list:
            class_selector = f".{'.'.join(element.class_list)}"
            locator = self.page.locator(class_selector)
            logger.warning(f"Locator count: {await locator.count()}")
            logger.warning(await locator.all())
            # for loc in await locator.all():
            #     try:
            #         url = await loc.get_attribute("href")
            #         logger.success(url)
            #     except TimeoutError:
            #         logger.error("Could not get href")
            return tuple(await locator.all())
        logger.warning("Could not find link locators")
        return tuple()

    async def navigate_to_next_page(self) -> bool:
        next_page_agent = Agent(
            name="next_page_agent",
            instructions=await load_prompt("scraping:system:next_page_button"),
            tools=[click, get_page_data],
            model=self.model,
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
