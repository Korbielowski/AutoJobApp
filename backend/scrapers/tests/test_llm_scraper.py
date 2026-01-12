import logging

import pytest
from loguru import logger
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from backend.config import settings
from backend.scrapers.llm_scraper import LLMScraper


@pytest.mark.asyncio
@pytest.mark.skip
async def test_is_on_login_page_return_false_when_not_on_login_page(
    get_data_for_scraper,
):
    async with Stealth().use_async(async_playwright()) as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context(locale="en-US")
        page = await context.new_page()
        url = "https://it.pracuj.pl/praca"
        scraper = LLMScraper(
            url=url,
            email=settings.USER_EMAIL,
            password=settings.PASSWORD,
            context=context,
            page=page,
            website_info=None,
        )
        await scraper.page.goto(scraper.url)
        await scraper.page.wait_for_load_state("load")
        assert await scraper._is_on_login_page() is False


@pytest.mark.asyncio
@pytest.mark.skip
async def test_is_on_login_page_return_true_when_on_login_page(
    get_data_for_scraper,
):
    async with Stealth().use_async(async_playwright()) as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context(locale="en-US")
        page = await context.new_page()
        url = "https://it.pracuj.pl/praca"
        scraper = LLMScraper(
            url=url,
            email=settings.USER_EMAIL,
            password=settings.PASSWORD,
            context=context,
            page=page,
            website_info=None,
        )
        await scraper.page.goto(scraper.url)
        await scraper.page.wait_for_load_state("load")
        assert await scraper._is_on_login_page() is True


@pytest.mark.asyncio
@pytest.mark.skip
async def test_navigate_to_login_page(get_data_for_scraper, caplog):
    async with Stealth().use_async(async_playwright()) as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context(locale="en-US")
        page = await context.new_page()
        url = "https://it.pracuj.pl/praca"
        scraper = LLMScraper(
            url=url,
            email=settings.USER_EMAIL,
            password=settings.PASSWORD,
            context=context,
            page=page,
            website_info=None,
        )
        await scraper.page.goto(scraper.url)
        await scraper.page.wait_for_load_state("load")
        with caplog.at_level(logging.ERROR):
            await scraper._navigate_to_login_page()
            assert "Could not find button to login page" not in caplog.text


@pytest.mark.asyncio
@pytest.mark.skip
async def test_loging_to_page(get_data_for_scraper, caplog):
    async with Stealth().use_async(async_playwright()) as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context(locale="en-US")
        page = await context.new_page()
        url = "https://it.pracuj.pl/praca"
        scraper = LLMScraper(
            url=url,
            email=settings.USER_EMAIL,
            password=settings.PASSWORD,
            context=context,
            page=page,
            website_info=None,
        )
        with caplog.at_level(logging.ERROR):
            await scraper.login_to_page()
            assert "Could not log into" not in caplog.text


# @pytest.mark.asyncio
# @pytest.mark.skip
# async def test_get_page_content(get_data_for_scraper, caplog):
#     async with Stealth().use_async(async_playwright()) as playwright:
#         browser = await playwright.chromium.launch(headless=False)
#         context = await browser.new_context(locale="en-US")
#         page = await context.new_page()
#         url = "https://it.pracuj.pl/praca"
#         scraper = LLMScraper(
#             url=url,
#             email=settings.USER_EMAIL,
#             password=settings.PASSWORD,
#             context=context,
#             page=page,
#             website_info=None,
#         )
#         await scraper.page.goto(scraper.url)
#         await scraper.page.wait_for_load_state("load")
#         content = await scraper._get_page_content()
#         logger.info(type(content))
#         assert type(content) is not str


@pytest.mark.asyncio
@pytest.mark.skip
async def test_get_job_entries(get_data_for_scraper):
    async with Stealth().use_async(async_playwright()) as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context(locale="en-US")
        page = await context.new_page()
        url = "https://it.pracuj.pl/praca"
        scraper = LLMScraper(
            url=url,
            email=settings.USER_EMAIL,
            password=settings.PASSWORD,
            context=context,
            page=page,
            website_info=None,
        )
        await scraper.page.goto(scraper.url)
        await scraper.page.wait_for_load_state("load")
        await scraper._pass_cookies_popup()
        job_entries = await scraper.get_job_entries()
        for job in job_entries:
            logger.info(f"Now Scraping: {await job.get_attribute('href')}")
            entry = await scraper._get_job_information(
                await job.get_attribute("href")
            )
            if entry:
                logger.info("Everything works fine for now")
            else:
                logger.error("Something is wrong :(")
        assert type(job_entries) is tuple
        assert len(job_entries) > 0


# @pytest.fixture(
#     scope="module",
# )
# def get_data_for_scraper() -> tuple[UserModel, str, str]:
#     profile = UserModel(
#         firstname="test", middlename="test", surname="test", age="30"
#     )
#     email = "test.test@gmail.com"
#     password = "testTest123"
#     return profile, email, password
