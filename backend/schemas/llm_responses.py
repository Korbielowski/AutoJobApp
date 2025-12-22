from typing import Literal

from pydantic import BaseModel, Field

from backend.schemas.models import (
    Certificate,
    Charity,
    Education,
    Experience,
    Language,
    ProgrammingLanguage,
    Project,
    Tool,
)


class HTMLElement(BaseModel):
    id: str = ""
    name: str = ""
    element_type: str = ""
    aria_label: str = ""
    placeholder: str = ""
    role: str = ""
    text: str = ""
    class_list: list[str] = []


class CompanyDetails(BaseModel):
    products_and_technologies: str = ""
    work_culture: str = ""
    business_and_industry_context: str = ""
    mission_and_strategic_direction: str = ""


class CVOutput(BaseModel):
    html: str = ""
    css: str = ""


class CoverLetterOutput(BaseModel):
    html: str = ""


class JobEntryResponse(BaseModel):
    title: str
    company_name: str
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


class SkillsLLMResponse(BaseModel):
    programming_languages: list[ProgrammingLanguage] | None
    languages: list[Language] | None
    tools: list[Tool] | None
    certificates: list[Certificate] | None
    charities: list[Charity] | None
    educations: list[Education] | None
    experiences: list[Experience] | None
    projects: list[Project] | None


class StateOutput(BaseModel):
    state: bool = False


class TaskState(BaseModel):
    """
    state: State of your task
    confidence: How confident you are that you accomplished your task
    """

    state: Literal["done", "in-progress"]
    confidence: float = Field(gt=0.0, le=1.0)
