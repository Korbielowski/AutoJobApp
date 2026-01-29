from backend.database.models import EducationModel
from backend.database.repositories.base import DataRepository


class EducationRepository(DataRepository[EducationModel]):
    model = EducationModel
