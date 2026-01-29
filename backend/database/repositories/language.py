from backend.database.models import LanguageModel
from backend.database.repositories.base import DataRepository
from backend.schemas.models import Language


class LanguageRepository(DataRepository[LanguageModel, Language]):
    model = LanguageModel
    read_model = Language
