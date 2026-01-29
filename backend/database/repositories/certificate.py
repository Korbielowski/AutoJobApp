from backend.database.models import CertificateModel
from backend.database.repositories.base import DataRepository
from backend.schemas.models import Certificate


class CertificateRepository(DataRepository[CertificateModel, Certificate]):
    model = CertificateModel
    read_model = Certificate
