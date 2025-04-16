from sqlmodel import SQLModel, create_engine
from sqlalchemy.orm import Session

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@database:5432/postgres_db"

engine = create_engine(DATABASE_URL)
SessionLocal = Session(autocommit=False, autoflush=False, bind=engine)
