from fastapi import FastAPI
from routes.home import home_router
from routes.user import user_route
from routes.llm import prediction_task_router, ml_route
from database.database import init_database
import uvicorn

app = FastAPI()
app.include_router(home_router, tags=['home'])
app.include_router(user_route, prefix='/user')
app.include_router(prediction_task_router, prefix='/prediction', tags=['prediction_tasks'])
app.include_router(ml_route, tags=['ml_task'])

@app.on_event("startup") 
def on_startup():
     init_database()

if __name__ == '__main__':
    uvicorn.run('api:app', host='0.0.0.0', port=8080, reload=True)