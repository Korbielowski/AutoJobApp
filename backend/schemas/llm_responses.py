from pydantic import BaseModel


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
