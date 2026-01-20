import datetime

from devtools import pformat
from playwright.async_api import Page
from pydantic_ai import Agent, AgentRunResult
from pydantic_ai.models import KnownModelName

from backend.llm.llm import send_req_to_llm
from backend.llm.prompts import load_prompt
from backend.logger import get_logger
from backend.schemas.llm_responses import (
    ContextForLLM,
    JobEntryResponse,
    TaskState,
    TextResponse,
)
from backend.schemas.models import JobEntry
from backend.scrapers.base_scraper import BaseScraper
from backend.scrapers.page_actions import goto
from backend.scrapers.page_processing import (
    get_jobs_urls,
    get_page_content,
)
from backend.scrapers.tools import click_element, fill_element, get_page_data

OPENAI_MODEL = "openai:gpt-5-mini-2025-08-07"
logger = get_logger()


def _log_agent_run_data(result: AgentRunResult[TaskState]):
    input_tokens = result.usage().input_tokens
    output_tokens = result.usage().output_tokens
    logger.info(
        f"Agent name: {result.response.model_name}\nTotal cost: {
            result.response.cost()
        }\nTotal tokens used: {
            input_tokens + output_tokens
        }\nInput tokens used: {input_tokens}\nOutput tokens used: {
            output_tokens
        }\nFinal agent output{pformat(result.output)}\nFinish reason: {
            result.response.finish_reason
        }"
    )


class LLMScraperV2(BaseScraper):
    _model: KnownModelName = OPENAI_MODEL

    async def _agent_loop(self, agent: Agent[ContextForLLM, TaskState]) -> bool:
        logger.debug(f"Running agent loop for '{agent.name}'")

        start_url = self.page.url
        for _ in range(self.retries):
            result = await agent.run(
                "",
                deps=ContextForLLM(
                    page=self.page,
                    website_info=self.website_info,
                    agent_name=name if (name := agent.name) else "",
                ),
            )
            _log_agent_run_data(result)
            if (
                result.output.state == "done"
                and result.output.confidence >= 0.8
            ):
                return True
            elif result.output.state == "failed":
                await goto(page=self.page, url=start_url)
        return False

    async def login_to_page(self) -> None:
        await goto(self.page, self.url)

        login_agent = Agent(
            name="login_agent",
            model=self._model,
            system_prompt=await load_prompt("scraping:system:login_to_page"),
            tools=[click_element, fill_element, get_page_data],
            deps_type=ContextForLLM,
            output_type=TaskState,
        )

        await self._agent_loop(login_agent)

    async def navigate_to_job_listing_page(self) -> None:
        job_list_page_agent = Agent(
            name="job_list_page_agent",
            model=self._model,
            system_prompt=await load_prompt(
                "scraping:system:navigate_to_job_listing_page"
            ),
            tools=[click_element, get_page_data],
            deps_type=ContextForLLM,
            output_type=TaskState,
        )

        await self._agent_loop(job_list_page_agent)

    async def get_job_entries(self) -> tuple[str, ...]:
        text_response = await send_req_to_llm(
            system_prompt=await load_prompt("scraping:system:job_offer_links"),
            prompt=await get_page_content(self.page),
            model=TextResponse,
        )
        return await get_jobs_urls(text_response=text_response, page=self.page)

    async def navigate_to_next_page(self) -> bool:
        next_page_agent = Agent(
            name="next_page_agent",
            model=self._model,
            system_prompt=await load_prompt("scraping:system:next_page_button"),
            tools=[click_element, get_page_data],
            deps_type=ContextForLLM,
            output_type=TaskState,
        )

        return await self._agent_loop(next_page_agent)

    async def _apply_for_job(self):
        pass

    async def _get_job_information(self, url: str) -> JobEntry | None:
        job_page: Page = await self.context.new_page()
        await goto(job_page, url)

        response = await send_req_to_llm(
            prompt=await load_prompt(
                prompt_path="scraping:user:job_offer_info",
                page=await get_page_content(job_page),
            ),
            use_openai=True,
            model=JobEntryResponse,
        )

        attributes = response.model_dump()
        attributes["discovery_date"] = datetime.date.today()
        attributes["job_url"] = url

        await job_page.close()

        try:
            job_entry = JobEntry.model_validate(attributes)
            logger.info(f"JobEntry model data: {pformat(job_entry)}")
            return job_entry
        except Exception as e:
            logger.exception(e)
        return None
