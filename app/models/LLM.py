from datetime import datetime
from models.user import User
from sqlmodel import SQLModel, Field, Relationship, ForeignKey 
from typing import Optional
from enum import Enum

class TaskStatus(str, Enum):
  PENDING = "pending"
  COMPLETED = "completed"
  FAILED = "failed"

class PredictionTask (SQLModel, table = True):

    Task_id: int = Field (default = None, primary_key=True)
    LLM_id: int = Field (foreign_key = ("llm.llm_id"))
    User_id: int = Field (foreign_key = ("user.user_id"))
    input_data: str
    created_at: datetime = Field (default_factory=datetime.utcnow)
    cost: int
    result: Optional [str] =None
    status: str = 'pending'

    LLM: Optional ["LLM"] = Relationship (back_populates="tasks")
    user: Optional [User] = Relationship (back_populates="tasks")


class Transaction (SQLModel, table = True):
    
    Transaction_id: int = Field (default = None, primary_key=True)
    User_id: int = Field (foreign_key = ("user.user_id"))
    amount: int
    description: str
    created_at: datetime = Field (default_factory=datetime.utcnow)
    related_task_id: int = Field (foreign_key = ("predictiontask.task_id"))
    status:str = 'completed'

    def do_transaction ():
      pass

class History (SQLModel, table = True):
  
    History_id: int = Field (default = None, primary_key=True)
    predictions: Optional [str]
    transactions: Optional [str]
    User_id: int = Field (foreign_key = ("user.user_id"))
    created_at: datetime = Field (default_factory=datetime.utcnow)


class LLM (SQLModel, table=True):
  
    LLM_id: int = Field (default = None, primary_key=True)
    title: str
    description: str
    creator: Optional[str] = None
    cost_per_request: int

    tasks: list [PredictionTask] = Relationship (back_populates="LLM")

