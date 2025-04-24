from sqlmodel import SQLModel, Session, create_engine
from models.user import User
import pytest
# from database.database import get_database_engine, init_database

@pytest.fixture(scope="module")
def test_engine():
    test_engine = create_engine("postgresql+psycopg2://test:test@localhost/test_db")
    SQLModel.metadata.create_all(test_engine)
    yield test_engine
    SQLModel.metadata.drop_all(test_engine)
    test_engine.dispose()

@pytest.fixture
def session(test_engine):
    with Session(test_engine) as session:
        yield session
        session.rollback()  


def test_create_user(session: Session):
    user = User(id=1, email="test@mail.ru", password="1234")
    session.add(user)
    session.commit()

    db_user = session.get(User, 1)
    assert db_user.email == "test@mail.ru"
    assert db_user.password == "1234"
    
def test_fail_create_user(session: Session):
    with pytest.raises(Exception) as ex:
        user = User(id=1, email="test_2@mail.ru", password="12")
        session.add(user)
        session.commit()

def test_get_nonexistent_user(session: Session):
    user = session.get(User, 999)
    assert user is None

def test_update_user_profile(session: Session):
    user = User(email="update@test.com", password="pass")
    session.add(user)
    session.commit()
    
    user.nickname = "new_nickname"
    session.commit()
    
    updated_user = session.get(User, user.user_id)
    assert updated_user.nickname == "new_nickname"

def test_get_all_users(session: Session):
    session.add_all([
        User(email="user1@test.com", password="pass"),
        User(email="user2@test.com", password="pass")
    ])
    session.commit()
    
    users = session.query(User).all()
    assert len(users) == 2
    
        
def test_delete_user(session: Session):
    test_create_user(session)
    
    user = session.get(User, 1)
    assert user is not None, "User with id=0 not found"

    session.delete(user)
    session.commit()

    deleted_user = session.get(User, 1)
    assert deleted_user is None, "User was not deleted"
