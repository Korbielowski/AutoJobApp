from backend.database.models import ProgrammingLanguageModel
from backend.database.repositories.base import DataRepository
from backend.schemas.models import ProgrammingLanguage


class ProgrammingLanguageRepository(
    DataRepository[ProgrammingLanguageModel, ProgrammingLanguage]
):
    model = ProgrammingLanguageModel
    read_model = ProgrammingLanguage
