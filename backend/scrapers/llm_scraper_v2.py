import asyncio
import datetime
import random
from collections import deque
from dataclasses import dataclass
from enum import StrEnum
from typing import Deque, Literal, Optional

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
    JobEntryResponse,
    TaskState,
)
from backend.schemas.models import JobEntry
from backend.scrapers.base_scraper import BaseScraper
from backend.scrapers.utils import get_page_content, goto

OPENAI_MODEL = "gpt-5-mini-2025-08-07"
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


class InputEnum(StrEnum):
    email = "email"
    password = "password"


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
    :type input_type: InputEnum
    :return: Result of the action
    :rtype: ToolResult
    """
    logger.debug(
        f"'{wrapper.context.agent_name}' invoked 'fill' tool call with params: input_type= {input_type}\nelement= {pformat(element)}"
    )
    tag = await find_html_tag(page=wrapper.context.page, element=element)
    if not tag:
        return ToolResult(success=False, error_code="ELEMENT_NOT_FOUND")

    if input_type == InputEnum.email:
        value = wrapper.context.website_info.user_email
    elif input_type == InputEnum.password:
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
    return ToolResult(
        success=True,
        result=f"url: {wrapper.context.page.url}\npage: {await get_page_content(wrapper.context.page)}",
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


class TrimmingSession(SessionABC):
    def __init__(self, turns: int):
        self.turns = turns
        self._items = Deque[TResponseInputItem] = deque()

    def _trim_messages(
        self, items: list[TResponseInputItem]
    ) -> list[TResponseInputItem]:
        pass

    async def get_items(
        self, limit: int | None = None
    ) -> list[TResponseInputItem]:
        pass

    async def add_items(self, items: list[TResponseInputItem]) -> None:
        if not items:
            return
        self._trim_messages(items)

    async def pop_item(self) -> TResponseInputItem | None:
        return self._items.pop() if self._items else None

    async def clear_session(self) -> None:
        pass


class LLMScraperV2(BaseScraper):
    model = OpenAIResponsesModel(
        model=OPENAI_MODEL,
        openai_client=AsyncOpenAI(api_key=settings.OPENAI_API_KEY),
    )
    # run_config = RunConfig(session_input_callback=)

    async def _agent_loop(self, agent: Agent) -> bool:
        logger.debug(f"Running agent loop for '{agent.name}'")

        start_url = self.page.url
        max_turns = DEFAULT_MAX_TURNS  # TODO: Test what happens if we have too little turns for a given agent
        for _ in range(self.retries):
            try:
                result = await Runner.run(
                    starting_agent=agent,
                    input=await get_page_content(self.page),
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
        return tuple()

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
