from fastapi import APIRouter, HTTPException, status, Depends,Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from auth.authenticate import authenticate_cookie
from database.database import get_session
from database.config import get_settings
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from models.user import User, Admin
from services.crud import user as UserService
from typing import List, Dict
import logging


settings = get_settings()
templates = Jinja2Templates(directory="view")
logger = logging.getLogger(__name__)
user_route = APIRouter()
hash_password = HashPassword()

async def get_current_user(email: str = Depends(authenticate_cookie), 
                           session=Depends(get_session)) -> User:
    user = UserService.get_user_by_email(email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@user_route.get('/signup', response_class=HTMLResponse)
async def signup_form(request: Request, errors: list = []):
    return templates.TemplateResponse(
        "signup.html", {"request": request, "errors": errors, "email": ""})

@user_route.post('/signup', response_class=HTMLResponse)
async def signup(
    request: Request, 
    email: str = Form(...),
    password: str = Form(...), 
    session=Depends(get_session)
): 
     try:
        user_exist = UserService.get_user_by_email(email, session)
        if user_exist:
            return templates.TemplateResponse(
                "signup.html",
                {
                    "request": request,
                    "errors": ["User with this email already exists"],
                    "email": email
                },
                status_code=status.HTTP_409_CONFLICT
            )
        
        hashed_password = hash_password.create_hash(password)
        new_user = User (
            email=email, 
            password=hashed_password,
            nickname=email.split('@')[0],
            balance=5,
        )

        UserService.create_user(new_user, session)
        session.commit()

        access_token = create_access_token(new_user.email)
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(
            key=settings.COOKIE_NAME,
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=3600
        )
        return response
     except Exception as e:
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "errors": ["Internal server error"],
                "email": email
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
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