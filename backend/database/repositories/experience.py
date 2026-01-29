from backend.database.models import ExperienceModel
from backend.database.repositories.base import DataRepository


class ExperienceRepository(DataRepository[ExperienceModel]):
    model = ExperienceModel
