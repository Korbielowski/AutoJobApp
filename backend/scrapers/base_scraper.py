import abc

from devtools import pformat
from playwright.async_api import BrowserContext, Page

from backend.database.models import WebsiteModel
from backend.llm.llm import send_req_to_llm
from backend.llm.prompts import load_prompt
from backend.logger import get_logger
from backend.schemas.llm_responses import StateOutput
from backend.schemas.models import JobEntry, UserNeeds

logger = get_logger()


class BaseScraper(abc.ABC):
    def __init__(
        self,
        url: str,
        context: BrowserContext,
        page: Page,
        website_info: WebsiteModel,
        retries: int,
    ) -> None:
        self.url = url
        self.context = context
        self.page = page
        self.website_info = website_info
        self.retries = retries

    @abc.abstractmethod
    async def login_to_page(self) -> None:
        pass

    @abc.abstractmethod
    async def navigate_to_job_listing_page(self) -> None:
        pass

    @abc.abstractmethod
    async def get_job_entries(self) -> tuple[str, ...]:
        pass

    @abc.abstractmethod
    async def navigate_to_next_page(self) -> bool:
        pass

    @abc.abstractmethod
    async def _apply_for_job(self):
        pass

    @abc.abstractmethod
    async def _get_job_information(self, url: str) -> JobEntry | None:
        pass

    async def process_and_evaluate_job(
        self, job_url: str, user_needs: UserNeeds
    ) -> JobEntry | None:
        job_entry = await self._get_job_information(job_url)
        logger.info(f"job_entry: {pformat(job_entry)}")
        if not job_entry:
            return None

        # return job_entry
        state = await send_req_to_llm(
            prompt=await load_prompt(
                prompt_path="career_documents:user:determine_if_offer_valuable",
                model=job_entry.model_dump(),
                user_needs=user_needs,
            ),
            use_openai=True,
            model=StateOutput,
        )

        if state.state:
            return job_entry
        return None
