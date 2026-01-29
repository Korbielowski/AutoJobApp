from backend.database.models import ExperienceModel
from backend.database.repositories.base import DataRepository
from backend.schemas.models import Experience


class ExperienceRepository(DataRepository[ExperienceModel, Experience]):
    model = ExperienceModel
    read_model = Experience
