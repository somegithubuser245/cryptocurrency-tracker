from pathlib import Path

from alembic import command
from alembic.config import Config
from pydantic_settings import BaseSettings
from sqlalchemy import URL, create_engine


class PostgresDBSettings(BaseSettings):
    POSTGRES_DB: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "root"
    DRIVER_NAME: str = "postgresql"
    PORT: int = 5432

    def construct_url(self, use_alembic: bool = False) -> URL:
        host = "localhost" if use_alembic else "db"

        return URL.create(
            host=host,
            port=self.PORT,
            drivername=self.DRIVER_NAME,
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            database=self.POSTGRES_DB,
        )

DB_URL = PostgresDBSettings().construct_url().render_as_string(hide_password=False)
DB_URL_ALEMBIC = PostgresDBSettings().construct_url(use_alembic=True).render_as_string(hide_password=False)
engine = create_engine(DB_URL)


def run_alembic_migrations() -> None:
    alembic_config_path = Path.cwd() / "alembic.ini"
    alembic_cfg = Config(alembic_config_path)
    alembic_cfg.set_main_option("sqlalchemy.url", DB_URL)
    with engine.begin() as connection:
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")
