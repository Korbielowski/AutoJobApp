from backend.database.models import CharityModel
from backend.database.repositories.base import DataRepository


class CharityRepository(DataRepository[CharityModel]):
    model = CharityModel
