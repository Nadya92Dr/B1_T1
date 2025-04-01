from models.LLM import LLM, PredictionTask, Transaction, History
from models.user import User
from typing import List, Optional


def get_all_transactions(session) -> List[Transaction]:
    return session.query(Transaction).all()

def get_transactions_by_id(transaction_id:int, session) -> Optional[Transaction]:
    Transaction = session.get(Transaction, transaction_id) 
    if Transaction:
        return Transaction 
    return None



def create_transaction(new_transaction: Transaction, session) -> None:
    session.add(new_transaction) 
    session.commit() 
    session.refresh(new_transaction)
    
def delete_all_predictions(session) -> None:
    session.query(PredictionTask).delete()
    session.commit()
    
def delete_predictions_by_id(Task_id:int, session) -> None:
    PredictionTask = session.get(PredictionTask, Task_id)
    if PredictionTask:
        session.delete(PredictionTask)
        session.commit()
        return
        
    raise Exception("PredictionTask with supplied ID does not exist")



def run_LLM (user: User, llm_id: int, input_data: dict, session) -> dict:
    if user.balance <= 0:
     raise ValueError("Недостаточно средств на балансе")
    
    
    new_task = PredictionTask(
          LLM_id=LLM.LLM_id,
          User_id=user.User_id,
          cost=LLM.cost,
          input_data=str,
          status="в обработке"
      )
    
    new_transaction = Transaction(
          User_id=user.User_id,
          amount=Transaction.amount,
          description=f"LLM запрос {llm_id}",
          related_task_id=new_task.Task_id
      )
      
    session.add_all([new_task, new_transaction])
    session.commit()
    
    try:
        result = run_LLM (LLM_id, input_data)
        new_task.status = "завершено"
        new_task.result = str(result)
    except Exception as e:
        new_task.status = "failed"
      
    session.commit()
    return new_task