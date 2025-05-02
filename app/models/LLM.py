from datetime import datetime
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text
from typing import Optional
from enum import Enum
from models.user import User


class task_status(str, Enum):
  PENDING = "pending"
  COMPLETED = "completed"
  FAILED = "failed"

class llm (SQLModel, table=True):
  
    llm_id: int = Field (default = 1, primary_key=True)
    title: str
    description: str
    creator: Optional[str] = None
    cost_per_request: int

    tasks: list ["prediction_task"] = Relationship (back_populates="llm")


class prediction_task (SQLModel, table = True):

    prediction_task_id: int = Field (default = None, primary_key=True)
    llm_id: int = Field (foreign_key = ("llm.llm_id"))
    user_id: int = Field (foreign_key = ("user.id"))
    input_data: str
    created_at: datetime = Field (default_factory=datetime.utcnow)
    cost: int   
    result: Optional [str] = Field (sa_column=Column(Text))
    status: str = Field (default ="pending")

    llm: Optional ["llm"] = Relationship (back_populates="tasks")
    user: Optional ["User"] = Relationship (back_populates="tasks")

class prediction_request(BaseModel):
    text: str

class transaction (SQLModel, table = True):
    
    transaction_id: int = Field (default = None, primary_key=True)
    user_id: int = Field (foreign_key = ("user.id"))
    amount: int
    description: str
    created_at: datetime = Field (default_factory=datetime.utcnow)
    related_task_id: int = Field (foreign_key = ("prediction_task.prediction_task_id"))
    status:str = Field (default = 'completed')

    def do_transaction ():
      pass

class history (SQLModel, table = True):
  
    history_id: int = Field (default = None, primary_key=True)
    predictions: Optional [str]
    transactions: Optional [str]
    user_id: int = Field (foreign_key = ("user.id"))
    created_at: datetime = Field (default_factory=datetime.utcnow)




