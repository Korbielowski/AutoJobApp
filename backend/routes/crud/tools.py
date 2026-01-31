from backend.database.crud import get_tools, delete_model, save_model
from backend.database.models import ToolModel
from backend.schemas.endpoints import ToolPost, Tool
from backend.routes.deps import CurrentUser, SessionDep

from sqlmodel import select
from fastapi import APIRouter


router = APIRouter(prefix="tools")


@router.get("/")
async def read_tools(user: CurrentUser, session: SessionDep):
    return get_tools(session, user, use_base_model=True)


@router.get("/{item_id}")
async def read_tool(user: CurrentUser, session: SessionDep):
    return get_tools(session, user, use_base_model=True)


@router.post("/")
async def create_tool(
        user: CurrentUser, session: SessionDep, item: Tool
):
    save_model(session, user, ToolModel.model_validate(item))


@router.put("/{item_id}")
async def update_tool(
        user: CurrentUser, session: SessionDep, item_id: int, item: ToolPost
):
    model_to_update = session.exec(
        select(ToolModel).where(ToolModel.id == item_id)
    ).one()

    model_to_update.sqlmodel_update(item)
    session.add(model_to_update)
    session.commit()
    session.refresh(model_to_update)

    return model_to_update


@router.delete("/{item_id}")
async def delete_tool(user: CurrentUser, session: SessionDep, item_id: int):
    delete_model(session, user, ToolModel, item_id)
