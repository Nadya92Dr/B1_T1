import bcrypt
import os
from models.user import User, Admin
from models.LLM import LLM, History 
from typing import List, Optional

def get_all_users(session) -> List[User]:
    return session.query(User).all()

def get_user_by_id(user_id:int, session) -> Optional[User]:
    users = session.get(User, user_id) 
    if users:
        return users 
    return None

def get_user_by_email(email:str, session) -> Optional[User]:
    user = session.query(User).filter(User.email == email).first()
    if user:
        return user 
    return None

def get_user_history(user_id: int, session):
    return (
        session.query(History)
        .filter(History.User_id == user_id)
        .order_by(History.created_at.desc())
        .all()
    )

def check_balance(user: User, balance: int) -> bool:
    return user.balance >= balance

def create_user(new_user: User, session) -> User:
    session.add(new_user) 
    session.commit() 
    session.refresh(new_user)
    return new_user

    def _hash_password(hashed_password: password, password:str) -> bytes:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw (password.encode(),salt)
    def check_password (self, password:str) -> bool:
         return bcrypt.checkpw (password.encode(),self._password_hash)

def auth_user(email: str, password: str, session) -> Optional[User]:
    user = get_user_by_email(email, session)
    if not user or not bcrypt.checkpw(password.encode(), user.password.encode()):
        return None
    return user


def recharge_balance(admin: Admin, user_id: int, amount: int, session) -> Optional[User]:
    
    db_admin = session.get (Admin, admin.Admin_id)
    if not db_admin:
        raise ValueError ("Только администратор может пополнять баланс")
    
    if amount <= 0:
        raise ValueError("Сумма пополнения должна быть положительной")
    
    user = get_user_by_id(user_id, session)
    if not user:
        return None
    user.balance += amount
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user

