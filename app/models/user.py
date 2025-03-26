import bcrypt
import os

class User:
  def __init__(self, user_id:int, email:str, password:str, nickname:str, balance:int=5):
    self._email = email
    self._user_id = user_id
    self._password_hash = self._hash_password (password)
    self._nickname = nickname
    self._balance = balance

  def _hash_password(self, password:str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw (password.encode(),salt)
  def check_password (self, password:str) -> bool:
    return bcrypt.checkpw (password.encode(),self._password_hash)
  
  def __str__(self) -> str:
    return f"id: {self._user_id}, email: {self._email}"


@property 
def balance (self) -> int:
  return self._balance



class Admin (User):
  def __init__(self, user_id:int, nickname: str):
    super().__init__(
        user_id = user_id,
        email = os.getenv ('ADMIN_EMAIL', 'admin@mail.ru'),
        password = os.getenv ('ADMIN_PASSWORD', 'admin'),
        nickname = nickname)
    
  def recharge_balance (self, user:User, amount: int) -> None:
    pass
  def get_users (self):
    pass

class User_creation:
  def create_users():
   pass