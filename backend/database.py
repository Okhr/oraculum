import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()
SQLACHEMY_DATABASE_URL = f'postgresql+psycopg2://{os.getenv("POSTGRES_USER")}@{os.getenv("POSTGRES_HOST")}:{os.getenv("DATABASE_PORT")}/{os.getenv("POSTGRES_DB")}'

engine = create_engine(SQLACHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
