from datetime import datetime
from models.user import User

class LLM:
  def __init__(self, title:str, description:str, creator: User): 
    self.title = title
    self.description = description
    self.creator = creator
  
  def run ():
    pass

class PredictionTask:
  def __init__(self, task_id:int, model: LLM, user: User ):
    self.task_id = task_id
    self.model = model
    self.user = user
    self.created_at = datetime.now ()
    

class Transaction:
  def __init__(self, transaction_id:int, user: User, amount: int):
    self._transaction_id =transaction_id
    self._user = user
    self._amount = amount
    self._timestamp = datetime.now ()

  def do_transaction ():
    pass
  
class History:
  def __init__ (self):
    self._predictions =[]
    self._transactions = []

  def add_prediction (self, task:PredictionTask) -> None:
    self._predictions.append (task)

  def add_transaction (self, transaction: Transaction) -> None:
    self._transactions.append (transaction)