import asyncio
import datetime

from devtools import pformat
from playwright.async_api import Locator, Page, TimeoutError

from backend.llm.llm import send_req_to_llm
from backend.llm.prompts import load_prompt
from backend.logger import get_logger
from backend.schemas.llm_responses import JobEntryResponse, StateOutput
from backend.scrapers.base_scraper import BaseScraper, JobEntry
from backend.scrapers.utils import (
    click,
    fill,
    find_html_element,
    find_html_element_attributes,
    get_page_content,
    goto,
)

logger = get_logger()


# TODO: Add try except blocks to all operations that can timeout
# TODO: Save all important information about the pages in database (e.g. links, buttons, fields, scrollbars)
# for later use, so that we don't make so many requests to LLM if we already know certain page.
# If saved information does not work at any stage of the process, switch back to LLM scraper and update adequate steps in database
class LLMScraper(BaseScraper):
    async def login_to_page(self) -> None:
        await goto(self.page, self.url)

        await self._pass_cookies_popup()
        await self._navigate_to_login_page()

        email_field_locator, _, _ = await find_html_element(
            self.page, await load_prompt("scraping:user:email_field")
        )
        await fill(email_field_locator, self.email)

        password_field_locator, _, _ = await find_html_element(
            self.page, await load_prompt("scraping:user:password_field")
        )
        if not password_field_locator:
            sign_in_btn_locator, _, _ = await find_html_element(
                self.page, await load_prompt("scraping:user:next_login_page")
            )
            await click(sign_in_btn_locator, self.page)

            password_field_locator, _, _ = await find_html_element(
                self.page, await load_prompt("scraping:user:password_field")
            )
        await fill(password_field_locator, self.password)

        sign_in_btn_locator, _, _ = await find_html_element(
            self.page,
            await load_prompt("scraping:user:sign_in_button"),
            additional_llm=True,
        )
        await click(sign_in_btn_locator, self.page)

    async def _is_on_login_page(self) -> bool:
        # if (
        #     "login" in url
        #     or "signin" in url
        #     or "sign-in" in url
        #     or "sign_in" in url
        # ):
        #     return True
        state = await send_req_to_llm(
            prompt=await load_prompt(
                prompt_path="scraping:user:is_login_page",
                url=self.page.url,
                page=await get_page_content(self.page),
            ),
            use_openai=True,
            model=StateOutput,
        )
        return state.state

    async def _navigate_to_login_page(self) -> None:
        retry = 0
        attribute_list = []

        while not await self._is_on_login_page() and retry < 5:
            if not attribute_list:
                prompt = await load_prompt(
                    "scraping:user:navigate_to_login_page"
                )
            else:
                prompt = await load_prompt(
                    "scraping:user:navigate_to_login_page_with_params",
                    attribute_list=attribute_list,
                )

            btn, attributes, _ = await find_html_element(
                page=self.page, prompt=prompt
            )
            attribute_list.append(attributes)

            await click(btn, self.page)
            retry += 1

    async def _check_if_popup_exists(self) -> bool:
        retry = 0
        while retry < 3:
            state = await send_req_to_llm(
                prompt=await load_prompt(
                    "scraping:user:check_if_popup_exists", page=self.page
                ),
                use_openai=True,
                model=StateOutput,
            )
            if state.state:
                return True
            retry += 1
        return False

    async def _pass_cookies_popup(self) -> None:
        if not await self._check_if_popup_exists():
            return

        retry = 0
        passed = False
        while not passed and retry < 5:
            btn, attribute, attribute_type = await find_html_element(
                self.page, "scraping:user:cookies_button"
            )
            passed = await click(btn, self.page)
            retry += 1

        # cookies_steps = self.website_info.automation_steps.pass_cookies_popup
        # TODO: Try using cookies to avoid popups
        # if cookies_steps:
        #     btn = await get_locator(self.page, cookies_steps[0])
        #     if await click(btn, self.page):
        #         return
        # btn, attribute, attribute_type = await find_html_element(
        #     self.page,
        #     "Find button responsible for accepting website cookies",
        # )
        # await click(btn, self.page)
        #
        # step = Step(
        #     action=click,
        #     html_element_attribute=attribute,
        #     attribute_type=attribute_type,
        #     arguments={},
        # )
        #
        # self.website_info.automation_steps.pass_cookies_popup = [step]

    async def _remove_any_popup(self) -> None:
        if not await self._check_if_popup_exists():
            return

        retry = 0
        passed = False
        while not passed and retry < 5:
            btn, attribute, attribute_type = await find_html_element(
                self.page, await load_prompt("scraping:user:popup_button")
            )
            passed = await click(btn, self.page)
            retry += 1

    async def _is_on_job_list_page(self) -> bool:
        state = await send_req_to_llm(
            prompt=await load_prompt(
                prompt_path="scraping:user:is_job_listing_page",
                url=self.page.url,
                page=await get_page_content(self.page),
            ),
            use_openai=True,
            model=StateOutput,
        )
        return state.state

    async def _navigate_to_job_list_page(self) -> None:
        logger.info("Navigating to job listing page")
        retry = 0
        attribute_list = []

        while not await self._is_on_job_list_page() and retry < 5:
            logger.info(f"Navigation step: {retry}")
            if not attribute_list:
                prompt = await load_prompt(
                    "scraping:user:job_listing_page_button"
                )
            else:
                prompt = await load_prompt(
                    "scraping:user:job_listing_page_button_with_params",
                    attribute_list=attribute_list,
                )

            btn, attributes, _ = await find_html_element(
                page=self.page, prompt=prompt
            )
            attribute_list.append(attributes)

            await click(btn, self.page)
            retry += 1

        if retry >= 5:
            logger.error("Could not get to job listing page")
            return
        logger.info("Navigation to job listing page ended")

    async def get_job_entries(self) -> tuple[Locator, ...]:
        await self._remove_any_popup()

        await self._navigate_to_job_list_page()

        bottom_element, _, _ = await find_html_element(
            self.page, await load_prompt("scraping:user:footer")
        )

        if bottom_element:
            try:
                await bottom_element.scroll_into_view_if_needed()  # TODO: Scroll to this element, but in the way that only a few of entries are loaded at a given time
                logger.info(
                    "Scrolling to element using scroll_into_view_if_needed method"
                )
            except TimeoutError:
                retry = 0
                while not await bottom_element.is_visible() and retry < 100:
                    await self.page.mouse.wheel(0, 500)
                    logger.info(
                        f"Scrolling to element using while loop. is_visible: {await bottom_element.is_visible()}, retry: {retry}"
                    )
                    await asyncio.sleep(0.5)
                    retry += 1
                if not await bottom_element.is_visible():
                    logger.exception(
                        "Element at the bottom of the page is not visible and it cannot be scrolled to"
                    )
                    # TODO: Make use of scrollbar if possible
                    # scrollbar, _, _ = await find_html_element(
                    #     self.page,
                    #     "Find a scrollbar element that is able to scroll to the bottom of the page",
                    # )
                    await self.page.keyboard.press("End")
                    logger.info(
                        "Scrolling to the bottom of the page using 'End' key"
                    )
        else:
            logger.exception(
                "Could not find an element that is at the bottom of the page"
            )
            await self.page.keyboard.press("End")
            logger.info("Scrolled to bottom of the page using 'End' key")

        # TODO: Add some verification for this types of lines as the one below
        prompt = await load_prompt("scraping:user:job_offer_links")
        # prompt = "Find an element that is responsible for holding job offer tile",
        attributes = await find_html_element_attributes(
            page=self.page,
            prompt=prompt,
        )
        if not attributes:
            logger.exception(
                "Cannot find attributes that would enable scraper to find job entries"
            )
            return tuple()

        class_list = attributes.class_list
        if not class_list:
            logger.error("Did not find class_list for selecting job tiles")
            return tuple()
        logger.info("We are going to select job tiles")

        class_selector = f".{'.'.join(class_list)}"
        logger.info(f"{class_selector=}")
        locator = self.page.locator(class_selector)

        job_entry_links = [
            await z.get_attribute("href") for z in await locator.all()
        ]
        # TODO: Add check for None inside of job_entry_links
        logger.info(
            f"Do those classes CSS classes: {class_list} select only job offers and no other elements. Return 'True' if only jobs are selected and 'False' if {class_list} CSS classes select also other elements. {'\n'.join(job_entry_links)}"
        )
        # response = await send_req_to_llm(
        #     f"Do those classes CSS classes: {class_list} select only job offers and no other elements. Return 'True' if only jobs are selected and 'False' if {class_list} CSS classes select also other elements. {'\n'.join(await locator.all_inner_texts())}",
        #     use_openai=True,
        # )
        # if "True" in response:
        jobs = set(await locator.all())
        jobs_2 = set(await locator.and_(self.page.get_by_role("link")).all())
        jobs3 = set(await locator.get_by_role("link").all())
        logger.info(
            f"Amount of elements selected by {class_list} CSS classes: {len(jobs)} and second version: {len(jobs_2)}, and third version: {len(jobs3)}"
        )
        return tuple(jobs)

        logger.error(f"{class_list} don't select only job entries")
        logger.error(
            f"Amount of elements selected by {class_list} CSS classes: {len(await locator.all())}"
        )
        return tuple()

    async def navigate_to_next_page(self) -> bool:
        btn, _, _ = await find_html_element(
            self.page, await load_prompt("scarping:user:next_page_button")
        )
        if not btn:
            logger.info("Could not find next page button")
            return False
        await click(btn, self.page)
        return True

    async def _go_to_next_job(self) -> bool:
        pass

    async def _apply_for_job(self):
        pass

    async def _get_job_information(self, link: str) -> None | JobEntry:
        job_page: Page = await self.context.new_page()
        await goto(job_page, link)

        response = await send_req_to_llm(
            prompt=await load_prompt(
                "scraping:user:job_offer_info",
                page=await get_page_content(job_page),
            ),
            use_openai=True,
            model=JobEntryResponse,
        )

        attributes = response.model_dump()
        attributes["discovery_date"] = datetime.date.today()
        attributes["job_url"] = link

        await job_page.close()

        try:
            job_entry = JobEntry.model_validate(attributes)
            logger.info(f"JobEntry model data: {pformat(job_entry)}")
            return job_entry
        except Exception as e:
            logger.exception(e)
        return None
