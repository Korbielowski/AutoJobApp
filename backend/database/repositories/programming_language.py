from backend.database.models import ProgrammingLanguageModel
from backend.database.repositories.base import DataRepository


class ProgrammingLanguageRepository(DataRepository[ProgrammingLanguageModel]):
    model = ProgrammingLanguageModel
