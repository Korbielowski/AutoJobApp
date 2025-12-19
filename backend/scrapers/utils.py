import asyncio
import random

import devtools
import tiktoken
from bs4 import BeautifulSoup
from devtools import pformat
from playwright.async_api import Locator, Page, TimeoutError
from pydantic import BaseModel

from backend.config import settings
from backend.database.models import AttributeType, Step
from backend.llm.llm import send_req_to_llm
from backend.llm.prompts import load_prompt
from backend.logger import get_logger
from backend.schemas.llm_responses import HTMLElement

TIK = tiktoken.encoding_for_model("gpt-5-")
logger = get_logger()


async def goto(page: Page, link: str, retry: int = 3) -> None:
    done = False
    while not done and retry > 0:
        try:
            await page.goto(link)
            await page.wait_for_load_state("load")
            await asyncio.sleep(3)
            done = True
        except TimeoutError:
            logger.exception("Timeout for goto")
        retry -= 1


async def click(element: None | Locator, page: Page, retry: int = 3) -> bool:
    if not element:
        logger.exception("Button/Link is None")
        return False

    while retry > 0:
        try:
            if settings.DEBUG:
                await element.highlight()
                await asyncio.sleep(3)
            await element.click()
            await page.wait_for_load_state("load")
            await asyncio.sleep(3)
            return True
        except TimeoutError:
            logger.exception("Timeout for click")
        retry -= 1
    return False


async def fill(element: None | Locator, value: str, retry: int = 3) -> bool:
    if not element:
        logger.error("Could not find input field")
        return False

    while retry > 0:
        try:
            if settings.DEBUG:
                await element.highlight()
                await asyncio.sleep(3)
            await element.press_sequentially(
                value, delay=random.randint(5, 10) * 100
            )
            return True
        except TimeoutError:
            logger.exception("Timeout for fill")
        retry -= 1
    return False


async def get_page_content(page: Page) -> str:
    # TODO: Make page content smaller by e.g. excluding head or code tags and only by including body
    # TODO: Check in the future, whether regex would not be faster and overall better solution
    # TODO: Add option to get important info about html tags and their content, then send all of it in json format to LLM
    page_content = await page.content()

    logger.info(
        f"Amount of tokens before cleaning: {len(TIK.encode(page_content))}"
    )
    soup = BeautifulSoup(page_content, "html.parser")
    cleaned_page_content = ""
    for tag in soup(
        [
            "head",
            "meta",
            "style",
            "script",
            "noscript",
            "template",
            "iframe",
            "video",
            "audio",
            "map",
            "area",
            "embed",
            "object",
            "applet",
            "track",
            "canvas",
            "svg",
            "img",
            "picture",
            "source",
        ]
    ):
        tag.decompose()
        cleaned_page_content = str(soup)
    logger.info(
        f"Amount of tokens after cleaning: {len(TIK.encode(cleaned_page_content))}"
    )
    return cleaned_page_content


async def find_html_element_attributes(
    page: Page | str, prompt: str
) -> HTMLElement:
    if type(page) is Page:
        page_content = await get_page_content(page)
    else:
        page_content = page

    response = await send_req_to_llm(
        system_prompt=await load_prompt("scraping:system:get_attributes"),
        prompt=f"{prompt}\n{page_content}",
        use_openai=True,
        model=HTMLElement,
    )

    logger.info(f"Object got from LLM: {devtools.pformat(response)}")

    return response


async def find_html_element(
    page: Page, prompt: str, additional_llm: bool = False
) -> tuple[None, None, None] | tuple[Locator, str, AttributeType]:
    logger.info(f"Prompt: {prompt}")

    page_content = await get_page_content(page)
    for _ in range(5):
        attributes = await find_html_element_attributes(page_content, prompt)
        if not any(attributes.model_dump().values()):
            return None, None, None

        count_dict = {}
        locator = None

        element_id = attributes.id
        if element_id:
            logger.info(element_id)
            locator = page.locator(f"#{element_id}")
            count = await locator.count()
            await log_locator(locator, message="Search by id", count=count)
            if 0 < count < 2 and await verify_if_right_element_was_chosen(
                locator.last, attributes, prompt
            ):
                return locator.last, element_id, AttributeType.id
            elif count > 2:
                count_dict[count] = await locator.all()

        role = attributes.role
        if role:
            if locator and await locator.count() >= 2:
                locator = locator.and_(page.get_by_role(role, exact=True))
            else:
                locator = page.get_by_role(role, exact=True)

            count = await locator.count()
            await log_locator(locator, message="Search by role", count=count)
            if 0 < count < 2 and await verify_if_right_element_was_chosen(
                locator.last, attributes, prompt
            ):
                return locator.last, role, AttributeType.text
            elif count > 2:
                count_dict[count] = await locator.all()

        text = attributes.text
        logger.info(f"Search by text: {text}")
        if text:
            if locator and await locator.count() >= 2:
                locator = locator.and_(page.get_by_text(text, exact=True))
            else:
                locator = page.get_by_text(text, exact=True)

            count = await locator.count()
            await log_locator(locator, message="Search by text", count=count)
            if 0 < count < 2 and await verify_if_right_element_was_chosen(
                locator.last, attributes, prompt
            ):
                return locator.last, text, AttributeType.text
            elif count > 2:
                count_dict[count] = await locator.all()

        aria_label = attributes.aria_label
        if aria_label:
            if locator and await locator.count() >= 2:
                locator = locator.and_(
                    page.get_by_label(aria_label, exact=True)
                )
            else:
                locator = page.get_by_label(aria_label, exact=True)
            count = await locator.count()
            await log_locator(
                locator, message="Search by aria_label", count=count
            )
            if 0 < count < 2 and await verify_if_right_element_was_chosen(
                locator.last, attributes, prompt
            ):
                return locator.last, aria_label, AttributeType.aria_label
            elif count > 2:
                count_dict[count] = await locator.all()

        name = attributes.name
        if name:
            if locator and await locator.count() >= 2:
                locator = locator.and_(page.locator(f'[name="{name}"]'))
            else:
                locator = page.locator(f'[name="{name}"]')
            count = await locator.count()
            await log_locator(locator, message="Search by name", count=count)
            if 0 < count < 2 and await verify_if_right_element_was_chosen(
                locator.last, attributes, prompt
            ):
                return locator.last, name, AttributeType.name
            elif count > 2:
                count_dict[count] = await locator.all()

        placeholder = attributes.placeholder
        if placeholder:
            if locator and await locator.count() >= 2:
                locator = locator.and_(
                    page.get_by_placeholder(placeholder, exact=True)
                )
            else:
                locator = page.get_by_placeholder(placeholder, exact=True)

            count = await locator.count()
            await log_locator(
                locator, message="Search by placeholder", count=count
            )
            if 0 < count < 2 and await verify_if_right_element_was_chosen(
                locator.last, attributes, prompt
            ):
                return locator.last, placeholder, AttributeType.element_type
            elif count > 2:
                count_dict[count] = await locator.all()

        element_type = attributes.element_type
        if element_type:
            if locator and await locator.count() >= 2:
                locator = locator.and_(page.locator(f'[type="{element_type}"]'))
            else:
                locator = page.locator(f'[type="{element_type}"]')

            count = await locator.count()
            await log_locator(locator, message="Search by type", count=count)
            if 0 < count < 2 and await verify_if_right_element_was_chosen(
                locator.last, attributes, prompt
            ):
                return locator.last, element_type, AttributeType.element_type
            elif count > 2:
                count_dict[count] = await locator.all()

        class_list = attributes.class_list
        # FIXME: playwright._impl._errors.Error: Locator.count: SyntaxError: Failed to execute 'querySelectorAll' on 'Document': '.tw-w-[120px]' is not a valid selector.
        logger.info(f"Class_list type: {type(class_list)}, {class_list}")
        if class_list:
            class_selector = f".{'.'.join(class_list)}"
            if locator and await locator.count() >= 2:
                locator = locator.and_(page.locator(class_selector))
            else:
                locator = page.locator(class_selector)
            count = await locator.count()
            if 0 < count < 2 and await verify_if_right_element_was_chosen(
                locator.last, attributes, prompt
            ):
                return locator.last, class_selector, AttributeType.class_l
            elif count > 2:
                count_dict[count] = await locator.all()

        # TODO: Add LLM element choosing
        if additional_llm:
            prompt_elements = await load_prompt(
                "scraping:user:llm_select_element"
            )
            # TODO: We are choosing wrong item from dict by count
            for locator in count_dict[min(count_dict, key=count_dict.get)]:
                prompt_elements += f"{await locator.all_inner_texts()}, "
            prompt_elements += prompt
            logger.info(
                f"Chosen this count: {min(count_dict, key=count_dict.get)}, this is the prompt:\n{prompt_elements}"
            )

            response = await send_req_to_llm(
                prompt=prompt_elements, use_openai=True
            )
            try:
                num_in_list = int(response)
                return (
                    count_dict[min(count_dict, key=count_dict.get)][
                        num_in_list
                    ],
                    None,
                    None,
                )
            except ValueError:
                logger.exception(
                    f"ValueError while casting LLM response for locators: {response}"
                )

    return None, None, None


async def verify_if_right_element_was_chosen(
    locator: Locator, attributes: BaseModel, prompt: str
) -> bool:
    check_prompt = await load_prompt(
        "scraping:user:llm_verify_output",
        inner_texts=await locator.all_inner_texts(),
        attributes=attributes,
        prompt=prompt,
    )
    if "True" in await send_req_to_llm(prompt=check_prompt, use_openai=True):
        logger.info(
            f"LLM thinks this element:\n{pformat(attributes)}\nSuits this prompt: {prompt}"
        )
        return True
    logger.error(
        f"LLM thinks this element:\n{pformat(attributes)}\nDoes not suit this prompt: {prompt}"
    )
    return False


async def get_locator(page: Page, step: Step) -> Locator | None:
    attribute_type = step.attribute_type
    attribute = step.html_element_attribute
    if attribute_type == AttributeType.id:
        return page.locator(f"#{attribute}")
    elif attribute_type == AttributeType.text:
        return page.get_by_text(attribute)
    elif attribute_type == AttributeType.aria_label:
        return page.get_by_label(attribute)
    elif attribute_type == AttributeType.name:
        return page.locator(f'[name="{attribute}"]')
    elif attribute_type == AttributeType.element_type:
        return page.locator(f'[type="{attribute}"]')
    elif attribute_type == AttributeType.class_l:
        return page.locator(f".{attribute}")
    return None


async def log_locator(
    locator: None | Locator, message: str = "", **kwargs
) -> None:
    if locator is None:
        logger.info(f"The locator is None, other data:\n{kwargs}\n")
    else:
        logger.info(
            f"{message}\n{await locator.all()}\nother data:\n{kwargs}\n"
        )
