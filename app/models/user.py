import bcrypt
import os
from sqlmodel import SQLModel, Field, Relationship, ForeignKey 
from typing import Optional
from datetime import datetime

class User (SQLModel, table=True):
    user_id: int = Field (default = None, primary_key=True)
    email:str
    password: str
    nickname: str
    balance: int
    transaction: Optional[str] = None

    tasks: list ["models.llm.prediction_task"] = Relationship (back_populates="user")


    def say(self):
        return "HI!"

class User_history (SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field (foreign_key = ('user.user_id'))
    action: str
    timestamp: datetime 
    details: str


class Admin (SQLModel, table=True):
    admin_id:int = Field(default=None, primary_key=True)
    email:str
    password: str
    nickname: str


    def say(self):
        return "HI, Im admin!"
    
    