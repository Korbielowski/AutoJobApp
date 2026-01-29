from backend.database.models import JobEntryModel
from backend.database.repositories.base import DataRepository


class JobEntryRepository(DataRepository[JobEntryModel]):
    model = JobEntryModel
