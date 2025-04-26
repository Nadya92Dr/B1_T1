import pytest
from fastapi.testclient import TestClient
from api import app
from sqlmodel import SQLModel, Session, create_engine 
from database.database import get_session 
from sqlalchemy.pool import StaticPool
from auth.authenticate import authenticate
import os

@pytest.fixture(scope="module")
def test_engine():
    test_engine = create_engine(os.getenv("TEST_DATABASE_URL",
     "postgresql+psycopg2://test:test@localhost/test_db"))
    SQLModel.metadata.create_all(test_engine)
    yield test_engine
    SQLModel.metadata.drop_all(test_engine)
    test_engine.dispose()

@pytest.fixture
def db_session(test_engine):
    with Session(test_engine) as session:
        yield session
        session.rollback()

@pytest.fixture(name="session")  
def session_fixture():  
    engine = create_engine("sqlite:///testing.db", 
    connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client") 
def client_fixture(session: Session):  
    def get_session_override():  
        return session

    app.dependency_overrides[get_session] = get_session_override  
    app.dependency_overrides[authenticate] = lambda: "user@test.ru"  
    
    client = TestClient(app)  
    yield client  
    app.dependency_overrides.clear()