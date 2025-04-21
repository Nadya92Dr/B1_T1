from sqlmodel import SQLModel, Session, create_engine
from .config import get_settings
from services.crud.user import create_user
from models.user import User, Admin
from models.llm import llm
from services.crud.llm import create_llm


def get_database_engine():
    """
    Create and configure the SQLAlchemy engine.
    
    Returns:
        Engine: Configured SQLAlchemy engine
    """
    settings = get_settings()
    
    engine = create_engine(
        url=settings.DATABASE_URL_psycopg,
        echo=settings.DEBUG,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    return engine

engine = get_database_engine()

def get_session():
    with Session(engine) as session:
        yield session
         
def init_database(drop_all: bool = False) -> None:
    try:
        engine = get_database_engine()
        if drop_all:
            SQLModel.metadata.drop_all(engine)
        
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        raise

    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    demo_user = User (user_id = 1, email = "demo@email.ru", password = "test", nickname = "u_demo", balance = 5)
    demo_admin = Admin (admin_id = 2, email = "admin@email.ru", password = "pass",nickname = "admin")
    demo_llm = llm (llm_id = 1, title = "демо ллм", description = "описание", cost_per_request = 3)



    with Session(engine) as session:

        create_user(demo_user, session) 
        create_user(demo_admin, session)
        create_llm (demo_llm, session)
        session.add (demo_admin)
        
        session.commit()  
        session.refresh (demo_admin)

