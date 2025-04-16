from fastapi import APIRouter, Body, HTTPException, status, Depends, BackgroundTasks
from database.database import Session, get_session
from models.llm import llm, prediction_task, prediction_request, task_status
from models.user import User
from services.crud import llm as LlmService
from services.crud import user as UserService
from routes.user import get_current_user
from routes.ml import send_task
from typing import List,Dict, Any

prediction_task_router = APIRouter(tags=["prediction_tasks"])
prediction_tasks = []

@prediction_task_router.get("/", response_model=List[prediction_task]) 
async def retrieve_all_predictions() -> List[prediction_task]:
    return prediction_tasks

@prediction_task_router.get("/{id}", response_model=prediction_task) 
async def retrieve_predictions(id: int) -> prediction_task:
    for task in prediction_tasks: 
        if task.prediction_task_id == id:
            return task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                        detail="Task with supplied ID does not exist")

@prediction_task_router.get("/status/{task_id}")
async def get_task_status(task_id: int, session=Depends(get_session)):
    task = session.get(prediction_task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "status": task.status,
        "result": task.result
    }

@prediction_task_router.post("/new")
async def create_prediction_task(body: prediction_task = Body(...)) -> dict: 
    prediction_tasks.append(body)
    return {"message": "Prediction_task created successfully"}


@prediction_task_router.post("/predict", response_model=Dict[str, Any])
async def create_prediction(
    llm_id: int,
    user_id: int,
    request: prediction_request,
    # user: User= Depends(get_current_user),
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
)-> Dict [str, Any]:
    
    db_llm = session.get(llm, llm_id)
    if not db_llm:
        raise HTTPException(status_code=404, detail="LLM model not found")
    
    user = UserService.get_user_by_id (user_id, session)

    if user.balance <= 0:
        raise HTTPException(
            status_code=402,
            detail="Insufficient balance to process request"
        )
    
    db_task = prediction_task(
        user_id=user.user_id,
        llm_id=llm_id,
        input_data=request.text,
        status=task_status.PENDING,
        result=None
    )
    
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    send_task({
        "task_id": db_task.prediction_task_id,
        "llm_id": llm_id,
        "input_data": request.text
    })

    return {
        "task_id": db_task.prediction_task_id,
        "status": db_task.status,
        "message": "Prediction task queued"
    }

    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found")
    
    # try:
    #     task = LlmService.run_llm(
    #      user_id,
    #      llm_id, 
    #      request.text,
    #      session,
    #      background_tasks
    #      )
    #     return {"task_id": task.prediction_task_id, "status": "processing"}
    
    
    # except ValueError as e:
    #     raise HTTPException(status_code=400, detail=str(e))
    

    
    


@prediction_task_router.delete("/{id}")
async def delete_prediction_task(id: int) -> dict: 
    for task in prediction_tasks:
        if task.prediction_task_id == id: 
            prediction_tasks.remove(task)
            return {"message": "Task deleted successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task with supplied ID does not exist")

@prediction_task_router.delete("/")
async def delete_all_prediction_tasks() -> dict: 
    prediction_tasks.clear()
    return {"message": "Prediction task deleted successfully"}