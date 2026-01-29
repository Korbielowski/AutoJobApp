from backend.database.models import SocialPlatformModel
from backend.database.repositories.base import DataRepository


class SocialPlatformRepository(DataRepository[SocialPlatformModel]):
    model = SocialPlatformModel
