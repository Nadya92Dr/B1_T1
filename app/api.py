from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from routes.home import home_route
from routes.user import user_route
from routes.auth import auth_route
from routes.llm import prediction_task_router
from database.database import init_database
from database.config import get_settings
import uvicorn
import logging
from fastapi.staticfiles import StaticFiles

templates = Jinja2Templates(directory="view")

logger = logging.getLogger(__name__)
settings = get_settings()

def create_application() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.API_VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(home_route, tags=['home'])
    app.include_router(user_route)
    app.include_router(prediction_task_router, prefix='/prediction', tags=['prediction_tasks'])
    app.include_router(auth_route, prefix="/auth", tags=["auth"])

    return app

app = create_application()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup") 
def on_startup():
    try:
        logger.info("Initializing database...")
        init_database(drop_all=True)
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise
    
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Application shutting down...")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    uvicorn.run(
        'api:app',
        host='0.0.0.0',
        port=8080,
        reload=True,
        log_level="info"
    )