import datetime
from enum import StrEnum
from typing import Sequence, Callable

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
