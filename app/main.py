from database.config import get_settings
from database.database import init_database, engine
from sqlmodel import Session
from services.crud.user import get_all_users, create_user
from services.crud.llm import create_llm
from services.rm.rm import setup_result_consumer
from datetime import datetime
from models.user import User
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from routes.llm import prediction_task_router
from routes.home import home_route
from routes.user import user_route
from routes.auth import auth_route
import uvicorn
from models.llm import llm, prediction_task, transaction, task_status


app = FastAPI()
app.include_router(prediction_task_router)
app.include_router(home_route)
app.include_router(user_route)
app.include_router(auth_route)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="view")

@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "404.html",
        {"request": request},
        status_code=404
    )

@app.exception_handler(500)
async def server_error_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "500.html",
        {"request": request},
        status_code=500
    )

@app.get('/')
def index():
    nickname = user (1, 'Nadya@gmail.com')
    return "HI" + nickname

@app.on_event ("startup")
async def startup_event ():
    setup_result_consumer()


if __name__ == '__main__':

    settings = get_settings ()
    # print (settings.DB_HOST)
    # print (settings.DB_NAME)
    # print (settings.DB_USER)
    
    init_database()
    print ("Init db has been success")

    test_user = User (user_id = 3, email = "test1@email.ru", password = "test", nickname = "u1", balance = 5)
    test_user_2 = User (user_id = 4, email = "test2@email.ru", password = "test",nickname = "u2", balance = 5)
    test_user_3 = User (user_id = 5, email = "test3@email.ru", password = "test",nickname = "u3", balance = 5)

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
        create_llm (demo_llm, session)
        session.add(demo_llm)
        session.add_all([demo_task, demo_transaction])
        session.commit()