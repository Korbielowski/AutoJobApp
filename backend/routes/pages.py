import os.path
from typing import Annotated, Union

import aiofiles
from fastapi import APIRouter, File, Form, Request, UploadFile, status
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    StreamingResponse,
)
from fastapi.templating import Jinja2Templates
from sqlmodel import func

from backend.config import settings
from backend.database.crud import (
    get_job_entries,
    get_user_needs,
    get_user_preferences,
    get_websites,
    save_model,
)
from backend.database.models import (
    CVCreationModeEnum,
    UserModel,
    UserPreferencesModel,
)
from backend.logger import get_logger
from backend.routes.deps import CurrentUser, SessionDep
from backend.scrapers import find_job_entries

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(settings.ROOT_DIR / "templates")
logger = get_logger()


@router.get("/", response_class=Union[RedirectResponse, HTMLResponse])
async def index(user: CurrentUser, session: SessionDep, request: Request):
    if not user:
        if session.scalar(func.count(UserModel.id)) >= 1:
            return RedirectResponse(
                url=request.url_for("load_login_page"),
                status_code=status.HTTP_303_SEE_OTHER,
            )
        return RedirectResponse(
            url=request.url_for("load_register_page"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    scraped_job_entries = get_job_entries(session, user)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user": user,
            "scraped_job_entries": scraped_job_entries,
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
    save_model(session=session, user=user, model=preferences_model)


@router.get("/scrape_jobs", response_class=StreamingResponse)
async def scrape_jobs(user: CurrentUser, session: SessionDep):
    websites = get_websites(session=session, user=user, use_base_model=True)
    user_preferences = get_user_preferences(session=session, user=user)
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
