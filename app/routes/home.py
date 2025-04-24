from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from auth.authenticate import authenticate_cookie, authenticate
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from database.database import get_session
from services.crud import user as UserService
from models.user import User 
from routes.user import get_current_user
from database.config import get_settings
from typing import Dict

settings = get_settings()
home_route = APIRouter()
hash_password = HashPassword()
templates = Jinja2Templates(directory="view")

@home_route.get("/", response_class=HTMLResponse)
async def index(request: Request):
    token = request.cookies.get(settings.COOKIE_NAME)
    if token:
        user = await authenticate_cookie(token)
    else:
        user = None

    context = {
        "user": user,
        "request": request
    }
    return templates.TemplateResponse("index.html", context)




@home_route.get("/private", response_class=HTMLResponse)
async def private_page(
    request: Request,
    user: User = Depends(get_current_user),
    session=Depends(get_session)
):
    history = UserService.get_user_history(user.user_id, session)
    context = {
        "user": user,
        "history": history,
        "request": request
    }
    return templates.TemplateResponse("private.html", context)


@home_route.get("/private2")
async def index_privat2(request: Request, user:str=Depends(authenticate)):
    return {"user": user}

@home_route.get(
    "/health",
    response_model=Dict[str, str],
    summary="Health check endpoint",
    description="Returns service health status"
)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring.

    Returns:
        Dict[str, str]: Health status message
    
    Raises:
        HTTPException: If service is unhealthy
    """
    try:
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail="Service unavailable"
        )





