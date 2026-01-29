from backend.database.models import ProjectModel
from backend.database.repositories.base import DataRepository


class ProjectRepository(DataRepository[ProjectModel]):
    model = ProjectModel
