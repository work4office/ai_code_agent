from ai_code_agent.database import (
    Session,
    SQLModel,
    create_engine,
    Annotated,
    Depends,
    settings,
)

SQL_SERVER_URL = settings.SQL_SERVER_URL or ""

connect_args = {"check_same_thread": False}
engine = create_engine(SQL_SERVER_URL, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
