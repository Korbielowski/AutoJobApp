from pprint import pformat
from typing import Literal

from pydantic_ai import RunContext

from backend.logger import get_logger
from backend.schemas.llm_responses import (
    ContextForLLM,
    ToolResult,
)
from backend.scrapers.page_actions import click, fill
from backend.scrapers.page_processing import get_page_content

logger = get_logger()


async def get_page_data(context: RunContext[ContextForLLM]) -> ToolResult:
    """
    Get data about all page HTML elements in a simplified form of JSON and page url
    :return: Page elements in JSON-like form and url
    :rtype: ToolResult
    """
    logger.debug(f"'{context.deps.agent_name}' invoked 'get_page_data' tool")
    result = ToolResult(
        success=True,
        result=f"url: {context.deps.page.url}\npage elements representation:\n{await get_page_content(context.deps.page)}",
    )
    # logger.info(f"Tool: get_page_data, {pformat(result)}")
    return result


async def click_element(
    context: RunContext[ContextForLLM], text: str
) -> ToolResult:
    """
    Click a given element on the page.
    :param text: Text of the element to clik
    :type text: str
    :return: Result of the click action
    :rtype: ToolResult
    """
    logger.debug(
        f"'{context.deps.agent_name}' invoked 'click_element' tool with params: {text =}"
    )
    result = await click(
        page=context.deps.page, text=text, steps=context.deps.steps
    )
    logger.info(f"'click_element' tool result:{pformat(result)}")
    return result


async def fill_element(
    context: RunContext[ContextForLLM],
    text: str,
    input_type: Literal["email", "password"],
) -> ToolResult:
    """
    Fill a given input field.
    :param text: Label of the input field
    :type text: str
    :param input_type: Whether the input, that should be passed to input field should be user email or password. Password and email will be read from database by function.
    :type input_type: InputFieldTypeEnum
    :return: Result of the action
    :rtype: ToolResult
    """
    logger.debug(
        f"'{context.deps.agent_name}' invoked 'fill_element' tool with params: {input_type =}\n{text =}"
    )
    result = await fill(
        page=context.deps.page,
        text=text,
        input_type=input_type,
        website_info=context.deps.website_info,
        steps=context.deps.steps,
    )
    logger.info(f"'fill_element' tool result:{pformat(result)}")
    return result
