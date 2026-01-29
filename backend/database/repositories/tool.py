from backend.database.models import ToolModel
from backend.database.repositories.base import DataRepository
from backend.schemas.models import Tool


class ToolRepository(DataRepository[ToolModel, Tool]):
    model = ToolModel
    read_model = Tool
