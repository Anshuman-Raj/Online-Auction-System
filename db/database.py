import sqlalchemy as _sql
import sqlalchemy.ext.declarative as _declarative
import sqlalchemy.orm as _orm
from typing import Generator
import os
import sqlite3

# For local run
# DATABASE_URL = 'postgresql://myuser:password@localhost:5432/user_details'

# For docker run
user_name = os.environ["POSTGRES_USERNAME"]
password = os.environ["POSTGRES_PASSWORD"]
host = os.environ["POSTGRES_HOST"]
port = os.environ["POSTGRES_PORT"]
db_name = os.environ["POSTGRES_DB"]

DATABASE_URL = f'postgresql://{user_name}:{password}@{host}:{port}/{db_name}'

# For test purpose
# DATABASE_URL = 'sqlite:///foo.db'
engine = _sql.create_engine(DATABASE_URL)
SessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = _declarative.declarative_base()

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()