from backend.database.crud import get_educations, delete_model, save_model
from backend.database.models import EducationModel
from backend.schemas.endpoints import EducationPost, Education
from backend.routes.deps import CurrentUser, SessionDep

from sqlmodel import select
from fastapi import APIRouter


router = APIRouter(prefix="/educations")


@router.get("/")
async def read_educations(user: CurrentUser, session: SessionDep):
    return get_educations(session, user, use_base_model=True)


@router.get("/{item_id}")
async def read_education(user: CurrentUser, session: SessionDep):
    return get_educations(session, user, use_base_model=True)


@router.post("/")
async def create_education(
        user: CurrentUser, session: SessionDep, item: Education
):
    save_model(session, user, EducationModel.model_validate(item))


@router.put("/{item_id}")
async def update_education(
        user: CurrentUser, session: SessionDep, item_id: int, item: EducationPost
):
    model_to_update = session.exec(
        select(EducationModel).where(EducationModel.id == item_id)
    ).one()

    model_to_update.sqlmodel_update(item)
    session.add(model_to_update)
    session.commit()
    session.refresh(model_to_update)

    return model_to_update


@router.delete("/{item_id}")
async def delete_education(user: CurrentUser, session: SessionDep, item_id: int):
    delete_model(session, user, EducationModel, item_id)
