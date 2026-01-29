import datetime

from backend.database.repositories.website import update_website_model
from devtools import pformat
from playwright.async_api import Page
from pydantic_ai import (
    Agent,
    UnexpectedModelBehavior,
    UsageLimitExceeded,
    UsageLimits,
)
from pydantic_ai.models import KnownModelName, Model

from backend.config import settings
from backend.database.models import WebsiteModel
from backend.exceptions import AgentLoopError, ModelImportError
from backend.llm.llm import send_req_to_llm
from backend.llm.prompts import load_prompt
from backend.logger import get_logger
from backend.schemas.llm_responses import (
    ContextForLLM,
    JobEntryResponse,
    TaskState,
    TextResponse,
)
from backend.schemas.models import AgentNameEnum, HTMLElement, JobEntry, Step
from backend.scrapers.base_scraper import BaseScraper
from backend.scrapers.page_actions import goto, step_click, step_fill
from backend.scrapers.page_processing import (
    get_jobs_urls,
    get_page_content,
)
from backend.scrapers.tools import click_element, fill_element, get_page_data
from backend.utils import log_agent_run_data

OPENAI_MODEL = "openai:gpt-5-mini-2025-08-07"
logger = get_logger()


async def _run_automation_steps(
    agent_name: AgentNameEnum,
    website_info: WebsiteModel,
    page: Page,
) -> tuple[bool, HTMLElement | None]:
    logger.info(f"Running automation steps for {agent_name} agent")
    automation_steps = website_info.automation_steps
    start_url = page.url

    if not automation_steps:
        logger.warning(f"There are no automation steps for {agent_name}")
        return False, None

    if agent_name == AgentNameEnum.login_agent:
        steps = [
            Step.model_validate(step)
            for step in automation_steps.get("login_steps", [])
        ]
    elif agent_name == AgentNameEnum.job_listing_page_agent:
        steps = [
            Step.model_validate(step)
            for step in automation_steps.get("job_listing_page_steps", [])
        ]
    elif agent_name == AgentNameEnum.job_urls_agent:
        steps = [
            Step.model_validate(step)
            for step in automation_steps.get("job_urls_steps", [])
        ]
    elif agent_name == AgentNameEnum.next_page_agent:
        steps = [
            Step.model_validate(step)
            for step in automation_steps.get("next_page_steps", [])
        ]

    if not steps:
        logger.warning(f"There are no automation steps for {agent_name}")
        return False, None

    for step in steps:
        if step.function == "click":
            tool_result = await step_click(page=page, element=step.tag)
        elif step.function == "fill":
            tool_result = await step_fill(
                page=page,
                element=step.tag,
                website_info=website_info,
                **step.additional_arguments,
            )
        else:  # Required for job_urls_steps/job_urls_agent
            return True, step.tag

        if not tool_result.success:
            logger.error(
                f"There was an error while running {agent_name} automation steps. Navigating back to {start_url}, and using LLM to find proper elements"
            )
            await goto(page, start_url)
            return False, None

    return True, None


# async def _save_automation_steps(
#     agent_name: AgentNameEnum,
#     steps: list[Step],
#     website_info: WebsiteModel,
# ) -> None:
#     return
# await save_automation_steps(
#     AutomationSteps(agent_name=agent_name, steps=steps)
# )


def _get_model(name: KnownModelName, api_key: str) -> Model:
    provider_name, model_name = name.split(":")

    # Grok (x.AI) works with both openai and anthropic models. We chose to use openai
    # According to this github issue: https://github.com/pydantic/pydantic-ai/issues/261
    if provider_name == "grok":
        provider_name = "openai"

    provider_model_import_map: dict[str, tuple[tuple[str, str], ...]] = {
        "openai": (
            ("pydantic_ai.models.openai", "pydantic_ai.providers.openai"),
            ("OpenAIChatModel", "OpenAIProvider"),
        ),
        "google": (
            ("pydantic_ai.models.google", "pydantic_ai.providers.google"),
            ("GoogleModel", "GoogleProvider"),
        ),
        "anthropic": (
            ("pydantic_ai.models.anthropic", "pydantic_ai.providers.anthropic"),
            ("AnthropicModel", "AnthropicProvider"),
        ),
        "mistral": (
            ("pydantic_ai.models.mistral", "pydantic_ai.providers.mistral"),
            ("MistralModel", "MistralProvider"),
        ),
    }

    imports = provider_model_import_map.get(provider_name)
    if not imports:
        raise ModelImportError(
            f"Cannot import {model_name} model from {provider_name} provider. Check if You have required dependencies installed via application's dependencies manager.",
        )

    # Dynamically import provider and model classes
    model = getattr(
        __import__(imports[0][0], fromlist=imports[1][0]), imports[1][0]
    )
    provider = getattr(
        __import__(imports[0][1], fromlist=imports[1][1]), imports[1][1]
    )

    return model(model_name=model_name, provider=provider(api_key=api_key))


class LLMScraperV2(BaseScraper):
    _model: Model = _get_model(OPENAI_MODEL, settings.OPENAI_API_KEY)

    async def _agent_loop(
        self, agent: Agent[ContextForLLM, TaskState], agent_name: AgentNameEnum
    ) -> bool:
        start_url = self.page.url
        max_turns = 15
        steps: list[Step] = []
        causes: list[BaseException | None] = []

        logger.debug(f"Running agent loop for '{agent.name}'")
        for _ in range(1, self.retries + 1):
            try:
                result = await agent.run(
                    "",
                    deps=ContextForLLM(
                        page=self.page,
                        website_info=self.website_info,
                        agent_name=agent_name,
                        steps=steps,
                    ),
                    usage_limits=UsageLimits(request_limit=max_turns),
                )
                log_agent_run_data(agent_name, result)
            except (UnexpectedModelBehavior, UsageLimitExceeded) as e:
                logger.exception(
                    f"Error occurred: {e}\nCause: {e.__cause__}\nRun {_} of {self.retries}"
                )
                steps.clear()
                causes.append(e.__cause__)

                await goto(page=self.page, url=start_url)
                if isinstance(e, UsageLimitExceeded):
                    max_turns += 5

                continue

            if (
                result.output.state == "done"
                and result.output.confidence >= 0.8
            ):
                update_website_model(
                    session=self.session,
                    agent_name=agent_name,
                    website_info=self.website_info,
                    steps=steps,
                )
                return True
            elif (
                result.output.state == "cannot_be_done"
                and result.output.confidence >= 0.8
            ):
                return False
            elif result.output.state == "failed":
                await goto(page=self.page, url=start_url)

        raise AgentLoopError(
            f"Agent loop failed for {agent_name}", self.retries, causes
        )

    async def login_to_page(self) -> None:
        await goto(self.page, self.url)

        status, _ = await _run_automation_steps(
            AgentNameEnum.login_agent,
            self.website_info,
            self.page,
        )
        if status:
            return

        login_agent = Agent(
            name=AgentNameEnum.login_agent,
            model=self._model,
            system_prompt=await load_prompt("scraping:system:login_to_page"),
            tools=[click_element, fill_element, get_page_data],
            deps_type=ContextForLLM,
            output_type=TaskState,
        )

        await self._agent_loop(login_agent, AgentNameEnum.login_agent)

    async def navigate_to_job_listing_page(self) -> None:
        status, _ = await _run_automation_steps(
            AgentNameEnum.job_listing_page_agent,
            self.website_info,
            self.page,
        )
        if status:
            return

        job_list_page_agent = Agent(
            name=AgentNameEnum.job_listing_page_agent,
            model=self._model,
            system_prompt=await load_prompt(
                "scraping:system:navigate_to_job_listing_page"
            ),
            tools=[click_element, get_page_data],
            deps_type=ContextForLLM,
            output_type=TaskState,
        )

        await self._agent_loop(
            job_list_page_agent, AgentNameEnum.job_listing_page_agent
        )

    async def get_job_entries(self) -> tuple[str, ...]:
        status, tag = await _run_automation_steps(
            AgentNameEnum.job_urls_agent,
            self.website_info,
            self.page,
        )
        if status and tag:
            await get_jobs_urls(text_response=tag, page=self.page)

        text_response = await send_req_to_llm(
            system_prompt=await load_prompt("scraping:system:job_offer_links"),
            prompt=await get_page_content(
                self.page, self.website_info, AgentNameEnum.job_urls_agent
            ),
            response_type=TextResponse,
            model=self._model,
            agent_name=AgentNameEnum.job_urls_agent,
        )
        return await get_jobs_urls(text_response=text_response, page=self.page)

    async def navigate_to_next_page(self) -> bool:
        status, _ = await _run_automation_steps(
            AgentNameEnum.next_page_agent,
            self.website_info,
            self.page,
        )
        if status:
            return True

        next_page_agent = Agent(
            name=AgentNameEnum.next_page_agent,
            model=self._model,
            system_prompt=await load_prompt("scraping:system:next_page_button"),
            tools=[click_element, get_page_data],
            deps_type=ContextForLLM,
            output_type=TaskState,
        )

        return await self._agent_loop(
            next_page_agent, AgentNameEnum.next_page_agent
        )

    async def _apply_for_job(self):
        pass

    async def _get_job_information(self, url: str) -> JobEntry | None:
        job_page: Page = await self.context.new_page()
        await goto(job_page, url)

        response = await send_req_to_llm(
            prompt=await load_prompt(
                prompt_path="scraping:user:job_offer_info",
                page=await get_page_content(
                    job_page,
                    self.website_info,
                    AgentNameEnum.login_agent,  # FIXME: Call to get_page_content function is not correct here, as we are calling it with login_agent data
                ),
            ),
            response_type=JobEntryResponse,
            model=self._model,
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
