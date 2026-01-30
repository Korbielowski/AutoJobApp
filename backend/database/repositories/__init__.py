from backend.database.repositories.certificate import CertificateRepository
from backend.database.repositories.charity import CharityRepository
from backend.database.repositories.education import EducationRepository
from backend.database.repositories.experience import ExperienceRepository
from backend.database.repositories.job_board_website import (
    JobBoardWebsiteRepository,
)
from backend.database.repositories.job_entry import JobEntryRepository
from backend.database.repositories.language import LanguageRepository
from backend.database.repositories.location import LocationRepository
from backend.database.repositories.programming_language import (
    ProgrammingLanguageRepository,
)
from backend.database.repositories.project import ProjectRepository
from backend.database.repositories.social_platform import (
    SocialPlatformRepository,
)
from backend.database.repositories.tool import ToolRepository
from backend.database.repositories.user import UserRepository
from backend.database.repositories.user_preferences import (
    UserPreferencesRepository,
)
from backend.database.repositories.utils import (
    get_candidate_data,
    get_user_needs,
)
from backend.database.repositories.base import DataRepository

__all__ = [
    "JobBoardWebsiteRepository",
    "JobEntryRepository",
    "get_user_needs",
    "get_candidate_data",
    "UserRepository",
    "UserPreferencesRepository",
    "EducationRepository",
    "CharityRepository",
    "ExperienceRepository",
    "LocationRepository",
    "CertificateRepository",
    "SocialPlatformRepository",
    "ProjectRepository",
    "ToolRepository",
    "LanguageRepository",
    "ProgrammingLanguageRepository",
    "DataRepository",
]
