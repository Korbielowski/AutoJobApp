from typing import Union

from devtools import pformat
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select

from backend.config import settings
from backend.database.models import (
    BaseUserConnectedData,
    CertificateModel,
    CharityModel,
    EducationModel,
    ExperienceModel,
    JobBoardWebsiteModel,
    LanguageModel,
    LocationModel,
    ProgrammingLanguageModel,
    ProjectModel,
    SocialPlatformModel,
    ToolModel,
    UserModel,
    UserPreferencesModel,
)
from backend.database.repositories import (
    CertificateRepository,
    CharityRepository,
    DataRepository,
    EducationRepository,
    ExperienceRepository,
    JobBoardWebsiteRepository,
    LanguageRepository,
    LocationRepository,
    ProgrammingLanguageRepository,
    ProjectRepository,
    SocialPlatformRepository,
    ToolRepository,
    UserPreferencesRepository,
    UserRepository,
)
from backend.logger import get_logger
from backend.routes.deps import (
    CurrentUser,
    SessionDep,
    set_current_user,
)
from backend.schemas.endpoints import (
    CertificatePost,
    CharityPost,
    DeleteItem,
    EducationPost,
    ExperiencePost,
    LanguagePost,
    LocationPost,
    ProfileInfo,
    ProgrammingLanguagePost,
    ProjectPost,
    SocialPlatformPost,
    ToolPost,
    WebsitePost,
)
from backend.schemas.models import (
    Certificate,
    Charity,
    CVCreationModeEnum,
    Education,
    Experience,
    JobBoardWebsite,
    Language,
    Location,
    ProgrammingLanguage,
    Project,
    SocialPlatform,
    Tool,
)

REPO_MAP: dict[str, type[DataRepository]] = {
    "location": LocationRepository,
    "programmingLanguage": ProgrammingLanguageRepository,
    "language": LanguageRepository,
    "tool": ToolRepository,
    "certificate": CertificateRepository,
    "charity": CharityRepository,
    "education": EducationRepository,
    "experience": ExperienceRepository,
    "project": ProjectRepository,
    "socialPlatform": SocialPlatformRepository,
    "website": JobBoardWebsiteRepository,
}
MODEL_MAP: dict[str, type[BaseUserConnectedData]] = {
    "Location": LocationModel,
    "ProgrammingLanguage": ProgrammingLanguageModel,
    "Language": LanguageModel,
    "Tool": ToolModel,
    "Certificate": CertificateModel,
    "Charity": CharityModel,
    "Education": EducationModel,
    "Experience": ExperienceModel,
    "Project": ProjectModel,
    "SocialPlatform": SocialPlatformModel,
    "Website": JobBoardWebsiteModel,
}
router = APIRouter(tags=["users"])
templates = Jinja2Templates(settings.ROOT_DIR / "templates")
logger = get_logger()


@router.get("/login", response_class=HTMLResponse)
async def load_login_page(
    user: CurrentUser, session: SessionDep, request: Request
):
    users = UserRepository().get_users(session)
    if not users:
        return RedirectResponse(
            url=request.url_for("load_register_page"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"user": user, "users": users},
    )


@router.post("/login", response_class=RedirectResponse)
async def login(session: SessionDep, request: Request, email: str = Form(...)):
    # TODO: Get current profile in other/better way ;)
    set_current_user(session, email)
    return RedirectResponse(
        url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/logout", response_class=RedirectResponse)
async def logout(session: SessionDep, request: Request):
    set_current_user(session, None)
    return RedirectResponse(
        url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/register", response_class=Union[RedirectResponse, HTMLResponse])
async def load_register_page(
    user: CurrentUser, session: SessionDep, request: Request
):
    users = UserRepository().get_users(session)
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"user": user, "users": users},
    )


@router.post("/register", response_class=RedirectResponse)
async def register(
    session: SessionDep,
    request: Request,
    form_data: ProfileInfo,  # form: Annotated[TestInfo, Form()]
):
    logger.info(f"form_data: {pformat(form_data)}")

    user_repo = UserRepository()
    user = user_repo.create(
        session, UserModel.model_validate(form_data.profile)
    )

    form_dump = form_data.model_dump()
    form_dump.pop("profile")

    for key, val in form_dump.items():
        for v in val:
            model = MODEL_MAP[key].model_validate(v)
            repo = REPO_MAP[key]()
            repo.create(session=session, obj=model)

    UserPreferencesRepository().create(
        session=session,
        obj=UserPreferencesModel(
            user_id=user.id,
            cv_creation_mode=CVCreationModeEnum.llm_generation,
            generate_cover_letter=False,
            cv_path="",
            retries=3,
        ),
    )

    set_current_user(session, user.email)

    return RedirectResponse(
        url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/account", response_class=Union[HTMLResponse, RedirectResponse])
async def account_details(
    current_user: CurrentUser, session: SessionDep, request: Request
):
    if not current_user.id:
        return RedirectResponse(
            url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER
        )
    user_id = current_user.id
    # Load all user connected data into context
    context = {
        key: val().read_all(session, user_id) for key, val in REPO_MAP.items()
    }
    return templates.TemplateResponse(
        request=request, name="account.html", context=context
    )


@router.post(
    "/delete_account", response_class=Union[HTMLResponse, RedirectResponse]
)
async def delete_account(
    session: SessionDep, request: Request, email: str = Form(...)
):  # TODO: Try using EmailStr instead of plain str
    UserRepository().delete_user(session, email)
    set_current_user(session, None)

    return RedirectResponse(
        url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/add_new_information_to_account")
async def add_new_information_to_account(
    user: CurrentUser,
    session: SessionDep,
    form_data: Union[
        Location,
        ProgrammingLanguage,
        Language,
        Tool,
        Certificate,
        Charity,
        Education,
        Experience,
        Project,
        SocialPlatform,
        JobBoardWebsite,
    ],
):
    form_dump = form_data.model_dump()
    logger.debug(f"Model sent for 'create' operation: {form_dump}")

    validator = MODEL_MAP[form_data.__class__.__name__]
    model = validator.model_validate(form_dump)

    model.user_id = user.id
    session.add(model)
    session.commit()
    session.refresh(model)

    return model


@router.post("/edit_information_about_account", response_class=JSONResponse)
async def edit_information_about_account(
    session: SessionDep,
    form_data: Union[
        LocationPost,
        ProgrammingLanguagePost,
        LanguagePost,
        ToolPost,
        CertificatePost,
        CharityPost,
        EducationPost,
        ExperiencePost,
        ProjectPost,
        SocialPlatformPost,
        WebsitePost,
    ],
):
    d = {
        "LocationPost": LocationModel,
        "ProgrammingLanguagePost": ProgrammingLanguageModel,
        "LanguagePost": LanguageModel,
        "ToolPost": ToolModel,
        "CertificatePost": CertificateModel,
        "CharityPost": CharityModel,
        "EducationPost": EducationModel,
        "ExperiencePost": ExperienceModel,
        "ProjectPost": ProjectModel,
        "SocialPlatformPost": SocialPlatformModel,
        "WebsitePost": JobBoardWebsiteModel,
    }

    form_dump = form_data.model_dump()
    logger.debug(f"Model sent for 'update' operation: {form_dump}")

    model_class = d[form_data.__class__.__name__]
    model_to_update = session.exec(
        select(model_class).where(model_class.id == form_data.id)
    ).one()

    model_to_update.sqlmodel_update(form_dump)
    session.add(model_to_update)
    session.commit()
    session.refresh(model_to_update)

    logger.info(f"Model to be returned: {pformat(model_to_update)}")
    return model_to_update


@router.get("/manage_users", response_class=HTMLResponse)
async def load_manage_users_page(
    user: CurrentUser, session: SessionDep, request: Request
):
    return templates.TemplateResponse(
        request=request,
        name="manage_users.html",
        context={"user": user, "users": UserRepository().get_users(session)},
    )


@router.delete("/delete")
async def delete_item(
    user: CurrentUser, session: SessionDep, request: Request, item: DeleteItem
):
    if item.item_type == "user":
        UserRepository().delete_user(session, user.email)
        set_current_user(session=session, email=None)
        return RedirectResponse(
            url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER
        )

    REPO_MAP[item.item_type]().delete(session, item.item_id)
