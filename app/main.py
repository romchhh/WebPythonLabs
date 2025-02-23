from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers import users, products, orders
from database import engine, Base
import os

app = FastAPI()

# Отримуємо абсолютний шлях до директорії static та templates
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
templates_dir = os.path.join(current_dir, "templates")

# Монтування статичних файлів
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Налаштування шаблонів
templates = Jinja2Templates(directory=templates_dir)

# Підключення роутерів
app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)

# Створення таблиць у БД
Base.metadata.create_all(bind=engine)

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "products": [], "user": None})

@app.exception_handler(500)
async def internal_error(request: Request, exc: Exception):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error": str(exc)},
        status_code=500
    )