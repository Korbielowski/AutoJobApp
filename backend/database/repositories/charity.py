from backend.database.models import CharityModel
from backend.database.repositories.base import DataRepository
from backend.schemas.models import Charity


class CharityRepository(DataRepository[CharityModel, Charity]):
    model = CharityModel
    read_model = Charity
