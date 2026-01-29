from backend.database.models import CertificateModel
from backend.database.repositories.base import DataRepository


class CertificateRepository(DataRepository[CertificateModel]):
    model = CertificateModel
