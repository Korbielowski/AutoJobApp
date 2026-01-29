from backend.database.models import ProjectModel
from backend.database.repositories.base import DataRepository
from backend.schemas.models import Project


class ProjectRepository(DataRepository[ProjectModel, Project]):
    model = ProjectModel
    read_model = Project
