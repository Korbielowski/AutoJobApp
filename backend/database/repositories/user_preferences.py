from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, select

from backend.database.models import UserPreferencesModel
from backend.database.repositories.base import DataRepository
from backend.schemas.models import UserPreferences


class UserPreferencesRepository(
    DataRepository[UserPreferencesModel, UserPreferences]
):
    model = UserPreferencesModel
    read_model = UserPreferences

    def read_one_by_user_id(
        self, session: Session, user_id: int
    ) -> UserPreferencesModel:
        result = session.exec(
            select(self.model).where(self.model.user_id == user_id)
        ).one()
        return result


UserPreferencesRepositoryDep = Annotated[
    UserPreferencesRepository, Depends(UserPreferencesRepository)
]
