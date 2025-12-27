from typing import Sequence, TypeVar

from sqlmodel import Session, SQLModel, select

from backend.database.models import (
    CertificateModel,
    CharityModel,
    EducationModel,
    ExperienceModel,
    JobEntryModel,
    LanguageModel,
    LocationModel,
    ProgrammingLanguageModel,
    ProjectModel,
    SocialPlatformModel,
    ToolModel,
    UserModel,
    UserPreferencesModel,
    WebsiteModel,
)
from backend.logger import get_logger
from backend.schemas.models import (
    CandidateData,
    Certificate,
    Charity,
    Education,
    Experience,
    JobEntry,
    Language,
    Location,
    ProgrammingLanguage,
    Project,
    SocialPlatform,
    Tool,
    User,
    UserNeeds,
    UserPreferences,
    Website,
)

logger = get_logger()
T = TypeVar("T", bound=SQLModel)


def create_user(session: Session, user: UserModel) -> UserModel:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user(session: Session, email: str) -> None:
    session.delete(
        session.exec(select(UserModel).where(UserModel.email == email)).first()
    )
    session.commit()


def get_user_preferences(
    session: Session, user: UserModel, use_base_model: bool = False
) -> UserPreferencesModel | UserPreferences:
    output = session.exec(
        select(UserPreferencesModel).where(
            UserPreferencesModel.user_id == user.id
        )
    ).one()
    if use_base_model:
        return output
    return UserPreferences.model_validate(output.model_dump())


def update_user_preferences(
    session: Session, user: UserModel, model: UserPreferencesModel
):
    record = session.exec(
        select(UserPreferencesModel).where(
            UserPreferencesModel.user_id == user.id
        )
    ).first()
    if not record:
        save_model(session=session, user=user, model=model)
        return

    # record.sqlmodel_update(model.model_dump())
    record.cv_creation_mode = model.cv_creation_mode
    record.generate_cover_letter = model.generate_cover_letter
    record.cv_path = model.cv_path
    record.retries = record.retries
    session.add(record)
    session.commit()


def get_users(
    session: Session, use_base_model: bool = False
) -> Sequence[User] | Sequence[UserModel]:
    output = session.exec(select(UserModel)).all()
    if use_base_model:
        return output
    return [User.model_validate(element.model_dump()) for element in output]


def get_locations(
    session: Session, user: UserModel, use_base_model: bool = False
) -> Sequence[Location] | Sequence[LocationModel]:
    output = session.exec(
        select(LocationModel).where(LocationModel.user_id == user.id)
    ).all()
    if use_base_model:
        return output
    return [Location.model_validate(element.model_dump()) for element in output]


def get_programming_languages(
    session: Session, user: UserModel, use_base_model: bool = False
) -> Sequence[ProgrammingLanguage] | Sequence[ProgrammingLanguageModel]:
    output = session.exec(
        select(ProgrammingLanguageModel).where(
            ProgrammingLanguageModel.user_id == user.id
        )
    ).all()
    if use_base_model:
        return output
    return [
        ProgrammingLanguage.model_validate(element.model_dump())
        for element in output
    ]


def get_languages(
    session: Session, user: UserModel, use_base_model: bool = False
) -> Sequence[Language] | Sequence[LanguageModel]:
    output = session.exec(
        select(LanguageModel).where(LanguageModel.user_id == user.id)
    ).all()
    if use_base_model:
        return output
    return [Language.model_validate(element.model_dump()) for element in output]


def get_tools(
    session: Session, user: UserModel, use_base_model: bool = False
) -> Sequence[Tool] | Sequence[ToolModel]:
    output = session.exec(
        select(ToolModel).where(ToolModel.user_id == user.id)
    ).all()
    if use_base_model:
        return output
    return [Tool.model_validate(element.model_dump()) for element in output]


def get_certificates(
    session: Session, user: UserModel, use_base_model: bool = False
) -> Sequence[Certificate] | Sequence[CertificateModel]:
    output = session.exec(
        select(CertificateModel).where(CertificateModel.user_id == user.id)
    ).all()
    if use_base_model:
        return output
    return [
        Certificate.model_validate(element.model_dump()) for element in output
    ]


def get_experiences(
    session: Session, user: UserModel, use_base_model: bool = False
) -> Sequence[Experience] | Sequence[ExperienceModel]:
    output = session.exec(
        select(ExperienceModel).where(ExperienceModel.user_id == user.id)
    ).all()
    if use_base_model:
        return output
    return [
        Experience.model_validate(element.model_dump()) for element in output
    ]


def get_charities(
    session: Session, user: UserModel, use_base_model: bool = False
) -> Sequence[Charity] | Sequence[CharityModel]:
    output = session.exec(
        select(CharityModel).where(CharityModel.user_id == user.id)
    ).all()
    if use_base_model:
        return output
    return [Charity.model_validate(element.model_dump()) for element in output]


def get_educations(
    session: Session, user: UserModel, use_base_model: bool = False
) -> Sequence[Education] | Sequence[EducationModel]:
    output = session.exec(
        select(EducationModel).where(EducationModel.user_id == user.id)
    ).all()
    if use_base_model:
        return output
    return [
        Education.model_validate(element.model_dump()) for element in output
    ]


def get_social_platforms(
    session: Session, user: UserModel, use_base_model: bool = False
) -> Sequence[SocialPlatform] | Sequence[SocialPlatformModel]:
    output = session.exec(
        select(SocialPlatformModel).where(
            SocialPlatformModel.user_id == user.id
        )
    ).all()
    if use_base_model:
        return output
    return [
        SocialPlatform.model_validate(element.model_dump())
        for element in output
    ]


def get_projects(
    session: Session, user: UserModel, use_base_model: bool = False
) -> Sequence[Project] | Sequence[ProjectModel]:
    output = session.exec(
        select(ProjectModel).where(ProjectModel.user_id == user.id)
    ).all()
    if use_base_model:
        return output
    return [Project.model_validate(element.model_dump()) for element in output]


def get_websites(
    session: Session, user: UserModel, use_base_model: bool = False
) -> Sequence[Website] | Sequence[WebsiteModel]:
    output = session.exec(
        select(WebsiteModel).where(WebsiteModel.user_id == user.id)
    ).all()
    if use_base_model:
        return output
    return [Website.model_validate(element.model_dump()) for element in output]


def get_job_entries(
    session: Session, user: UserModel, use_base_model: bool = False
) -> Sequence[JobEntry] | Sequence[JobEntryModel]:
    output = session.exec(
        select(JobEntryModel).where(JobEntryModel.user_id == user.id)
    ).all()
    if use_base_model:
        return output
    return [JobEntry.model_validate(element.model_dump()) for element in output]


def get_candidate_data(session: Session, user: UserModel) -> CandidateData:
    locations = get_locations(session=session, user=user)
    programming_languages = get_programming_languages(
        session=session, user=user
    )
    languages = get_languages(session=session, user=user)
    tools = get_tools(session=session, user=user)
    certificates = get_certificates(session=session, user=user)
    experiences = get_experiences(session=session, user=user)
    charities = get_charities(session=session, user=user)
    educations = get_educations(session=session, user=user)
    social_platforms = get_social_platforms(session=session, user=user)
    full_name = (
        f"{user.first_name} {user.middle_name} {user.surname}"
        if user.middle_name
        else f"{user.first_name} {user.surname}"
    )
    projects = get_projects(session=session, user=user)
    return CandidateData(
        full_name=full_name,
        email=user.email,
        phone_number=user.phone_number,
        locations=locations,
        programming_languages=programming_languages,
        languages=languages,
        tools=tools,
        certificates=certificates,
        charities=charities,
        educations=educations,
        experiences=experiences,
        projects=projects,
        social_platforms=social_platforms,
    )


def get_user_needs(session: Session, user: UserModel) -> UserNeeds:
    locations = get_locations(session=session, user=user)
    programming_languages = get_programming_languages(
        session=session, user=user
    )
    languages = get_languages(session=session, user=user)
    tools = get_tools(session=session, user=user)
    certificates = get_certificates(session=session, user=user)
    experiences = get_experiences(session=session, user=user)
    projects = get_projects(session=session, user=user)
    return UserNeeds(
        locations=locations,
        programming_languages=programming_languages,
        languages=languages,
        tools=tools,
        certificates=certificates,
        experiences=experiences,
        projects=projects,
    )


def save_job_entry(
    session: Session, user: UserModel, job_entry: JobEntry
) -> JobEntryModel:
    job_entry_model = JobEntryModel.model_validate(job_entry.model_dump())
    job_entry_model.user_id = user.id
    session.add(job_entry_model)
    session.commit()
    session.refresh(job_entry_model)
    return job_entry_model


def save_model(
    session: Session,
    user: UserModel,
    model: T,
    validator: type[T] | None = None,
) -> None:
    if validator:
        model = validator.model_validate(model.model_dump())
    model.user_id = user.id
    session.add(model)
    session.commit()


def save_and_return_model(
    session: Session,
    user: UserModel,
    model: T,
    validator: type[T] | None = None,
) -> T:
    if validator:
        model = validator.model_validate(model.model_dump())
    model.user_id = user.id
    session.add(model)
    session.commit()
    session.refresh(model)
    return model
