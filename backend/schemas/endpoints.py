import datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr

from backend.schemas.models import (
    AutomationSteps,
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
    User,
    Website,
)


def ensure_date(value: str | datetime.date):
    if isinstance(value, str):
        return datetime.date.fromisoformat(value)
    return value


class WebsitePost(BaseModel):
    id: int
    user_id: int
    cookies: str
    user_email: EmailStr
    user_password: str
    url: str
    automation_steps: AutomationSteps | None

    model_config = ConfigDict(strict=True)


class LocationPost(BaseModel):
    id: int
    user_id: int
    country: str
    state: str
    city: str
    zip_code: str

    model_config = ConfigDict(strict=True)


class ProgrammingLanguagePost(BaseModel):
    id: int
    user_id: int
    programming_language: str
    level: str  # Maybe in the future change to int

    model_config = ConfigDict(strict=True)


class LanguagePost(BaseModel):
    id: int
    user_id: int
    language: str
    level: str

    model_config = ConfigDict(strict=True)


class ToolPost(BaseModel):
    id: int
    user_id: int
    tool: str
    level: str

    model_config = ConfigDict(strict=True)


class CertificatePost(BaseModel):
    id: int
    user_id: int
    certificate: str
    description: str
    organisation: str

    model_config = ConfigDict(strict=True)


class CharityPost(BaseModel):
    id: int
    user_id: int
    charity: str
    description: str
    organisation: str
    start_date: Annotated[datetime.date, BeforeValidator(ensure_date)]
    end_date: Annotated[datetime.date, BeforeValidator(ensure_date)]

    model_config = ConfigDict(strict=True)


class EducationPost(BaseModel):
    id: int
    user_id: int
    school: str
    major: str
    description: str
    start_date: Annotated[datetime.date, BeforeValidator(ensure_date)]
    end_date: Annotated[datetime.date, BeforeValidator(ensure_date)]

    model_config = ConfigDict(strict=True)


class ExperiencePost(BaseModel):
    id: int
    user_id: int
    company: str
    position: str
    description: str
    start_date: Annotated[datetime.date, BeforeValidator(ensure_date)]
    end_date: Annotated[datetime.date, BeforeValidator(ensure_date)]

    model_config = ConfigDict(strict=True)


class ProjectPost(BaseModel):
    id: int
    user_id: int
    project: str
    description: str
    url: str

    model_config = ConfigDict(strict=True)


class SocialPlatformPost(BaseModel):
    id: int
    user_id: int
    social_platform: str
    url: str

    model_config = ConfigDict(strict=True)


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


class DeleteItem(BaseModel):
    item_type: str
    item_id: int
