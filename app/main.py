from models.user import User
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get('/')
def index():
    nickname = User (1, 'Nadya@gmail.com')
    return "HI" + nickname

if __name__ == '__main__':
    uvicorn.run ('main:app', host='0.0.0.0', port=8080, reload=True)
