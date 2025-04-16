from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session
from database.database import get_session
from models.llm import prediction_task, task_status
from models.user import User
from services.rm.rm import send_task
from routes.user import get_current_user

ml_route = APIRouter()

class prediction_request(BaseModel):
    text: str

@ml_route.post(
    "/send_task", 
    response_model=Dict[str, Any],
    summary="ML endpoint",
    description="Send ml request"
)
async def send_task_endpoint(
 request: prediction_request,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    
    if user.balance <= 0:
        raise HTTPException(
            status_code=402,
            detail="Insufficient balance to process request"
        )
    
    db_task = prediction_task(
        user_id=user.user_id,
        input_data=request.message,
        status=task_status.PENDING,
        result=None
    )
    
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    send_task({
        "task_id": db_task.prediction_task_id,
        "input_data": request.message
    })

    return {
        "task_id": db_task.prediction_task_id,
        "status": db_task.status,
        "message": "Task successfully queued"
    }
    
