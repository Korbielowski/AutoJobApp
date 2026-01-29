from backend.database.models import JobEntryModel
from backend.database.repositories.base import DataRepository
from backend.schemas.models import JobEntry


class JobEntryRepository(DataRepository[JobEntryModel, JobEntry]):
    model = JobEntryModel
    read_model = JobEntry
