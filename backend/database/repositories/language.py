from backend.database.models import LanguageModel
from backend.database.repositories.base import DataRepository


class LanguageRepository(DataRepository[LanguageModel]):
    model = LanguageModel
