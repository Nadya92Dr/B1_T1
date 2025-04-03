from datetime import datetime
from models.user import user
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from enum import Enum

class task_status(str, Enum):
  PENDING = "pending"
  COMPLETED = "completed"
  FAILED = "failed"

class prediction_task (SQLModel, table = True):

    task_id: int = Field (default = None, primary_key=True)
    llm_id: int = Field (foreign_key = ("llm.llm_id"))
    user_id: int = Field (foreign_key = ("user.user_id"))
    input_data: str
    created_at: datetime = Field (default_factory=datetime.utcnow)
    cost: int
    result: Optional [str] =None
    status: str = 'pending'

    llm: Optional [llm] = Relationship (back_populates="tasks")
    user: Optional [user] = Relationship (back_populates="tasks")


class transaction (SQLModel, table = True):
    
    transaction_id: int = Field (default = None, primary_key=True)
    user_id: int = Field (foreign_key = ("user.user_id"))
    amount: int
    description: str
    created_at: datetime = Field (default_factory=datetime.utcnow)
    related_task_id: int = Field (foreign_key = ("prediction_task.task_id"))
    status:str = 'completed'

    def do_transaction ():
      pass

class history (SQLModel, table = True):
  
    history_id: int = Field (default = None, primary_key=True)
    predictions: Optional [str]
    transactions: Optional [str]
    user_id: int = Field (foreign_key = ("user.user_id"))
    created_at: datetime = Field (default_factory=datetime.utcnow)


class llm (SQLModel, table=True):
  
    llm_id: int = Field (default = None, primary_key=True)
    title: str
    description: str
    creator: Optional[str] = None
    cost_per_request: int

    tasks: list [prediction_task] = Relationship (back_populates="llm")

