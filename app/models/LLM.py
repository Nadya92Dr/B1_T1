from datetime import datetime
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Optional
from enum import Enum
from models.user import User

model_name = "Qwen/Qwen2.5-0.5B-Instruct"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

prompt = "Give me a short introduction to large language model."
messages = [
    {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
    {"role": "user", "content": prompt}
]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=512
)
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

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
    user_id: int = Field (foreign_key = ("user.user_id"))
    input_data: str
    created_at: datetime = Field (default_factory=datetime.utcnow)
    cost: int
    result: Optional [str] =None
    status: str = 'pending'

    llm: Optional ["llm"] = Relationship (back_populates="tasks")
    user: Optional ["User"] = Relationship (back_populates="tasks")

class prediction_request(BaseModel):
    text: str

class transaction (SQLModel, table = True):
    
    transaction_id: int = Field (default = None, primary_key=True)
    user_id: int = Field (foreign_key = ("user.user_id"))
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
    user_id: int = Field (foreign_key = ("user.user_id"))
    created_at: datetime = Field (default_factory=datetime.utcnow)




