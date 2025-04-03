from database.config import get_settings
from database.database import get_session, init_database, engine
from sqlmodel import SQLModel, Session
from services.crud.user import get_all_users, create_user
from datetime import datetime

from models.user import user
from fastapi import FastAPI
import uvicorn
from models.llm import llm, prediction_task, transaction, history, task_status


app = FastAPI()

@app.get('/')
def index():
    nickname = user (1, 'Nadya@gmail.com')
    return "HI" + nickname

if __name__ == '__main__':

    settings = get_settings ()
    # print (settings.DB_HOST)
    # print (settings.DB_NAME)
    # print (settings.DB_USER)
    
    init_database()
    print ("Init db has been success")

    test_user = user (user_id = 2, email = "test1@email.ru", password = "test", nickname = "u1", balance = 5)
    test_user_2 = user (user_id = 3, email = "test2@email.ru", password = "test",nickname = "u2", balance = 5)
    test_user_3 = user (user_id = 4, email = "test3@email.ru", password = "test",nickname = "u3", balance = 5)

    demo_llm = llm(
                title="LLM", 
                description="AI model", 
                cost_per_request=2
    )

    demo_task = prediction_task(
        llm_id=1,
        user_id=1,
        input_data="Запрос от пользователя",
        created_at=datetime.now(),
        cost=2,
        status=task_status.PENDING.value
        )

    demo_transaction = transaction(
            user_id=1,
            amount=-2,
            description="Успешная транзакция",
            created_at=datetime.now(),
            related_task_id=1,
            status="completed"
    )

    uvicorn.run ('main:app', host='0.0.0.0', port=8080, reload=True)

    with Session (engine) as session:
        create_user(test_user, session) 
        create_user(test_user_2, session)   
        create_user(test_user_3, session)
        users = get_all_users(session)

    for user in users:
        print(f'id: {user.User_id} - {user.email} - {user.nickname} - {user.balance}')
        print (type (user))
        print (user.say ())

    with Session (engine) as session:
        session.add(demo_llm)
        session.add_all([demo_task, demo_transaction])
        session.commit()