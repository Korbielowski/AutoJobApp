from backend.database.models import ToolModel
from backend.database.repositories.base import DataRepository


class ToolRepository(DataRepository[ToolModel]):
    model = ToolModel
