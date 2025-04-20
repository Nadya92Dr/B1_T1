from fastapi import APIRouter, Body, HTTPException, status, Depends, BackgroundTasks
from database.database import Session, get_session
from models.llm import llm, prediction_task, prediction_request, task_status
from models.user import User
from services.crud import user as UserService
from routes.user import get_current_user
from typing import List,Dict, Any
from pydantic import BaseModel
from sqlmodel import Session
from services.rm.rm import send_task

prediction_task_router = APIRouter(tags=["prediction_tasks"])

@prediction_task_router.get("/", response_model=List[prediction_task]) 
async def retrieve_all_predictions(
    session: Session = Depends(get_session)) -> List[prediction_task]:
    return session.query (prediction_task).all()

@prediction_task_router.get("/{id}", response_model=prediction_task) 
async def retrieve_predictions(
    id: int, session: Session = Depends (get_session)) -> prediction_task:
    task= session.get(prediction_task, id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                        detail="Task with supplied ID does not exist")
    return task

@prediction_task_router.get("/status/{task_id}")
async def get_task_status(task_id: int, session: Session =Depends(get_session)):
    task = session.get(prediction_task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "status": task.status,
        "result": task.result
    }


@prediction_task_router.delete("/{id}")
async def delete_prediction_task(
    id: int, session: Session = Depends (get_session)) -> dict: 
    task = session.get (prediction_task, id)
    if not task: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Task with supplied ID does not exist")

    session.delete(task)
    session.commit()
    return {"message": "Prediction task deleted successfully"}


@prediction_task_router.delete("/")
async def delete_all_prediction_tasks(
    session: Session = Depends(get_session)) -> dict:
    session.query(prediction_task).delete()
    session.commit()
    return {"message": "All prediction tasks deleted successfully"}


class prediction_request(BaseModel):
    text: str

@prediction_task_router.post(
    "/predict", 
    response_model=Dict[str, Any],
    summary="predict endpoint",
    description="Send predict request"
)
async def predict_endpoint(
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
        input_data=request.text,
        status=task_status.PENDING,
        result=None
    )
    
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    prediction_task({
        "task_id": db_task.prediction_task_id,
        "input_data": request.text
    })

    return {
        "task_id": db_task.prediction_task_id,
        "status": db_task.status,
        "message": "Task successfully queued"
    }
    
