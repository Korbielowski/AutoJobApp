from backend.database.models import EducationModel
from backend.database.repositories.base import DataRepository
from backend.schemas.models import Education


class EducationRepository(DataRepository[EducationModel, Education]):
    model = EducationModel
    read_model = Education
