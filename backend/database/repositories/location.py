from backend.database.models import LocationModel
from backend.database.repositories.base import DataRepository
from backend.schemas.models import Location


class LocationRepository(DataRepository[LocationModel, Location]):
    model = LocationModel
    read_model = Location
