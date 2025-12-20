from typing import Union

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select

from backend.config import settings
from backend.database.crud import (
    create_user,
    delete_user,
    get_certificates,
    get_charities,
    get_educations,
    get_experiences,
    get_languages,
    get_locations,
    get_programming_languages,
    get_projects,
    get_social_platforms,
    get_tools,
    get_users,
    get_websites,
)
from backend.database.models import (
    CertificateModel,
    CharityModel,
    EducationModel,
    ExperienceModel,
    LanguageModel,
    LocationModel,
    ProgrammingLanguageModel,
    ProjectModel,
    SocialPlatformModel,
    ToolModel,
    UserModel,
    WebsiteModel,
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
    Education,
    Experience,
    Language,
    Location,
    ProgrammingLanguage,
    Project,
    SocialPlatform,
    Tool,
    Website,
)

router = APIRouter(tags=["users"])
templates = Jinja2Templates(settings.ROOT_DIR / "templates")
logger = get_logger()


@router.get("/login", response_class=HTMLResponse)
async def load_login_page(session: SessionDep, request: Request):
    users = get_users(session=session, use_base_model=True)
    if not users:
        return RedirectResponse(
            url=request.url_for("load_register_page"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return templates.TemplateResponse(
        request=request, name="login.html", context={"users": users}
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
async def load_register_page(current_user: CurrentUser, request: Request):
    return templates.TemplateResponse(
        request=request, name="register.html", context={"user": current_user}
    )


@router.post("/register", response_class=RedirectResponse)
async def register(
    session: SessionDep,
    request: Request,
    form_data: ProfileInfo,  # form: Annotated[TestInfo, Form()]
):
    d = {
        "locations": LocationModel,
        "programming_languages": ProgrammingLanguageModel,
        "languages": LanguageModel,
        "tools": ToolModel,
        "certificates": CertificateModel,
        "charities": CharityModel,
        "educations": EducationModel,
        "experience": ExperienceModel,
        "projects": ProjectModel,
        "social_platforms": SocialPlatformModel,
        "websites": WebsiteModel,
    }
    form_dump = form_data.model_dump()
    user = UserModel.model_validate(form_dump.get("profile"))

    models = []
    for key, val in d.items():
        tmp = form_dump.get(key, [])
        for t in tmp:
            models.append(val.model_validate(t))

    user = create_user(session, user)

    for model in models:
        model.user_id = user.id
        session.add(model)
    session.commit()

    set_current_user(session, user.email)

    return RedirectResponse(
        url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/account", response_class=Union[HTMLResponse, RedirectResponse])
async def account_details(
    current_user: CurrentUser, session: SessionDep, request: Request
):
    if not current_user:
        return RedirectResponse(
            url=request.url_for("index"), status_code=status.HTTP_303_SEE_OTHER
        )
    context = {
        "user": current_user,
        "locations": get_locations(
            session=session, user=current_user, use_base_model=True
        ),
        "programming_languages": get_programming_languages(
            session=session, user=current_user, use_base_model=True
        ),
        "languages": get_languages(
            session=session, user=current_user, use_base_model=True
        ),
        "tools": get_tools(
            session=session, user=current_user, use_base_model=True
        ),
        "certificates": get_certificates(
            session=session, user=current_user, use_base_model=True
        ),
        "charities": get_charities(
            session=session, user=current_user, use_base_model=True
        ),
        "educations": get_educations(
            session=session, user=current_user, use_base_model=True
        ),
        "experiences": get_experiences(
            session=session, user=current_user, use_base_model=True
        ),
        "projects": get_projects(
            session=session, user=current_user, use_base_model=True
        ),
        "social_platforms": get_social_platforms(
            session=session, user=current_user, use_base_model=True
        ),
        "websites": get_websites(
            session=session, user=current_user, use_base_model=True
        ),
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
    delete_user(session, email)
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
        Website,
    ],
):
    d = {
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
        "Website": WebsiteModel,
    }
    form_dump = form_data.model_dump()
    logger.debug(f"Model sent for 'create' operation: {form_dump}")

    validator = d[form_data.__class__.__name__]
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
        "WebsitePost": WebsiteModel,
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

    return model_to_update


@router.get("/manage_users", response_class=HTMLResponse)
async def load_manage_users_page(
    user: CurrentUser, session: SessionDep, request: Request
):
    return templates.TemplateResponse(
        request=request,
        name="manage_users.html",
        context={
            "user": user,
            "users": get_users(session, use_base_model=True),
        },
    )
