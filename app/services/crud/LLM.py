from models.llm import llm, prediction_task, transaction
from models.user import user
from typing import List, Optional


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



def run_llm (user: user, llm_id: int, input_data: dict, session) -> dict:
    if user.balance <= 0:
     raise ValueError("Недостаточно средств на балансе")
    
    
    new_task = prediction_task(
          llm_id=llm.llm_id,
          user_id=user.user_id,
          cost=llm.cost,
          input_data=str,
          status="в обработке"
      )
    
    new_transaction = transaction(
          user_id=user.user_id,
          amount=transaction.amount,
          description=f"LLM запрос {llm_id}",
          related_task_id=new_task.task_id
      )
      
    session.add_all([new_task, new_transaction])
    session.commit()
    
    try:
        result = run_llm (llm_id, input_data)
        new_task.status = "завершено"
        new_task.result = str(result)
    except Exception as e:
        new_task.status = "failed"
      
    session.commit()
    return new_task