
import hashlib
from datetime import datetime

class User:
  def __init__(self, user_id:int, email:str, password:str, nickname:str, balance:int=5):
    self._email = email
    self._user_id = id
    self._password_hash = self._hash_password(password)
    self._nickname = nickname
    self._balance = balance

  def hash_password (password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

  def check_password(self, password: str) -> bool:
   return self._password_hash == self._hash_password(password)

  @property 
  def balance (self) -> int:
    return self._balance



class Admin (User):
  def __init__(self, user_id:int, nickname: str):
    super().init(user_id = id,
        email = 'admin@mail.ru',
        password = 'admin',
        nickname = nickname)
    
  def recharge_balance (self, user:User, amount: int) -> None:
    pass
  def get_users (self):
    pass


class User_creation:
  def create_users():
   pass

class LLM:
  def __init__(self, title:str, description:str, creator: User): 
    self.title = title
    self.description = description
    self.creator = creator
  
  def run ():
    pass

class Transaction:
  def __init__(self, transaction_id:int, user: User, amount: int):
    self._transaction_id =transaction_id
    self._user = user
    self._amount = amount
    self._timestamp = datetime.now ()

  def do_transaction ():
    pass
  
