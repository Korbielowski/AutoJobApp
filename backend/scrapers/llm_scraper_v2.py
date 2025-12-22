import asyncio
import random
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal, Optional

from agents import (
    Agent,
    OpenAIResponsesModel,
    RunConfig,
    RunContextWrapper,
    Runner,
    RunResult,
    TResponseInputItem,
    function_tool,
)
from openai import AsyncOpenAI
from playwright.async_api import Locator, Page
from pydantic import BaseModel

from backend.config import settings
from backend.database.models import WebsiteModel
from backend.llm.prompts import load_prompt
from backend.logger import get_logger
from backend.schemas.llm_responses import HTMLElement, TaskState
from backend.schemas.models import JobEntry
from backend.scrapers.base_scraper import BaseScraper
from backend.scrapers.utils import get_page_content, goto

OPENAI_MODEL = "gpt-5-mini-2025-08-07"
logger = get_logger()


@dataclass
class ContextForLLM:
    page: Page
    website_info: WebsiteModel


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
        logger.info(element.id)
        locator = page.locator(f"#{element.id}")
        count = await locator.count()
        if 0 < count < 2:
            return locator.last

    if element.role:
        if locator and await locator.count() >= 2:
            locator = locator.and_(page.get_by_role(element.role, exact=True))
        else:
            locator = page.get_by_role(element.role, exact=True)

        count = await locator.count()
        if 0 < count < 2:
            return locator.last

    if element.text:
        if locator and await locator.count() >= 2:
            locator = locator.and_(page.get_by_text(element.text, exact=True))
        else:
            locator = page.get_by_text(element.text, exact=True)

        count = await locator.count()
        if 0 < count < 2:
            return locator.last

    if element.aria_label:
        if locator and await locator.count() >= 2:
            locator = locator.and_(
                page.get_by_label(element.aria_label, exact=True)
            )
        else:
            locator = page.get_by_label(element.aria_label, exact=True)
        count = await locator.count()
        if 0 < count < 2:
            return locator.last

    if element.name:
        if locator and await locator.count() >= 2:
            locator = locator.and_(page.locator(f'[name="{element.name}"]'))
        else:
            locator = page.locator(f'[name="{element.name}"]')
        count = await locator.count()
        if 0 < count < 2:
            return locator.last

    if element.placeholder:
        if locator and await locator.count() >= 2:
            locator = locator.and_(
                page.get_by_placeholder(element.placeholder, exact=True)
            )
        else:
            locator = page.get_by_placeholder(element.placeholder, exact=True)

        count = await locator.count()
        if 0 < count < 2:
            return locator.last

    if element.element_type:
        if locator and await locator.count() >= 2:
            locator = locator.and_(
                page.locator(f'[type="{element.element_type}"]')
            )
        else:
            locator = page.locator(f'[type="{element.element_type}"]')

        count = await locator.count()
        if 0 < count < 2:
            return locator.last

    # FIXME: playwright._impl._errors.Error: Locator.count: SyntaxError: Failed to execute 'querySelectorAll' on 'Document': '.tw-w-[120px]' is not a valid selector.
    if element.class_list:
        class_selector = f".{'.'.join(element.class_list)}"
        if locator and await locator.count() >= 2:
            locator = locator.and_(page.locator(class_selector))
        else:
            locator = page.locator(class_selector)
        count = await locator.count()
        if 0 < count < 2:
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
    Get data about all page HTML elements in a simplified form of JSON
    :return: Page elements in JSON form
    :rtype: ToolResult
    """
    return ToolResult(
        success=True, result=await get_page_content(wrapper.context.page)
    )


def _log_agent_data(result: RunResult):
    logger.info(
        f"Total tokens used: {
            result.context_wrapper.usage.total_tokens
        }\nInput tokens used: {
            result.context_wrapper.usage.input_tokens
        }\nOutput tokens used: {result.context_wrapper.usage.output_tokens}"
    )


class CouldNotLoginException(Exception):
    pass


async def _session_input() -> TResponseInputItem:
    pass


class LLMScraperV2(BaseScraper):
    async def login_to_page(self) -> None:
        await goto(self.page, self.url)

        for _ in range(self.retries):
            login_agent = Agent(
                name="login_agent",
                instructions=await load_prompt("scraping:system:login_to_page"),
                tools=[click, fill, get_page_data],
                model=OpenAIResponsesModel(
                    model=OPENAI_MODEL,
                    openai_client=AsyncOpenAI(api_key=settings.OPENAI_API_KEY),
                ),  # TODO: Maybe move this to constructor
                output_type=TaskState,
            )
            result = await Runner.run(
                starting_agent=login_agent,
                input=await get_page_content(self.page),
                context=ContextForLLM(
                    page=self.page, website_info=self.website_info
                ),
                run_config=RunConfig(session_input_callback=_session_input),
            )
            _log_agent_data(result)
            if (
                result.final_output.state == "done"
                and result.final_output.confidence >= 0.8
            ):
                return
            logger.error(
                f"Could not log into the: {self.website_info.url}. After this many attempts: {self.retries}"
            )
            raise CouldNotLoginException(
                f"Could not log into the: {self.website_info.url}. After this many attempts: {self.retries}"
            )

    async def _navigate_to_job_list_page(self) -> None:
        pass

    async def get_job_entries(self) -> tuple[Locator, ...]:
        pass

    async def navigate_to_next_page(self) -> bool:
        pass

    async def _go_to_next_job(self) -> bool:
        pass

    async def _apply_for_job(self):
        pass

    async def _get_job_information(self, url: str) -> JobEntry | None:
        pass
