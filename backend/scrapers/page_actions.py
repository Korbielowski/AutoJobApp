import asyncio
import random
from typing import Literal

from playwright.async_api import Page, Error

from backend.config import settings
from backend.database.models import WebsiteModel
from backend.logger import get_logger
from backend.schemas.llm_responses import InputFieldTypeEnum, ToolResult
from backend.scrapers.page_processing import find_html_tag_v2

logger = get_logger()
_action_lock = asyncio.Lock()


async def goto(page: Page, link: str, retry: int = 3) -> None:
    for _ in range(retry):
        try:
            await page.goto(link)
            await page.wait_for_load_state("load")
            logger.info("goto action was successful")
            # await asyncio.sleep(7)
            return
        except TimeoutError:
            logger.exception("Timeout for goto")


async def click(page: Page, text: str) -> ToolResult:
    async with _action_lock:
        try:
            tag = await find_html_tag_v2(page=page, text=text)
        except Error as e:
            logger.error(f"Could not find button, ELEMENT_NOT_FOUND. Because of {e.message}")
            return ToolResult(success=False, error_code="ELEMENT_NOT_FOUND", additional_information=f"{e.name}\n{e.message}")

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
        except TimeoutError:
            logger.error("click call was not successful, TIMEOUT")
            return ToolResult(success=False, error_code="TIMEOUT")


async def fill(
    page: Page,
    text: str,
    input_type: Literal["email", "password"],
    website_info: WebsiteModel,
) -> ToolResult:
    async with _action_lock:
        try:
            tag = await find_html_tag_v2(page=page, text=text)
        except Error as e:
            logger.error(f"Could not find button, ELEMENT_NOT_FOUND. Because of {e.name}")
            return ToolResult(success=False, error_code="ELEMENT_NOT_FOUND", additional_information=f"{e.name}\n{e.message}")

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
            await tag.press_sequentially(
                value, delay=random.randint(2, 12) * 100
            )
            logger.info("fill was successful")
            return ToolResult(success=True)
        except TimeoutError:
            logger.error("fill was not successful, TIMEOUT")
            return ToolResult(success=False, error_code="TIMEOUT")
