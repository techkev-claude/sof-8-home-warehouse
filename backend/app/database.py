from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event
from app.config import settings
import os

DB_PATH = os.path.join(settings.data_path, "warehouse.db")
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_db():
    os.makedirs(settings.data_path, exist_ok=True)
    os.makedirs(settings.images_path, exist_ok=True)
    # Modelle muessen importiert sein, damit SQLModel.metadata sie kennt
    from app import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
