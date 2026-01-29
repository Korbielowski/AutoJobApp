from sqlmodel import Session

from backend.database.models import UserModel
from backend.database.repositories.certificate import CertificateRepository
from backend.database.repositories.charity import CharityRepository
from backend.database.repositories.education import EducationRepository
from backend.database.repositories.experience import ExperienceRepository
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
from backend.schemas.models import (
    CandidateData,
    UserNeeds,
)


def get_candidate_data(session: Session, user: UserModel) -> CandidateData:
    loc_repo = LocationRepository()
    locations = loc_repo.convert_list_to_read_only(
        loc_repo.read_all(session, user.id)
    )

    pro_lan_repo = ProgrammingLanguageRepository()
    programming_languages = pro_lan_repo.convert_list_to_read_only(
        pro_lan_repo.read_all(session, user.id)
    )

    lan_repo = LanguageRepository()
    languages = lan_repo.convert_list_to_read_only(
        lan_repo.read_all(session, user.id)
    )

    tool_repo = ToolRepository()
    tools = tool_repo.convert_list_to_read_only(
        tool_repo.read_all(session, user.id)
    )

    certificate_repo = CertificateRepository()
    certificates = certificate_repo.convert_list_to_read_only(
        certificate_repo.read_all(session, user.id)
    )

    exp_repo = ExperienceRepository()
    experiences = exp_repo.convert_list_to_read_only(
        exp_repo.read_all(session, user.id)
    )

    char_repo = CharityRepository()
    charities = char_repo.convert_list_to_read_only(
        char_repo.read_all(session, user.id)
    )

    edu_repo = EducationRepository()
    educations = edu_repo.convert_list_to_read_only(
        edu_repo.read_all(session, user.id)
    )

    soc_plat_repo = SocialPlatformRepository()
    social_platforms = soc_plat_repo.convert_list_to_read_only(
        soc_plat_repo.read_all(session, user.id)
    )

    proc_repo = ProjectRepository()
    projects = proc_repo.convert_list_to_read_only(
        proc_repo.read_all(session, user.id)
    )

    full_name = (
        f"{user.first_name} {user.middle_name} {user.surname}"
        if user.middle_name
        else f"{user.first_name} {user.surname}"
    )

    return CandidateData(
        full_name=full_name,
        email=user.email,
        phone_number=user.phone_number,
        locations=locations,
        programming_languages=programming_languages,
        languages=languages,
        tools=tools,
        certificates=certificates,
        charities=charities,
        educations=educations,
        experiences=experiences,
        projects=projects,
        social_platforms=social_platforms,
    )


def get_user_needs(session: Session, user: UserModel) -> UserNeeds:
    loc_repo = LocationRepository()
    locations = loc_repo.convert_list_to_read_only(
        loc_repo.read_all(session, user.id)
    )

    pro_lan_repo = ProgrammingLanguageRepository()
    programming_languages = pro_lan_repo.convert_list_to_read_only(
        pro_lan_repo.read_all(session, user.id)
    )

    lan_repo = LanguageRepository()
    languages = lan_repo.convert_list_to_read_only(
        lan_repo.read_all(session, user.id)
    )

    tool_repo = ToolRepository()
    tools = tool_repo.convert_list_to_read_only(
        tool_repo.read_all(session, user.id)
    )

    certificate_repo = CertificateRepository()
    certificates = certificate_repo.convert_list_to_read_only(
        certificate_repo.read_all(session, user.id)
    )

    exp_repo = ExperienceRepository()
    experiences = exp_repo.convert_list_to_read_only(
        exp_repo.read_all(session, user.id)
    )

    proc_repo = ProjectRepository()
    projects = proc_repo.convert_list_to_read_only(
        proc_repo.read_all(session, user.id)
    )

    return UserNeeds(
        locations=locations,
        programming_languages=programming_languages,
        languages=languages,
        tools=tools,
        certificates=certificates,
        experiences=experiences,
        projects=projects,
    )
