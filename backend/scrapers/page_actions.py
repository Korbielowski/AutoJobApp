import asyncio
import random
from typing import Literal

from playwright.async_api import (
    Page,
    TimeoutError as PlaywrightTimeoutError,
    Locator,
)

from backend.config import settings
from backend.database.models import WebsiteModel
from backend.logger import get_logger
from backend.schemas.llm_responses import InputFieldTypeEnum, ToolResult
from backend.schemas.models import Step, HTMLElement
from backend.scrapers.page_processing import (
    find_html_tag_v2,
    read_key_from_mapping_store,
)

logger = get_logger()
_action_lock = asyncio.Lock()


async def goto(page: Page, url: str, retry: int = 3) -> None:
    for _ in range(retry):
        try:
            await page.goto(url)
            await page.wait_for_load_state("load")
            logger.info("goto action was successful")
            await asyncio.sleep(3)
            return
        except PlaywrightTimeoutError:
            logger.exception("Timeout for goto")


async def base_click(tag: Locator | None, page: Page) -> ToolResult:
    if not tag:
        logger.error("Could not find button, ELEMENT_NOT_FOUND")
        return ToolResult(success=False, error_code="ELEMENT_NOT_FOUND")

    try:
        if settings.DEBUG:
            await tag.highlight()
        await tag.click(force=True)
        await page.wait_for_load_state("load")
        logger.info("click call was successful")
        return ToolResult(success=True)
    except PlaywrightTimeoutError:
        logger.error("click call was not successful, TIMEOUT")
        return ToolResult(success=False, error_code="TIMEOUT")


async def click(page: Page, text: str) -> tuple[ToolResult, Step | None]:
    async with _action_lock:
        tag = await find_html_tag_v2(page=page, text=text)
        tool_result = await base_click(tag=tag, page=page)

        if tool_result.success:
            return tool_result, Step(
                function="click",
                tag=await read_key_from_mapping_store(text),
                additional_arguments={},
            )
        else:
            return tool_result, None


async def step_click(element: HTMLElement, page: Page) -> ToolResult:
    tag = await find_html_tag_v2(page=page, text=element)
    tool_result = await base_click(tag=tag, page=page)
    await asyncio.sleep(3)
    return tool_result


async def base_fill(
    tag: Locator | None,
    input_type: Literal["email", "password"],
    website_info: WebsiteModel,
) -> ToolResult:
    if not tag:
        logger.error("Could not find input field, ELEMENT_NOT_FOUND")
        return ToolResult(success=False, error_code="ELEMENT_NOT_FOUND")

    if input_type == InputFieldTypeEnum.email:
        value = website_info.user_email
    elif input_type == InputFieldTypeEnum.password:
        value = website_info.user_password
    else:
        logger.error("fill was not successful, WRONG_INPUT")
        return ToolResult(success=False, error_code="WRONG_INPUT")

    try:
        if settings.DEBUG:
            await tag.highlight()
        await tag.click(force=True)
        await tag.press_sequentially(value, delay=random.randint(2, 12) * 100)
        logger.info("fill was successful")
        return ToolResult(success=True)
    except PlaywrightTimeoutError:
        logger.error("fill was not successful, TIMEOUT")
        return ToolResult(success=False, error_code="TIMEOUT")


async def fill(
    page: Page,
    text: str,
    input_type: Literal["email", "password"],
    website_info: WebsiteModel,
) -> tuple[ToolResult, Step | None]:
    async with _action_lock:
        tag = await find_html_tag_v2(page=page, text=text)
        tool_result = await base_fill(
            tag=tag, input_type=input_type, website_info=website_info
        )

        if tool_result.success:
            return tool_result, Step(
                function="fill",
                tag=await read_key_from_mapping_store(text),
                additional_arguments={"input_type": input_type},
            )
        else:
            return tool_result, None


async def step_fill(
    page: Page,
    element: HTMLElement,
    input_type: Literal["email", "password"],
    website_info: WebsiteModel,
) -> ToolResult:
    tag = await find_html_tag_v2(page=page, text=element)
    return await base_fill(
        tag=tag, input_type=input_type, website_info=website_info
    )
