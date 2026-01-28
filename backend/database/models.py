import datetime
from typing import Any, Self

# from pydantic_ai.models import KnownModelName
from pydantic import EmailStr, Json
from sqlmodel import JSON, Column, Field, SQLModel, Session, select

from backend.schemas.models import CVCreationModeEnum


class BaseDatabaseModel(SQLModel):
    id: int | None = Field(default=None, primary_key=True, index=True)


class BaseUserConnectedData(BaseDatabaseModel):
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )

    @classmethod
    def read_all(cls, session: Session, user_id: int | None) -> list[Self]:
        if not user_id:
            return list()

        rows = session.exec(
            select(cls.__class__).where(cls.__class__.user_id == user_id)
        ).all()
        return list(rows)

    def save(
        self,
        session: Session,
        user_id: int,
    ) -> None:
        self.user_id = user_id
        session.add(self)
        session.commit()
        session.refresh(self)

    def delete(self, session: Session) -> None:
        session.delete(
            session.exec(
                select(self.__class__).where(self.__class__.id == self.id)
            ).one()
        )
        session.commit()

    def update(self, session: Session, **kwargs) -> None:
        for key, val in kwargs.items():
            setattr(self, key, val)
        session.add(self)
        session.commit()


# TODO: Add priority to each category of skills and qualifications, so that the system can decide what should go into cv
# TODO: How to recognise duplicate job offers on a different sites and on the same site at different time
# Maybe try using normalization of several job information e.g. title, company name and part of description and fuzzy matching
# https://github.com/rapidfuzz/RapidFuzz
class JobEntryModel(BaseUserConnectedData, table=True):
    cv_path: str = ""
    cover_letter_path: str = ""
    title: str
    company_name: str
    discovery_date: datetime.date = Field(default_factory=datetime.date.today)
    job_url: str
    requirements: str
    duties: str
    about_project: str
    offer_benefits: str
    location: str
    contract_type: str
    employment_type: str
    work_arrangement: str
    additional_information: None | str
    company_url: (
        None | str
    )  # TODO: Here LLM will need to find information on the internet


class UserModel(BaseDatabaseModel, table=True):
    email: EmailStr = Field(unique=True, max_length=255)
    phone_number: str
    first_name: str
    middle_name: str
    surname: str
    age: str | None


class UserPreferencesModel(BaseUserConnectedData, table=True):
    cv_creation_mode: CVCreationModeEnum
    generate_cover_letter: bool
    cv_path: str
    retries: int = 3


class WebsiteModel(BaseUserConnectedData, table=True):
    cookies: str
    user_email: EmailStr
    user_password: str
    url: str
    automation_steps: Json[Any] | None = Field(
        sa_column=Column(JSON), default_factory=dict
    )
    # scarping_llm_model: KnownModelName
    # documents_llm_model: KnownModelName


class LocationModel(BaseUserConnectedData, table=True):
    country: str
    state: str
    city: str
    zip_code: str


class ProgrammingLanguageModel(BaseUserConnectedData, table=True):
    programming_language: str
    level: str  # Maybe in the future change to int


class LanguageModel(BaseUserConnectedData, table=True):
    language: str
    level: str  # Maybe in the future change to int


class ToolModel(BaseUserConnectedData, table=True):
    tool: str
    level: str  # Maybe in the future change to int


class CertificateModel(BaseUserConnectedData, table=True):
    certificate: str
    description: str
    organisation: str


class CharityModel(BaseUserConnectedData, table=True):
    charity: str
    description: str
    organisation: str
    start_date: datetime.date | None = Field(default=None)
    end_date: datetime.date | None = Field(default=None)


class EducationModel(BaseUserConnectedData, table=True):
    school: str
    major: str
    description: str
    start_date: datetime.date | None = Field(default=None)
    end_date: datetime.date | None = Field(default=None)


class ExperienceModel(BaseUserConnectedData, table=True):
    company: str
    position: str
    description: str
    start_date: datetime.date | None = Field(default=None)
    end_date: datetime.date | None = Field(default=None)


class ProjectModel(BaseUserConnectedData, table=True):
    project: str
    description: str
    url: str


class SocialPlatformModel(BaseUserConnectedData, table=True):
    social_platform: str
    url: str
