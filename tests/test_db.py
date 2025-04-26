from sqlmodel import SQLModel, Session, create_engine
from models.user import User
import pytest


def test_create_user(db_session: Session):
    user = User(email="test@mail.ru", password="1234")
    db_session.add(user)
    db_session.commit()

    db_user = db_session.get(User, 1)
    assert db_user.email == "test@mail.ru"
    
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
    
        
def test_delete_user(db_session: Session):
    user = User(email="test@mail.ru", password="1234")
    db_session.add(user)
    db_session.commit()

    db_user = db_session.get(User, 1)
    assert db_user is not None

    db_session.delete(db_user)
    db_session.commit()

    deleted_user = db_session.get(User, 1)
    assert deleted_user is None