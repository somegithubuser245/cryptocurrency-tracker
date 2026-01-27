from contextlib import contextmanager
from typing import Annotated, Generator

from config.database import engine
from fastapi import Depends
from sqlalchemy.orm import Session, sessionmaker


def get_session_dep() -> Generator[Session, None, None]:
    Session = sessionmaker(engine)
    with Session() as session:
        yield session


@contextmanager
def get_session_raw() -> Session:
    Session = sessionmaker(engine)
    with Session() as session:
        yield session
        session.close()


DBSessionDep = Annotated[Session, Depends(get_session_dep)]
