from pydantic import BaseModel

from backend.database.models import CVCreationModeEnum


class UserPreferences(BaseModel):
    cv_creation_mode: CVCreationModeEnum = CVCreationModeEnum.llm_generation
    generate_cover_letter: bool = True
    cv_path: str = ""
    retries: int = 3
