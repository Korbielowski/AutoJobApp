import pytest
from agents.tool_context import ToolContext
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from backend.database.models import WebsiteModel
from backend.logger import get_logger
from backend.scrapers.llm_scraper_v2 import ContextForLLM, get_page_data
from backend.scrapers.page_actions import goto

logger = get_logger()


@pytest.mark.asyncio
@pytest.mark.skip
async def test_get_page_data():
    async with Stealth().use_async(async_playwright()) as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context(locale="en-US")
        page = await context.new_page()
        url = "https://www.linkedin.com/checkpoint/rm/sign-in-another-account?fromSignIn=true"
        await goto(page, url)
        result = await get_page_data.on_invoke_tool(
            ToolContext(
                context=ContextForLLM(
                    page=page,
                    website_info=WebsiteModel(),
                    agent_name="login_agent",
                ),
                tool_name="dummy",
                tool_call_id="1",
            ),
            "",
        )
        logger.info(result)
