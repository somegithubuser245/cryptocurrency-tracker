import sqlalchemy as sa
from config.config import PostgresDBSettings
from sqlalchemy.orm import sessionmaker

db_url = PostgresDBSettings().construct_url()
db = sa.create_engine(db_url)
Session = sessionmaker(bind=db)
