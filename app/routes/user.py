from fastapi import APIRouter, HTTPException, status, Depends,Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database.database import get_session
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from models.user import User, Admin
from models.llm import llm
from services.crud import user as UserService
from services.crud import llm as LlmService
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

user_route = APIRouter(tags=['User'])
hash_password = HashPassword()

async def get_current_user(session=Depends(get_session)) -> User:
    
    user_id = int  
    user = UserService.get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@user_route.get('/signup', response_class=HTMLResponse)
async def signup_form(request: Request):
    return templates.TemplateResponse(
        "signup.html", {"request": request, "errors": []})

@user_route.post('/signup', response_class=RedirectResponse)
async def signup(user: User, request: Request, email: str = Form(...),
                 password: str = Form(...), 
                 session=Depends(get_session)) -> Dict[str, str]:
   
    try:
        user_exist = UserService.get_user_by_email(user.email, session)
        
        if user_exist:
            return templates.TemplateResponse(
                "signup.html",
                {
                    "request": request,
                    "errors": ["User with this email already exists"],
                    "email": email
                },
                status_code=409
            )
        
        hashed_password = hash_password.create_hash(user.password)
        user = User(email=email, password=hashed_password)
        UserService.create_user(user, session)

        access_token = create_access_token(user.email)
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(
            key=settings.COOKIE_NAME,
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=3600
        )
        return response
        
    except Exception as e:
        logger.error(f"Error during signup: {str(e)}")
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "errors": ["Internal server error"],
                "email": email
            },
            status_code=500
        )


@user_route.post('/signin')
async def signin(form_data: OAuth2PasswordRequestForm = Depends(), 
                 session=Depends(get_session)
                 ) -> Dict[str, str]:

    user_exist = UserService.get_user_by_email(form_data.username, session)
    
    if not user_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist"
        )
    try:
        is_valid_password = hash_password.verify_hash(
            form_data.password,
            user_exist.password 
        )
    
    except Exception as e:
        logger.error(f"Password verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    
    if not is_valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    access_token = create_access_token(user_exist.email)
    return {"access_token": access_token, "token_type": "Bearer"}

@user_route.get('/users', response_model=List[User])
async def get_all_users(session=Depends(get_session)) -> list:
    return UserService.get_all_users(session)

@user_route.get('/admins', response_model=List[Admin])
async def get_admins(session=Depends(get_session)) -> list:
    return UserService.get_admins(session)


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