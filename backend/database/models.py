import datetime

from pydantic import EmailStr
from sqlmodel import JSON, Column, Field, SQLModel

from backend.schemas.models import AutomationSteps, CVCreationModeEnum


# TODO: Add priority to each category of skills and qualifications, so that the system can decide what should go into cv
# TODO: How to recognise duplicate job offers on a different sites and on the same site at different time
# Maybe try using normalization of several job information e.g. title, company name and part of description and fuzzy matching
# https://github.com/rapidfuzz/RapidFuzz
class JobEntryModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
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


class UserModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True, max_length=255)
    phone_number: str
    first_name: str
    middle_name: str
    surname: str
    age: str | None


class UserPreferencesModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    cv_creation_mode: CVCreationModeEnum
    generate_cover_letter: bool
    cv_path: str
    retries: int = 3


class WebsiteModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    cookies: str
    user_email: EmailStr
    user_password: str
    url: str
    automation_steps: AutomationSteps | None = Field(
        sa_column=Column(JSON), default_factory=dict
    )


class LocationModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    country: str
    state: str
    city: str
    zip_code: str


class ProgrammingLanguageModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    programming_language: str
    level: str  # Maybe in the future change to int


class LanguageModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    language: str
    level: str  # Maybe in the future change to int


class ToolModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    tool: str
    level: str  # Maybe in the future change to int


class CertificateModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    certificate: str
    description: str
    organisation: str


class CharityModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    charity: str
    description: str
    organisation: str
    start_date: datetime.date | None = Field(default=None)
    end_date: datetime.date | None = Field(default=None)


class EducationModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    school: str
    major: str
    description: str
    start_date: datetime.date | None = Field(default=None)
    end_date: datetime.date | None = Field(default=None)


class ExperienceModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    company: str
    position: str
    description: str
    start_date: datetime.date | None = Field(default=None)
    end_date: datetime.date | None = Field(default=None)


class ProjectModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    project: str
    description: str
    url: str


class SocialPlatformModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    social_platform: str
    url: str
