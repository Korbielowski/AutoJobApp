import os.path
from typing import Annotated, Union

import aiofiles
from devtools import pformat
from fastapi import (
    APIRouter,
    File,
    Form,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import func

from backend.config import settings
from backend.database.models import (
    CVCreationModeEnum,
    UserModel,
    UserPreferencesModel,
)
from backend.database.repositories.job_board_website import (
    JobBoardWebsiteRepository,
)
from backend.database.repositories.job_entry import JobEntryRepository
from backend.database.repositories.user_preferences import (
    UserPreferencesRepository,
)
from backend.database.repositories.utils import get_user_needs
from backend.logger import get_logger
from backend.routes.deps import CurrentUser, SessionDep
from backend.schemas.models import UserPreferences
from backend.scrapers import find_job_entries

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(settings.ROOT_DIR / "templates")
logger = get_logger()


@router.get("/", response_class=Union[RedirectResponse, HTMLResponse])
async def index(user: CurrentUser, session: SessionDep, request: Request):
    if not user.id:
        if session.scalar(func.count(UserModel.id)) >= 1:
            return RedirectResponse(
                url=request.url_for("load_login_page"),
                status_code=status.HTTP_303_SEE_OTHER,
            )
        return RedirectResponse(
            url=request.url_for("load_register_page"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    scraped_job_entries = JobEntryRepository().read_all(session, user.id)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user": user,
            "scraped_job_entries": scraped_job_entries,
            "key_exists": True if settings.OPENAI_API_KEY else False,
        },
    )


async def save_user_cv(cv_file: UploadFile) -> str:
    file_path = ""
    if cv_file.size:
        logger.info(cv_file.filename)
        path = settings.CV_DIR_PATH / "user_specified_cv"
        if not os.path.isdir(path):
            os.mkdir(path)
            file_name = (
                cv_file.filename
                if cv_file.filename
                else "user_specified_cv.pdf"
            )
            file_path = (path / file_name).as_uri()
            if not os.path.isfile(file_path):
                async with aiofiles.open(file_path, "wb") as save_file:
                    await save_file.write(await cv_file.read())
    return file_path


@router.post("/save_preferences")
async def save_preferences(
    user: CurrentUser,
    session: SessionDep,
    cv_creation_mode: Annotated[CVCreationModeEnum, Form()],
    retries: Annotated[int, Form()],
    cv_file: Annotated[UploadFile, File],
    generate_cover_letter: Annotated[bool, Form()] = False,
):
    preferences_model = UserPreferencesModel(
        cv_creation_mode=cv_creation_mode,
        generate_cover_letter=generate_cover_letter,
        cv_path=await save_user_cv(cv_file),
        retries=retries,
    )
    repo = UserPreferencesRepository()
    db_preferences_model = repo.read_one_by_user_id(session, user.id)
    repo.update(session, db_preferences_model, **preferences_model.model_dump())


@router.get("/scrape_jobs", response_class=StreamingResponse)
async def scrape_jobs(user: CurrentUser, session: SessionDep):
    job_board_website_repo = JobBoardWebsiteRepository()
    websites = job_board_website_repo.read_all(session=session, user_id=user.id)
    user_preferences_repository = UserPreferencesRepository()

    x = user_preferences_repository.read_one_by_user_id(
        session=session, user_id=user.id
    ).model_dump()
    logger.error(pformat(x))
    user_preferences = UserPreferences.model_validate(x)
    user_needs = get_user_needs(session=session, user=user)
    return StreamingResponse(
        content=find_job_entries(
            user=user,
            session=session,
            websites=websites,
            user_preferences=user_preferences,
            user_needs=user_needs,
        ),
        media_type="text/event-stream",
    )


# TODO: In the future
# @router.post("/download_cv", response_class=FileResponse)
# async def download_cv(request: Request, path: str):
#     return FileResponse(path=path)
#


@router.get("/cv_page", response_class=HTMLResponse)
async def cv_page(
    current_user: CurrentUser, session: SessionDep, request: Request
):
    return


@router.get("/upload_cv", response_class=HTMLResponse)
async def upload_cv(
    current_user: CurrentUser, session: SessionDep, request: Request
):
    return
    # return templates.TemplateResponse(
    #     request=request, name="cv_page.html", context={"user": current_user}
    # )
