from fastapi import APIRouter, HTTPException, status, Depends
from  database.database import get_session
from models.user import User, Admin
from models.llm import llm
from services.crud import user as UserService
from services.crud import llm as LlmService
from typing import List


user_route = APIRouter(tags=['User'])

async def get_current_user(session=Depends(get_session)) -> User:
    
    user_id = int  
    user = UserService.get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# def get_current_user(session=Depends(get_session)
# ) -> dict:
#     current_user = UserService.get_user_by_id(user_id, session)
#     return current_user

   

@user_route.post('/signup')
async def signup(data: User, session=Depends(get_session)) -> dict:
    if UserService.get_user_by_email(data.email, session) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with supplied username exists")
    
    UserService.create_user(data, session)
    return {"message": "User successfully registered!"}

@user_route.post('/signin')
async def signin(data: User, session=Depends(get_session)) -> dict:
    user = UserService.get_user_by_email(data.email, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    
    if user.password != data.password:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Wrong credentials passed")
    
   
    
    return { "message": "User signed in successfully"}




@user_route.get('/users', response_model=List[User])
async def get_all_users(session=Depends(get_session)) -> list:
    return UserService.get_all_users(session)

@user_route.get('/admins', response_model=List[Admin])
async def get_admins(session=Depends(get_session)) -> list:
    return UserService.get_admins(session)

# @user_route.post('/run_llm')
# async def run_llm (
#     llm_id: int, 
#     input_data: dict, 
#     user: User = Depends(get_current_user),
#     session=Depends(get_session)):
#     return LlmService.run_llm (user, llm_id, input_data, session)


@user_route.get("/balance")
async def get_balance(user_id: int, session = Depends (get_session)):
    user = UserService.get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"balance": user.balance}

@user_route.get("/history")
async def get_history(user_id: int, session = Depends (get_session)):
    user = UserService.get_user_by_id(user_id, session)
    if not user:
            raise HTTPException(status_code=404, detail="User not found")
    user_history = UserService.get_user_history(user_id, session)
    return {"history": user_history}

@user_route.post("/recharge")
async def recharge_balance(
    user_id: int,
    amount: int,
    admin_id:int,
    session=Depends(get_session)
):
    admin = session.query(Admin).filter(Admin.admin_id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    return UserService.recharge_balance(admin, user_id, amount, session)