from pydantic import BaseModel

from backend.database.models import CVModeEnum


class UserPreferences(BaseModel):
    cv_creation_mode: CVModeEnum = CVModeEnum.llm_generation
    generate_cover_letter: bool = True
    cv_path: str = ""
    retries: int = 3
