import datetime
from typing import Any, AsyncGenerator

from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from sqlmodel import Session

from backend.career_documents.pdf import (
    generate_career_documents,
)
from backend.database.models import CVCreationModeEnum, UserModel
from backend.logger import get_logger
from backend.scrapers.llm_scraper import LLMScraper

logger = get_logger()


async def find_job_entries(
    user: UserModel,
    session: Session,
    websites,
    cv_creation_mode: CVCreationModeEnum,
    generate_cover_letter: bool,
    retries: int,
    # auto_apply: bool,
) -> AsyncGenerator[str, Any]:
    if not websites:
        yield "data:null\n\n"

    async with Stealth().use_async(async_playwright()) as playwright:
        # TODO: Add ability for users to choose their preferred browser, recommend and default to chromium
        browser = await playwright.chromium.launch(headless=False)
        # TODO: Move code below to the for loop
        context = await browser.new_context(locale="en-US")
        # context.add_cookies()
        page = await context.new_page()

        for website in websites:
            logger.info(website)
            scraper = LLMScraper(
                url=website.url,
                email=website.user_email,
                password=website.user_password,
                context=context,
                page=page,
                website_info=website,
                retries=retries,
            )
            await scraper.login_to_page()

            running = True
            while running:
                for job in await scraper.get_job_entries():
                    job_data = await scraper.process_and_evaluate_job(job)
                    if job_data:
                        job_entry_model = await generate_career_documents(
                            user=user,
                            session=session,
                            job_entry=job_data,
                            current_time=datetime.datetime.today().strftime(
                                "%Y-%m-%d_%H:%M:%S"
                            ),
                            cv_creation_mode=cv_creation_mode,
                            generate_cover_letter=generate_cover_letter,
                        )
                        yield f"data:{job_entry_model.model_dump_json()}\n\n"
                running = await scraper.navigate_to_next_page()


__all__ = ["find_job_entries"]
