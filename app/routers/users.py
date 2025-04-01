from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any, Optional
import models
from database import get_async_db
from passlib.context import CryptContext
from fastapi.templating import Jinja2Templates
from crud.user import user as user_crud

router = APIRouter(tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")

# Глобальна змінна для зберігання поточного користувача
current_user = None

# Глобальна змінна для зберігання кошиків користувачів
shopping_carts: Dict[str, List[Dict]] = {}

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    user = await user_crud.authenticate(db, email=email, password=password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    global current_user
    current_user = {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "is_admin": user.is_admin
    }
    return RedirectResponse(url="/products", status_code=303)

@router.get("/logout")
async def logout():
    global current_user
    current_user = None
    return RedirectResponse(url="/login", status_code=303)

def get_cart_count() -> int:
    """Повертає кількість товарів у кошику поточного користувача"""
    if not current_user:
        return 0
    
    user_cart = shopping_carts.get(current_user["email"], [])
    return sum(item["quantity"] for item in user_cart)

def get_current_user() -> Optional[Dict[str, Any]]:
    """Повертає інформацію про поточного користувача"""
    if current_user:
        # Додаємо інформацію про кількість товарів у кошику
        result = current_user.copy()
        result["cart_count"] = get_cart_count()
        return result
    return None

@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    # Перевірка чи користувач вже існує
    existing_user = await user_crud.get_by_email(db, email=email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_in = models.UserCreate(
        email=email,
        username=username,
        password=password,
        is_admin=False
    )
    user = await user_crud.create(db, obj_in=user_in)
    return RedirectResponse(url="/login", status_code=303) 