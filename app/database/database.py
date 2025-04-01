from sqlmodel import SQLModel, Session, create_engine, text  
from contextlib import contextmanager
from .config import get_settings
from services.crud.user import get_all_users, create_user
from models.user import User, Admin, UserHistory 
from models.LLM import LLM, PredictionTask, Transaction, History, TaskStatus
from datetime import datetime

engine = create_engine(url=get_settings().DATABASE_URL_psycopg, 
                       echo=True, pool_size=5, max_overflow=10)

def get_session():
    with Session(engine) as session:
        yield session
         
def init_database():
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))
        try:
            conn.execute(text(f"CREATE DATABASE {get_settings().DB_NAME}"))
        except Exception as e:
            print(f"Database already exists: {e}")

    # SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    demo_user = User (User_id = 1, email = "test1@email.ru", password = "test", nickname = "u_demo", balance = 5)
    demo_user_2 = User (User_id = 2, email = "test2@email.ru", password = "test",nickname = "u2_demo", balance = 5)
    demo_admin = Admin (Admin_id = 1, email = "admin@email.ru", password = "pass",nickname = "admin")
    demo_LLM = LLM(
                title="LLM", 
                description="AI model", 
                cost_per_request=2
            )
    with Session(engine) as session:

        create_user(demo_user, session) 
        create_user(demo_user_2, session)   
        create_user(demo_admin, session)

        session.add(demo_LLM)

        session.commit()  

    demo_task = PredictionTask(
    LLM_id=1,
    User_id=1,
    input_data="Запрос от пользователя",
    created_at=datetime.now(),
    cost=2,
    status=TaskStatus.PENDING.value
    )

    demo_transaction = Transaction(
        User_id=1,
        amount=-2,
        description="Успешная транзакция",
        created_at=datetime.now(),
        related_task_id=1,
        status="completed"
    )

    session.add_all([demo_task, demo_transaction])
    session.commit()