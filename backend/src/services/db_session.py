from typing import Annotated, Generator

from config.database import engine
from fastapi import Depends
from sqlalchemy.orm import Session


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

DBSessionDep = Annotated[Session, Depends(get_session)]

