from sqlmodel import Session

from backend.database.models import JobBoardWebsiteModel
from backend.database.repositories.base import DataRepository
from backend.schemas.models import (
    AgentNameEnum,
    AutomationSteps,
    JobBoardWebsite,
    Step,
)


class JobBoardWebsiteRepository(
    DataRepository[JobBoardWebsiteModel, JobBoardWebsite]
):
    model = JobBoardWebsiteModel
    read_model = JobBoardWebsite

    @staticmethod
    def update(
        session: Session,
        agent_name: AgentNameEnum,
        obj: JobBoardWebsiteModel,
        steps: list[Step],
        **kwargs,
    ) -> JobBoardWebsiteModel:
        if not obj.automation_steps:
            obj.automation_steps = AutomationSteps().model_dump()

        json_compatible_steps = [step.model_dump() for step in steps]

        if agent_name == AgentNameEnum.login_agent:
            obj.automation_steps["login_steps"] = json_compatible_steps
        elif agent_name == AgentNameEnum.job_listing_page_agent:
            obj.automation_steps["job_listing_page_steps"] = (
                json_compatible_steps
            )
        elif agent_name == AgentNameEnum.job_urls_agent:
            obj.automation_steps["job_urls_steps"] = json_compatible_steps
        elif agent_name == AgentNameEnum.next_page_agent:
            obj.automation_steps["next_page_steps"] = json_compatible_steps

        session.add(obj)
        session.commit()
        return obj
