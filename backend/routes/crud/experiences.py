from backend.database.crud import get_experiences, delete_model, save_model
from backend.database.models import ExperienceModel
from backend.schemas.endpoints import ExperiencePost, Experience
from backend.routes.deps import CurrentUser, SessionDep

from sqlmodel import select
from fastapi import APIRouter


router = APIRouter(prefix="experiences")


@router.get("/")
async def read_experiences(user: CurrentUser, session: SessionDep):
    return get_experiences(session, user, use_base_model=True)


@router.get("/{item_id}")
async def read_experience(user: CurrentUser, session: SessionDep):
    return get_experiences(session, user, use_base_model=True)


@router.post("/")
async def create_experience(
        user: CurrentUser, session: SessionDep, item: Experience
):
    save_model(session, user, ExperienceModel.model_validate(item))


@router.put("/{item_id}")
async def update_experience(
        user: CurrentUser, session: SessionDep, item_id: int, item: ExperiencePost
):
    model_to_update = session.exec(
        select(ExperienceModel).where(ExperienceModel.id == item_id)
    ).one()

    model_to_update.sqlmodel_update(item)
    session.add(model_to_update)
    session.commit()
    session.refresh(model_to_update)

    return model_to_update


@router.delete("/{item_id}")
async def delete_experience(user: CurrentUser, session: SessionDep, item_id: int):
    delete_model(session, user, ExperienceModel, item_id)
