from datetime import datetime
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship
from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
import torch
from typing import Optional
from enum import Enum
from models.user import User

model = Qwen2VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2-VL-2B-Instruct",
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
    device_map="auto",
)

min_pixels = 256*28*28
max_pixels = 1280*28*28
processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-2B-Instruct", 
min_pixels=min_pixels, max_pixels=max_pixels)

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                "image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg",
            },
            {"type": "text", "text": "Describe this image."},
        ],
    }
]

text = processor.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True
)
image_inputs, video_inputs = process_vision_info(messages)
inputs = processor(
    text=[text],
    images=image_inputs,
    videos=video_inputs,
    padding=True,
    return_tensors="pt",
)
inputs = inputs.to("cuda")

generated_ids = model.generate(**inputs, max_new_tokens=128)
generated_ids_trimmed = [
    out_ids[len(in_ids) :] 
    for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
]
output_text = processor.batch_decode(
    generated_ids_trimmed, 
    skip_special_tokens=True, 
    clean_up_tokenization_spaces=False
)
print(output_text)

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
    image_url: str
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




