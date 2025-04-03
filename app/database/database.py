from sqlmodel import SQLModel, Session, create_engine, text  
from contextlib import contextmanager
from .config import get_settings
from services.crud.user import get_all_users, create_user
from models.user import user, admin, user_history 
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

    demo_user = user (user_id = 1, email = "demo@email.ru", password = "test", nickname = "u_demo", balance = 5)
    demo_admin = admin (admin_id = 1, email = "admin@email.ru", password = "pass",nickname = "admin")
    
    with Session(engine) as session:

        create_user(demo_user, session) 
        create_user(demo_admin, session)

        session.commit()  

