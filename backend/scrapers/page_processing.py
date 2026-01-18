import asyncio
import json
import re
from copy import deepcopy

import tiktoken
import toon
from bs4 import BeautifulSoup
from devtools import pformat
from playwright.async_api import Locator, Page

from backend.logger import get_logger
from backend.schemas.llm_responses import HTMLElement, TextResponse

logger = get_logger()
TIK = tiktoken.encoding_for_model("gpt-5-")
CUTOFF_LEN = 100
TAGS_TO_REMOVE = (
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
)
# _tmp_data_store: list[dict[str, str | list[str]]] | None = None
_mapping_store: dict[str, dict[str, str | list[str]]] | None = None
_mapping_lock = asyncio.Lock()


async def set_mapping_store(
    mapping: dict[str, dict[str, str | list[str]]],
) -> None:
    async with _mapping_lock:
        global _mapping_store
        _mapping_store = mapping


# def set_tmp_data_store(element: list[dict[str, str | list[str]]]) -> None:
#     global _tmp_data_store
#     tmp_data_store = element


async def read_key_from_mapping_store(text_key: str) -> HTMLElement:
    async with _mapping_lock:
        if not _mapping_store:
            logger.error("It does not exist xd")
            raise Exception(
                "Reading from empty tmp_data_store, this should not happen"
            )
        tag = _mapping_store.get(text_key, None)
        if not tag:
            logger.error("Tag was not found in mapping")
            raise Exception("Tag was not found in mapping")
        return HTMLElement.model_validate(tag)


async def get_page_content(page: Page) -> str:
    page_content = await page.content()

    soup = BeautifulSoup(page_content, "html.parser")
    for tag in soup(TAGS_TO_REMOVE):
        tag.decompose()

    tag_list: list[dict[str, str | list[str]]] = []
    # Get "the most important" elements' attributes
    for tag in soup.find_all():
        text = tag.find(string=True, recursive=False)
        if not text:
            text = ""
        elif len(text) == 1:
            text = ""
        data: dict[str, str | list[str]] = {}
        if tag_id := tag.get("id"):
            data["id"] = tag_id
        if name := tag.get("name"):
            data["name"] = name
        if tag_type := tag.get("type"):
            data["element_type"] = tag_type
        if aria_label := tag.get("aria-label"):
            data["aria_label"] = aria_label
        if role := tag.get("role"):
            data["role"] = role
        if text:
            data["text"] = text
        if class_list := tag.get("class"):
            if isinstance(class_list, list):
                # FIXME: playwright._impl._errors.Error: Locator.count: SyntaxError: Failed to execute 'querySelectorAll' on 'Document': '.tw-w-[120px]' is not a valid selector.
                data["class_list"] = [
                    c.strip().replace("[", r"\[").replace("]", r"\]")
                    for c in class_list
                    if c.strip()
                ]
            else:
                data["class_list"] = [class_list]

        # If there is only class_list don't append element to the tag_list
        if [k for k in data.keys() if k != "class_list"]:
            data["parents_list"] = list(
                reversed(
                    [t.name for t in tag.parents if t.name != "[document]"]
                )
            )
            data["parents"] = " ".join(data["parents_list"])
            tag_list.append(data)

    tag_list_llm: list[dict[str, str | list[str]]] = []
    # Create list that will be sent to LLM/agent and will only include processed text
    for elem in tag_list:
        copied_elem: dict = deepcopy(elem)
        copied_elem.pop("parents")
        copied_elem.pop("parents_list")
        tag_list_llm.append(copied_elem)

    cleaned_tag_list: list[dict[str, str | list[str]]] = [
        tag for tag in tag_list if tag.get("text")
    ]
    mapping = {}

    # Make sure that text exists, if it exists check its length and cut if off, if it is too long
    tag_list_llm = [tag for tag in tag_list_llm if tag.get("text")]
    for index, tag in enumerate(tag_list_llm):
        processed_text = re.sub(r"\s+", " ", tag.get("text", "")).strip()
        if len(processed_text) >= CUTOFF_LEN:
            processed_text = processed_text[0 : CUTOFF_LEN + 1] + "..."
        tag_list_llm[index] = {"text": processed_text}
        mapping[processed_text] = cleaned_tag_list[index]

    methods = {
        "Raw HTML page": len(TIK.encode(page_content)),
        "Raw HTML page with certain tags removed": len(TIK.encode(str(soup))),
        "New cleaning method with json": len(
            TIK.encode(json.dumps(tag_list_llm))
        ),
        "New cleaning method with toons": len(
            TIK.encode(toon.encode(tag_list_llm))
        ),
    }
    logger.info(pformat(methods))

    # set_tmp_data_store(tag_list)
    await set_mapping_store(mapping)

    return toon.encode(tag_list_llm)


async def find_html_tag_v2(page: Page, text: str) -> Locator | None:
    element = await read_key_from_mapping_store(text)
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

    # TODO: Add step where LLMselects from multiple elements, if code above could not select single one element
    if locator:
        return locator.last

    return locator


async def get_jobs_urls(
    text_response: TextResponse, page: Page
) -> tuple[str, ...]:
    tag = await read_key_from_mapping_store(text_response.text)
    logger.debug(f"HTML element holding job title: {pformat(tag)}")

    if tag.class_list:
        class_selector = f".{'.'.join(tag.class_list)}"
    else:
        a_tag_with_job_title = page.get_by_role("link").filter(
            has_text=tag.text
        )
        tmp = (
            _
            if (_ := await a_tag_with_job_title.last.get_attribute("class"))
            else ""
        )
        class_selector = f".{'.'.join(tmp.split())}"

    if class_selector == ".":
        class_selector = ""

    a_tags = page.locator(class_selector)
    try:
        job_urls = tuple(
            [
                href
                for loc in await a_tags.all()
                if (href := await loc.get_attribute("href"))
            ]
        )
        if job_urls:
            logger.info(
                f"Job urls got using classList method: {class_selector}\n{pformat(job_urls)}"
            )
            return job_urls
    except TimeoutError:
        logger.error(
            "TimeoutError occurred while trying to retrieve job urls, using classList method"
        )

    start_index = len(tag.parents_list) - 1
    while start_index > 0 and tag.parents_list[start_index] != "a":
        start_index -= 1

    class_selector = " ".join(tag.parents_list[0 : start_index + 1])
    a_tags = page.locator(class_selector)
    try:
        job_urls = tuple(
            [
                href
                for loc in await a_tags.all()
                if (href := await loc.get_attribute("href"))
            ]
        )
        if job_urls:
            logger.info(
                f"Job urls got using parents method: {class_selector}\n{pformat(job_urls)}"
            )
            return job_urls
    except TimeoutError:
        logger.error(
            "TimeoutError occurred while trying to retrieve job urls, using parents method"
        )

    logger.warning("Could not find job urls, returning empty tuple")
    return tuple()
