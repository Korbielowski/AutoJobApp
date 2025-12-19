import abc

from playwright.async_api import BrowserContext, Locator, Page

from backend.database.models import JobEntry, WebsiteModel
from backend.llm.llm import send_req_to_llm
from backend.llm.prompts import load_prompt
from backend.logger import get_logger

logger = get_logger()


class BaseScraper(abc.ABC):
    def __init__(
        self,
        url: str,
        email: str,
        password: str,
        context: BrowserContext,
        page: Page,
        website_info: WebsiteModel | None,
        retries: int,
    ) -> None:
        self.url = url
        self.email = (
            email  # TODO: Get email for each website separately from database
        )
        self.password = password  # TODO: Get password for each website separately from database
        self.context = context
        self.page = page
        self.website_info = website_info if website_info else WebsiteModel()
        self.retries = retries

    @abc.abstractmethod
    async def login_to_page(self) -> None:
        pass

    @abc.abstractmethod
    async def _navigate_to_job_list_page(self) -> None:
        pass

    @abc.abstractmethod
    async def get_job_entries(self) -> tuple[Locator, ...]:
        pass

    @abc.abstractmethod
    async def navigate_to_next_page(self) -> bool:
        pass

    @abc.abstractmethod
    async def _go_to_next_job(self) -> bool:
        pass

    @abc.abstractmethod
    async def _apply_for_job(self):
        pass

    @abc.abstractmethod
    async def _get_job_information(self, url: str) -> JobEntry | None:
        pass

    async def process_and_evaluate_job(
        self, locator: Locator
    ) -> JobEntry | None:
        url = await locator.get_attribute("href")
        job_entry = await self._get_job_information(url)

        return job_entry

        if not job_entry:
            logger.error(f"job_entry: {job_entry}")
            return None

        logger.info(f"job_entry: {job_entry.model_dump_json()}")

        # TODO: Get user needs
        user_needs = ""
        prompt = await load_prompt(
            prompt_path="cv:user:determine_if_offer_valuable",
            user_needs=user_needs,
            job_entry=job_entry.model_dump_json(),
        )  # TODO: Fix this code, so that it behaves as other load_prompt instances
        response = await send_req_to_llm(prompt, use_openai=True)
        logger.info(f"LLM evaluation: {response}")

        if "True" in response:
            return job_entry
        else:
            return None
