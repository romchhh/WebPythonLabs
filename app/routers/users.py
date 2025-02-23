from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db
from passlib.context import CryptContext
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")

# Глобальна змінна для зберігання поточного користувача
current_user = None

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    global current_user
    # Перевірка на адміністратора
    if email == "roman.fedoniuk@gmail.com" and password == "123456":
        current_user = {"email": email, "is_admin": True}
        return RedirectResponse(url="/products", status_code=303)
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неправильний email або пароль")
    
    current_user = {"email": user.email, "is_admin": False}
    return RedirectResponse(url="/products", status_code=303)

@router.get("/logout")
async def logout():
    global current_user
    current_user = None
    return RedirectResponse(url="/login", status_code=303)

def get_current_user():
    return current_user

@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    db_user = models.User(
        email=email,
        username=username,
        hashed_password=pwd_context.hash(password)
    )
    db.add(db_user)
    db.commit()
    return RedirectResponse(url="/login", status_code=303) 