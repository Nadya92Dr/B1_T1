from fastapi import APIRouter, Body, HTTPException, status, Depends
from database.database import get_session
from models.llm import llm, prediction_task 
from typing import List

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
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task with supplied ID does not exist")

@prediction_task_router.post("/new")
async def create_prediction_task(body: prediction_task = Body(...)) -> dict: 
    prediction_tasks.append(body)
    return {"message": "Prediction_task created successfully"}

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