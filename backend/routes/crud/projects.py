from backend.database.crud import get_projects, delete_model, save_model
from backend.database.models import ProjectModel
from backend.schemas.endpoints import ProjectPost, Project
from backend.routes.deps import CurrentUser, SessionDep

from sqlmodel import select
from fastapi import APIRouter


router = APIRouter(prefix="projects")


@router.get("/")
async def read_projects(user: CurrentUser, session: SessionDep):
    return get_projects(session, user, use_base_model=True)


@router.get("/{item_id}")
async def read_project(user: CurrentUser, session: SessionDep):
    return get_projects(session, user, use_base_model=True)


@router.post("/")
async def create_project(
        user: CurrentUser, session: SessionDep, item: Project
):
    save_model(session, user, ProjectModel.model_validate(item))


@router.put("/{item_id}")
async def update_project(
        user: CurrentUser, session: SessionDep, item_id: int, item: ProjectPost
):
    model_to_update = session.exec(
        select(ProjectModel).where(ProjectModel.id == item_id)
    ).one()

    model_to_update.sqlmodel_update(item)
    session.add(model_to_update)
    session.commit()
    session.refresh(model_to_update)

    return model_to_update


@router.delete("/{item_id}")
async def delete_project(user: CurrentUser, session: SessionDep, item_id: int):
    delete_model(session, user, ProjectModel, item_id)
