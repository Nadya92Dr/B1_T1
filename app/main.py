from database.config import get_settings
from database.database import get_session, init_database, engine
from sqlmodel import SQLModel, Session
from services.crud.user import get_all_users, create_user

from models.user import User
from fastapi import FastAPI
import uvicorn
from models.LLM import LLM


app = FastAPI()

@app.get('/')
def index():
    nickname = User (1, 'Nadya@gmail.com')
    return "HI" + nickname

if __name__ == '__main__':
    # test_user = User (User_id = 1, email = "test1@email.ru", password = "test", nickname = "u1", balance = 5)
    # test_user_2 = User (User_id = 2, email = "test2@email.ru", password = "test",nickname = "u2", balance = 5)
    # test_user_3 = User (User_id = 3, email = "test3@email.ru", password = "test",nickname = "u3", balance = 5)

    # uvicorn.run ('main:app', host='0.0.0.0', port=8080, reload=True)

    settings = get_settings ()
    # print (settings.DB_HOST)
    # print (settings.DB_NAME)
    # print (settings.DB_USER)
    
    init_database()
    print ("Init db has been success")

    # with Session (engine) as session:
    #     create_user(test_user, session) 
    #     create_user(test_user_2, session)   
    #     create_user(test_user_3, session)
    #     users = get_all_users(session)

    # for user in users:
    #     print(f'id: {user.User_id} - {user.email} - {user.nickname} - {user.balance}')
    #     print (type (user))
    #     print (user.say ())
