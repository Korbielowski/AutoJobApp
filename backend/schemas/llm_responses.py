from dataclasses import dataclass
from enum import StrEnum
from typing import Literal, Optional

from playwright.async_api import Page
from pydantic import BaseModel, Field

from backend.database.models import WebsiteModel
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
    parents: str = ""


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


class InputFieldTypeEnum(StrEnum):
    email = "email"
    password = "password"


class StateOutput(BaseModel):
    state: bool = False


class TaskState(BaseModel):
    """
    state: State of a task
    confidence: Confidence of a task state
    """

    state: Literal["done", "failed"]
    confidence: float = Field(gt=0.0, le=1.0)


class TextResponse(BaseModel):
    text: str


class ToolResult(BaseModel):
    success: bool
    result: Optional[str] = None
    error_code: Optional[
        Literal["ELEMENT_NOT_FOUND", "TIMEOUT", "NOT_VISIBLE", "WRONG_INPUT"]
    ] = None


@dataclass
class ContextForLLM:
    page: Page
    website_info: WebsiteModel
    agent_name: str
