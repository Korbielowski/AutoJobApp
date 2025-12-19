import os
from pathlib import Path

import aiofiles
import devtools
from sqlmodel import Session
from weasyprint import CSS, HTML

from backend.config import settings
from backend.database.crud import (
    get_candidate_data,
    get_user_preferences,
    save_job_entry,
)
from backend.database.models import (
    CVCreationModeEnum,
    JobEntryModel,
    SkillsLLMResponse,
    UserModel,
)
from backend.llm.llm import send_req_to_llm
from backend.llm.prompts import load_prompt
from backend.logger import get_logger
from backend.schemas.llm_responses import (
    CompanyDetails,
    CoverLetterOutput,
    CVOutput,
)
from backend.scrapers.base_scraper import JobEntry

logger = get_logger()


async def load_template_and_styling() -> tuple[str, str]:
    html_template, styling = "", ""
    async with (
        aiofiles.open(settings.HTML_TEMPLATE_PATH, "r") as template_file,
        aiofiles.open(settings.STYLING_PATH, "r") as styling_file,
    ):
        html_template, styling = (
            await template_file.read(),
            await styling_file.read(),
        )

    return html_template, styling


async def save_document_to_file(path: Path, file_name: str, data: str) -> None:
    editable_file_path = path / file_name
    async with aiofiles.open(editable_file_path, "w") as file:
        await file.write(data)


async def create_cover_letter(
    user: UserModel,
    session: Session,
    job_entry: JobEntry,
    converted_title: str,
    current_time: str,
    path: Path,
) -> str:
    if not job_entry.company_name:
        logger.warning(
            f"Company name does not exist, cannot create cover letter, {job_entry.company_name=}"
        )
        return ""

    if job_entry.company_url:
        logger.debug(
            f"Company url does not exist, and it will not be included in LLM request, {job_entry.company_url=}"
        )

    company_details = await send_req_to_llm(
        prompt=await load_prompt(
            prompt_path="career_documents:user:company_data_search",
            company_name=job_entry.company_name,
        ),
        model=CompanyDetails,
        tools=["web_search"],
    )
    logger.debug(f"Company info: {devtools.pformat(company_details)}")

    candidate_data = get_candidate_data(session=session, user=user)

    cover_letter = await send_req_to_llm(
        prompt=await load_prompt(
            prompt_path="career_documents:user:cover_letter_generation",
            model=candidate_data,
            title=job_entry.title,
            requirements=job_entry.requirements,
            duties=job_entry.duties,
            about_project=job_entry.about_project,
            additional_information=job_entry.additional_information,
            products_and_technologies=company_details.products_and_technologies,
            work_culture=company_details.work_culture,
            business_and_industry_context=company_details.business_and_industry_context,
            mission_and_strategic_direction=company_details.mission_and_strategic_direction,
        ),
        model=CoverLetterOutput,
    )

    file_name = f"Letter_{converted_title}_{current_time}"
    cover_letter_path = path / f"{file_name}.pdf"

    HTML(string=cover_letter.html).write_pdf(cover_letter_path)
    await save_document_to_file(
        path, file_name=f"{file_name}.html", data=cover_letter.html
    )

    return cover_letter_path.as_uri()


async def create_cv(
    user: UserModel,
    session: Session,
    job_entry: JobEntry,
    converted_title: str,
    current_time: str,
    path: Path,
    cv_creation_mode: CVCreationModeEnum,
) -> str:
    candidate_data = get_candidate_data(session=session, user=user)
    html_template, styling = await load_template_and_styling()
    cv = None

    if cv_creation_mode == "llm-generation":
        skills_chosen_by_llm = await send_req_to_llm(
            system_prompt=await load_prompt(
                prompt_path="career_documents:system:skill_selection"
            ),
            prompt=await load_prompt(
                prompt_path="career_documents:user:skill_selection",
                model=candidate_data,
                requirements=job_entry.requirements,
                duties=job_entry.duties,
                about_project=job_entry.about_project,
            ),
            model=SkillsLLMResponse,
        )
        cv = await send_req_to_llm(
            system_prompt=await load_prompt(
                prompt_path="career_documents:system:cv_generation"
            ),
            prompt=await load_prompt(
                prompt_path="career_documents:user:cv_generation",
                model=skills_chosen_by_llm,
                full_name=candidate_data.full_name,
                email=candidate_data.email,
                phone_number=candidate_data.phone_number,
                social_platforms=candidate_data.social_platforms,
            ),
            model=CVOutput,
        )
    elif cv_creation_mode == "llm-selection":
        skills_chosen_by_llm = await send_req_to_llm(
            system_prompt=await load_prompt(
                prompt_path="career_documents:system:skill_selection"
            ),
            prompt=await load_prompt(
                prompt_path="career_documents:user:skill_selection",
                model=candidate_data,
                requirements=job_entry.requirements,
                duties=job_entry.duties,
                about_project=job_entry.about_project,
            ),
            model=SkillsLLMResponse,
        )
        cv = await send_req_to_llm(
            prompt=await load_prompt(
                "career_documents:user:cv_insert_skills",
                model=skills_chosen_by_llm,
                full_name=candidate_data.full_name,
                email=candidate_data.email,
                phone_number=candidate_data.phone_number,
                social_platforms=candidate_data.social_platforms,
                template=html_template,
            ),
            model=CVOutput,
        )
    elif cv_creation_mode == "no-llm-generation":
        raise NotImplementedError(
            "no-llm-generation option is not fully implemented yet. Please use other CV generation techniques"
        )
        # html = html_template.format(
        #     full_name=candidate_data.full_name,
        #     email=candidate_data.email,
        #     phone_number=candidate_data.phone_number,
        #     github=,
        #     linkedin=,
        #     personal_website=,
        # )
        # cv = CVOutput(html=html, css=styling)
    elif cv_creation_mode == "user-specified":
        if user_preferences := get_user_preferences(session, user):
            return Path(user_preferences.cv_path).as_uri()
        raise Exception("Could not load or create/generate CV")

    file_name = f"CV_{converted_title}_{current_time}"
    cv_path = path / f"{file_name}.pdf"

    HTML(string=cv.html).write_pdf(cv_path, stylesheets=[CSS(string=cv.css)])
    await save_document_to_file(
        path=path, file_name=f"{file_name}.html", data=cv.html
    )
    await save_document_to_file(
        path=path, file_name=f"{file_name}.css", data=cv.css
    )

    return cv_path.as_uri()


async def generate_career_documents(
    user: UserModel,
    session: Session,
    job_entry: JobEntry,
    current_time: str,
    cv_creation_mode: CVCreationModeEnum,
    generate_cover_letter: bool,
) -> JobEntryModel:
    if not os.path.isdir(settings.CV_DIR_PATH):
        os.mkdir(settings.CV_DIR_PATH)

    converted_title = job_entry.title.replace(" ", "").replace("/", "_")
    documents_path = settings.CV_DIR_PATH / f"{converted_title}_{current_time}"
    os.mkdir(documents_path)

    job_entry.cv_path = await create_cv(
        user=user,
        session=session,
        job_entry=job_entry,
        converted_title=converted_title,
        current_time=current_time,
        path=documents_path,
        cv_creation_mode=cv_creation_mode,
    )
    if generate_cover_letter:
        job_entry.cover_letter_path = await create_cover_letter(
            user=user,
            session=session,
            job_entry=job_entry,
            converted_title=converted_title,
            current_time=current_time,
            path=documents_path,
        )
    job_entry_model = save_job_entry(
        session=session, user=user, job_entry=job_entry
    )
    return job_entry_model
