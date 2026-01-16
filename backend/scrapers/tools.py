from pprint import pformat
from typing import Literal

from agents import RunContextWrapper, function_tool

from backend.logger import get_logger
from backend.schemas.llm_responses import (
    ContextForLLM,
    ToolResult,
)
from backend.scrapers.page_actions import click, fill
from backend.scrapers.page_processing import get_page_content

logger = get_logger()


@function_tool
async def get_page_data(
    wrapper: RunContextWrapper[ContextForLLM],
) -> ToolResult:
    """
    Get data about all page HTML elements in a simplified form of JSON and page url
    :return: Page elements in JSON-like form and url
    :rtype: ToolResult
    """
    logger.debug(f"'{wrapper.context.agent_name}' invoked 'get_page_data' tool")
    result = ToolResult(
        success=True,
        result=f"url: {wrapper.context.page.url}\npage elements representation:\n{await get_page_content(wrapper.context.page)}",
    )
    # logger.info(f"Tool: get_page_data, {pformat(result)}")
    return result


@function_tool
async def click_element(
    wrapper: RunContextWrapper[ContextForLLM], text: str
) -> ToolResult:
    """
    Click a given element on the page.
    :param text: Text of the element to clik
    :type text: str
    :return: Result of the click action
    :rtype: ToolResult
    """
    logger.debug(
        f"'{wrapper.context.agent_name}' invoked 'click_element' tool with params: {text =}"
    )
    result = await click(page=wrapper.context.page, text=text)
    logger.info(f"'click_element' tool result:{pformat(result)}")
    return result


@function_tool
async def fill_element(
    wrapper: RunContextWrapper[ContextForLLM],
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
        f"'{wrapper.context.agent_name}' invoked 'fill_element' tool with params: {input_type =}\n{text =}"
    )
    result = await fill(
        page=wrapper.context.page,
        text=text,
        input_type=input_type,
        website_info=wrapper.context.website_info,
    )
    logger.info(f"'fill_element' tool result:{pformat(result)}")
    return result
