import datetime
from enum import StrEnum
from typing import Literal, Sequence, TypeAliasType

from pydantic import BaseModel, EmailStr


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


class AttributeType(StrEnum):
    id = "id"
    text = "text"
    aria_label = "aria_label"
    name = "name"
    element_type = "element_type"
    class_l = "class_l"


class HTMLElement(BaseModel):
    id: str = ""
    name: str = ""
    element_type: str = ""
    aria_label: str = ""
    placeholder: str = ""
    role: str = ""
    text: str = ""
    class_list: list[str] = []
    parents: str = ""
    parents_list: list[str] = []


class Step(BaseModel):
    function: Literal["click", "fill"]
    tag: HTMLElement
    additional_arguments: dict


AgentName = TypeAliasType(
    "AgentName",
    Literal[
        "login_agent",
        "job_listing_page_agent",
        "next_page_agent",
        "job_urls_agent",
        "no_agent_name",
    ],
)


class AutomationSteps(BaseModel):
    agent_name: AgentName
    steps: list[Step]
    # login: list[Step]
    # job_listing_page: list[Step]
    # job_urls: list[Step]
    # next_page: list[Step]
    # TODO: Uncomment if this function gets html elements get_job_information: list[Step]


class Website(BaseModel):
    cookies: str
    user_email: EmailStr
    user_password: str
    url: str
    automation_steps: AutomationSteps | None


class Location(BaseModel):
    country: str
    state: str
    city: str
    zip_code: str


class ProgrammingLanguage(BaseModel):
    programming_language: str
    level: str  # Maybe in the future change to int


class Language(BaseModel):
    language: str
    level: str  # Maybe in the future change to int


class Tool(BaseModel):
    tool: str
    level: str  # Maybe in the future change to int


class Certificate(BaseModel):
    certificate: str
    description: str
    organisation: str


class Charity(BaseModel):
    charity: str
    description: str
    organisation: str
    start_date: datetime.date | None
    end_date: datetime.date | None


class Education(BaseModel):
    school: str
    major: str
    description: str
    start_date: datetime.date | None
    end_date: datetime.date | None


class Experience(BaseModel):
    company: str
    position: str
    description: str
    start_date: datetime.date | None
    end_date: datetime.date | None


class Project(BaseModel):
    project: str
    description: str
    url: str


class SocialPlatform(BaseModel):
    social_platform: str
    url: str


class UserPreferences(BaseModel):
    cv_creation_mode: CVCreationModeEnum = CVCreationModeEnum.llm_generation
    generate_cover_letter: bool = True
    cv_path: str = ""
    retries: int = 3


class UserNeeds(BaseModel):
    locations: Sequence[Location] | None
    programming_languages: Sequence[ProgrammingLanguage] | None
    languages: Sequence[Language] | None
    tools: Sequence[Tool] | None
    certificates: Sequence[Certificate] | None
    experiences: Sequence[Experience] | None
    projects: Sequence[Project] | None


class CandidateData(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: str
    locations: Sequence[Location] | None
    programming_languages: Sequence[ProgrammingLanguage] | None
    languages: Sequence[Language] | None
    tools: Sequence[Tool] | None
    certificates: Sequence[Certificate] | None
    charities: Sequence[Charity] | None
    educations: Sequence[Education] | None
    experiences: Sequence[Experience] | None
    projects: Sequence[Project] | None
    social_platforms: Sequence[SocialPlatform] | None
