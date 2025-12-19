import datetime
from enum import StrEnum
from typing import Annotated, Callable

from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr
from sqlmodel import JSON, Column, Field, SQLModel

# TODO: Add model for storing all of the users preferences regarding scraping, cv creation and applying

# TODO: Add priority to each category of skills and qualifications, so that the system can decide what should go into cv


def ensure_date(value: str | datetime.date):
    if isinstance(value, str):
        return datetime.date.fromisoformat(value)
    return value


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


class JobEntry(BaseModel):
    cv_path: str = ""
    cover_letter_path: str = ""
    title: str
    company_name: str
    discovery_date: datetime.date
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
    company_url: None | str


class AttributeType(StrEnum):
    id = "id"
    text = "text"
    aria_label = "aria_label"
    name = "name"
    element_type = "element_type"
    class_l = "class_l"


class Step(BaseModel):
    action: Callable
    html_element_attribute: str  # TODO: Experiment with Locators too if you can
    attribute_type: AttributeType
    arguments: dict


class AutomationSteps(BaseModel):
    login_to_page: list[Step]
    is_on_login_page: list[Step]
    navigate_to_login_page: list[Step]
    pass_cookies_popup: list[Step]
    navigate_to_job_list: list[Step]
    get_job_entries: list[Step]
    navigate_to_next_page: list[Step]
    # TODO: Uncomment if this function gets html elements get_job_information: list[Step]


class UserModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True, max_length=255)
    phone_number: str
    first_name: str
    middle_name: str
    surname: str
    age: str | None


class User(BaseModel):
    email: EmailStr
    phone_number: str
    first_name: str
    middle_name: str
    surname: str
    age: str | None


class CVCreationModeEnum(StrEnum):
    llm_generation = "llm-generation"
    llm_selection = "llm-selection"
    no_llm_generation = "no-llm-generation"
    user_specified = "user-specified"


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


class WebsitePost(BaseModel):
    id: int
    user_id: int
    cookies: str
    user_email: EmailStr
    user_password: str
    url: str
    automation_steps: AutomationSteps | None

    model_config = ConfigDict(strict=True)


class Website(BaseModel):
    cookies: str
    user_email: EmailStr
    user_password: str
    url: str
    automation_steps: AutomationSteps | None


class LocationModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    country: str
    state: str
    city: str
    zip_code: str


class LocationPost(BaseModel):
    id: int
    user_id: int
    country: str
    state: str
    city: str
    zip_code: str

    model_config = ConfigDict(strict=True)


class Location(BaseModel):
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


class ProgrammingLanguagePost(BaseModel):
    id: int
    user_id: int
    programming_language: str
    level: str  # Maybe in the future change to int

    model_config = ConfigDict(strict=True)


class ProgrammingLanguage(BaseModel):
    programming_language: str
    level: str  # Maybe in the future change to int


class LanguageModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    language: str
    level: str  # Maybe in the future change to int


class LanguagePost(BaseModel):
    id: int
    user_id: int
    language: str
    level: str

    model_config = ConfigDict(strict=True)


class Language(BaseModel):
    language: str
    level: str  # Maybe in the future change to int


class ToolModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    tool: str
    level: str  # Maybe in the future change to int


class ToolPost(BaseModel):
    id: int
    user_id: int
    tool: str
    level: str

    model_config = ConfigDict(strict=True)


class Tool(BaseModel):
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


class CertificatePost(BaseModel):
    id: int
    user_id: int
    certificate: str
    description: str
    organisation: str

    model_config = ConfigDict(strict=True)


class Certificate(BaseModel):
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


class CharityPost(BaseModel):
    id: int
    user_id: int
    charity: str
    description: str
    organisation: str
    start_date: Annotated[datetime.date, BeforeValidator(ensure_date)]
    end_date: Annotated[datetime.date, BeforeValidator(ensure_date)]

    model_config = ConfigDict(strict=True)


class Charity(BaseModel):
    charity: str
    description: str
    organisation: str
    start_date: datetime.date | None
    end_date: datetime.date | None


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


class EducationPost(BaseModel):
    id: int
    user_id: int
    school: str
    major: str
    description: str
    start_date: Annotated[datetime.date, BeforeValidator(ensure_date)]
    end_date: Annotated[datetime.date, BeforeValidator(ensure_date)]

    model_config = ConfigDict(strict=True)


class Education(BaseModel):
    school: str
    major: str
    description: str
    start_date: datetime.date | None
    end_date: datetime.date | None


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


class ExperiencePost(BaseModel):
    id: int
    user_id: int
    company: str
    position: str
    description: str
    start_date: Annotated[datetime.date, BeforeValidator(ensure_date)]
    end_date: Annotated[datetime.date, BeforeValidator(ensure_date)]

    model_config = ConfigDict(strict=True)


class Experience(BaseModel):
    company: str
    position: str
    description: str
    start_date: datetime.date | None
    end_date: datetime.date | None


class ProjectModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="usermodel.id", ondelete="CASCADE"
    )
    project: str
    description: str
    url: str


class ProjectPost(BaseModel):
    id: int
    user_id: int
    project: str
    description: str
    url: str

    model_config = ConfigDict(strict=True)


class Project(BaseModel):
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


class SocialPlatformPost(BaseModel):
    id: int
    user_id: int
    social_platform: str
    url: str

    model_config = ConfigDict(strict=True)


class SocialPlatform(BaseModel):
    social_platform: str
    url: str


class ProfileInfo(BaseModel):
    profile: User
    locations: (
        list[Location] | None
    )  # TODO: Maybe make this field a priority list
    programming_languages: list[ProgrammingLanguage] | None
    languages: list[Language] | None
    tools: list[Tool] | None
    certificates: list[Certificate] | None
    charities: list[Charity] | None
    educations: list[Education] | None
    experiences: list[Experience] | None
    projects: list[Project] | None
    social_platforms: list[SocialPlatform] | None
    websites: list[Website] | None


class CandidateData(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: str
    locations: list[LocationModel] | None
    programming_languages: list[ProgrammingLanguageModel] | None
    languages: list[LanguageModel] | None
    tools: list[ToolModel] | None
    certificates: list[CertificateModel] | None
    charities: list[CharityModel] | None
    educations: list[EducationModel] | None
    experiences: list[ExperienceModel] | None
    projects: list[ProjectModel] | None
    social_platforms: list[SocialPlatformModel] | None


class SkillsLLMResponse(BaseModel):
    programming_languages: list[ProgrammingLanguage] | None
    languages: list[Language] | None
    tools: list[Tool] | None
    certificates: list[Certificate] | None
    charities: list[Charity] | None
    educations: list[Education] | None
    experiences: list[Experience] | None
    projects: list[Project] | None
