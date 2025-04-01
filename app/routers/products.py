from fastapi import APIRouter, Depends, HTTPException, Request, Form
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
import models
from database import get_async_db
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from .users import get_current_user
from crud.product import product as product_crud

router = APIRouter(tags=["products"])
templates = Jinja2Templates(directory="templates")

@router.get("/products")
async def list_products(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_async_db),
    search: str = None,
    category: str = None
):
    if search:
        products = await product_crud.search_products(db, query=search)
    elif category:
        products = await product_crud.get_by_category(db, category=category)
    else:
        products = await product_crud.get_multi(db, limit=100)
    
    current_user = get_current_user()
    is_admin = current_user and current_user.get("is_admin", False)
    
    return templates.TemplateResponse(
        "products.html",
        {
            "request": request,
            "products": products,
            "is_admin": is_admin,
            "user": current_user,
            "search": search,
            "category": category
        }
    )

@router.get("/products/new")
async def new_product_page(request: Request):
    current_user = get_current_user()
    if not current_user or not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    return templates.TemplateResponse("new_product.html", {"request": request, "user": current_user})

@router.post("/products/new")
async def create_product(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    category: str = Form(None),
    image_url: Optional[str] = Form(None),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    current_user = get_current_user()
    if not current_user or not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    product_in = models.ProductCreate(
        name=name,
        description=description,
        price=price,
        stock=stock,
        category=category,
        image_url=image_url
    )
    await product_crud.create(db, obj_in=product_in)
    return RedirectResponse(url="/products", status_code=303)

@router.get("/products/{product_id}/edit")
async def edit_product_page(request: Request, product_id: str, db: AsyncIOMotorDatabase = Depends(get_async_db)):
    current_user = get_current_user()
    if not current_user or not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    
    product = await product_crud.get(db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не знайдено")
    return templates.TemplateResponse(
        "edit_product.html",
        {"request": request, "product": product, "user": current_user}
    )

@router.post("/products/{product_id}/edit")
async def update_product(
    product_id: str,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    category: str = Form(None),
    image_url: Optional[str] = Form(None),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    current_user = get_current_user()
    if not current_user or not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    product_data = {
        "name": name,
        "description": description,
        "price": price,
        "stock": stock,
        "category": category,
        "image_url": image_url
    }
    await product_crud.update(db, id=product_id, obj_in=product_data)
    return RedirectResponse(url="/products", status_code=303)

@router.post("/products/{product_id}/delete")
async def delete_product(
    product_id: str,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    current_user = get_current_user()
    if not current_user or not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await product_crud.delete(db, id=product_id)
    return RedirectResponse(url="/products", status_code=303) 