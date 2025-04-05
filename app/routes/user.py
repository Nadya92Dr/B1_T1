from fastapi import APIRouter, HTTPException, status, Depends
from  database.database import get_session
from models.user import User, Admin
from models.llm import llm
from services.crud import user as UserService
from services.crud import llm as LlmService
from typing import List


user_route = APIRouter(tags=['User'])

def get_current_user(user_id :int, session=Depends(get_session)
) -> dict:
    current_user = UserService.get_user_by_id(user_id, session)
    return current_user
    

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




@user_route.get('/get_all_users', response_model=List[User])
async def get_all_users(session=Depends(get_session)) -> list:
    return UserService.get_all_users(session)

@user_route.get('/get_admins', response_model=List[Admin])
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
async def get_balance(data: User = Depends(get_current_user)):
    return {"balance": get_balance.balance}

@user_route.get("/history")
async def get_history(data: User = Depends(get_current_user), session = Depends (get_session)):
    return UserService.get_user_history(User.user_id, session)

@user_route.post("/recharge")
async def recharge_balance(
    user_id: int,
    amount: int,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session)
):
    admin = session.query(Admin).filter(Admin.admin_id == current_user.user_id).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    return UserService.recharge_balance(admin, user_id, amount, session)