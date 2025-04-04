from fastapi import APIRouter

home_router = APIRouter()

@home_router.get('/', tags=['home'])
async def index() -> str:
    return "Hello World"