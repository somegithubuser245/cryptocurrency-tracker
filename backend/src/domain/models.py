from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    # used mostrly for alembic migrations
    pass

class TestTable(Base):
    pass
