from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from .users import get_current_user

router = APIRouter(tags=["products"])
templates = Jinja2Templates(directory="templates")

@router.get("/products")
async def list_products(request: Request, db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    current_user = get_current_user()
    is_admin = current_user and current_user.get("is_admin", False)
    return templates.TemplateResponse(
        "products.html",
        {
            "request": request, 
            "products": products,
            "is_admin": is_admin,
            "user": current_user
        }
    )

@router.get("/products/new")
async def new_product_page(request: Request):
    current_user = get_current_user()
    if not current_user or not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    return templates.TemplateResponse("new_product.html", {"request": request})

@router.post("/products/new")
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    db: Session = Depends(get_db)
):
    current_user = get_current_user()
    if not current_user or not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    
    product = models.Product(
        name=name,
        description=description,
        price=price,
        stock=stock
    )
    db.add(product)
    db.commit()
    return RedirectResponse(url="/products", status_code=303)

@router.get("/products/{product_id}/edit")
async def edit_product_page(request: Request, product_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user()
    if not current_user or not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не знайдено")
    return templates.TemplateResponse(
        "edit_product.html",
        {"request": request, "product": product}
    )

@router.post("/products/{product_id}/edit")
async def edit_product(
    product_id: int,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    db: Session = Depends(get_db)
):
    current_user = get_current_user()
    if not current_user or not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не знайдено")
    
    product.name = name
    product.description = description
    product.price = price
    product.stock = stock
    
    db.commit()
    return RedirectResponse(url="/products", status_code=303)

@router.post("/products/{product_id}/delete")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user()
    if not current_user or not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не знайдено")
    
    db.delete(product)
    db.commit()
    return RedirectResponse(url="/products", status_code=303) 