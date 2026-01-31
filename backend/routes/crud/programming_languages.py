from backend.database.crud import get_programming_languages, delete_model, save_model
from backend.database.models import ProgrammingLanguageModel
from backend.schemas.endpoints import ProgrammingLanguagePost, ProgrammingLanguage
from backend.routes.deps import CurrentUser, SessionDep

from sqlmodel import select
from fastapi import APIRouter


router = APIRouter(prefix="programming_languages")


@router.get("/")
async def read_programming_languages(user: CurrentUser, session: SessionDep):
    return get_programming_languages(session, user, use_base_model=True)


@router.get("/{item_id}")
async def read_programming_language(user: CurrentUser, session: SessionDep):
    return get_programming_languages(session, user, use_base_model=True)


@router.post("/")
async def create_programming_language(
        user: CurrentUser, session: SessionDep, item: ProgrammingLanguage
):
    save_model(session, user, ProgrammingLanguageModel.model_validate(item))


@router.put("/{item_id}")
async def update_programming_language(
        user: CurrentUser, session: SessionDep, item_id: int, item: ProgrammingLanguagePost
):
    model_to_update = session.exec(
        select(ProgrammingLanguageModel).where(ProgrammingLanguageModel.id == item_id)
    ).one()

    model_to_update.sqlmodel_update(item)
    session.add(model_to_update)
    session.commit()
    session.refresh(model_to_update)

    return model_to_update


@router.delete("/{item_id}")
async def delete_programming_language(user: CurrentUser, session: SessionDep, item_id: int):
    delete_model(session, user, ProgrammingLanguageModel, item_id)
