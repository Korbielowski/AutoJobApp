from backend.database.models import SocialPlatformModel
from backend.database.repositories.base import DataRepository
from backend.schemas.models import SocialPlatform


class SocialPlatformRepository(
    DataRepository[SocialPlatformModel, SocialPlatform]
):
    model = SocialPlatformModel
    read_model = SocialPlatform
