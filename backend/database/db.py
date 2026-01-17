from sqlmodel import SQLModel, create_engine, text

from backend.config import settings

engine = create_engine(settings.DATABASE_URI)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    # Enable foreign keys for local sqlite database
    if settings.DB_BACKEND == "sqlite":
        with engine.connect() as connection:
            connection.execute(text("PRAGMA foreign_keys=ON"))
