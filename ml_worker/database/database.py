from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import Session

DATABASE_URL = "postgresql://postgres:postgres@database:5432/postgres_db"

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    return Session(engine)