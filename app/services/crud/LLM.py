from models.llm import llm, prediction_task, transaction
from models.user import User
from services.crud.llm_inference import llm_service
from models.llm import task_status
from services.rm.rm import send_task

from typing import List, Optional


def process_task_async(task_id: int, input_data: str, session):
    with session.begin():
        task = session.get(prediction_task, task_id)
        user = session.get (User, task.user_id)

        try:
            result = llm_service.process_request(input_data)
            user.balance -= task.cost
            task.result = result
            task.status = task_status.COMPLETED.value

            transaction = transaction(
                user_id=user.user_id,
                amount=-task.cost,
                description=f"LLM request {task.llm_id}",
                related_task_id=task.prediction_task_id,
                status="completed"
            )
            session.add(transaction)
            
        except Exception as e:
            task.status = task_status.FAILED.value
            task.result = str(e)
        session.commit()


def get_all_transactions(session) -> List[transaction]:
    return session.query(transaction).all()

def get_transactions_by_id(transaction_id:int, session) -> Optional[transaction]:
    transaction = session.get(transaction, transaction_id) 
    if transaction:
        return transaction 
    return None



def create_transaction(new_transaction: transaction, session) -> None:
    session.add(new_transaction) 
    session.commit() 
    session.refresh(new_transaction)
    
def delete_all_predictions(session) -> None:
    session.query(prediction_task).delete()
    session.commit()
    
def delete_predictions_by_id(task_id:int, session) -> None:
    prediction_task = session.get(prediction_task, task_id)
    if prediction_task:
        session.delete(prediction_task)
        session.commit()
        return
        
    raise Exception("PredictionTask with supplied ID does not exist")

def create_llm (new_llm: llm, session) -> llm:
    session.add(new_llm) 
    session.commit() 
    session.refresh(new_llm)
    return new_llm

def run_llm (user_id:int, llm_id: int, input_data: str, session,  background_tasks):
    user = session.get(User, user_id)
    llm_model = session.get (llm, llm_id)
    if not llm_model:
        raise ValueError ("LLM model not found")
    if user.balance < llm_model.cost_per_request:
     raise ValueError("Недостаточно средств на балансе")
    

    new_task = prediction_task (
        llm_id = llm_model.llm_id,
        user_id = user.user_id,
        input_data = input_data,
        cost = llm_model.cost_per_request,
        status = task_status.PENDING.value
    )
    session.add(new_task)
    session.flush()

    task_data = {
        'task_id': new_task.prediction_task_id,
        'input_data': input_data,
        'llm_id': llm_id
    }
    send_task(task_data)

    # background_tasks.add_task(process_task_async, 
    # new_task.prediction_task_id, input_data, session)

    new_transaction = transaction(
          user_id=user.user_id,
          amount=llm_model.cost_per_request,
          description=f"LLM запрос {llm_id}",
          related_task_id=new_task.prediction_task_id,
          status = "completed"
      )
    
    user.balance -= llm_model.cost_per_request

    session.add (new_transaction)
    session.commit()
    return new_task 

