from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Dict
import models, schemas
from database import get_db
from fastapi.templating import Jinja2Templates
from .users import get_current_user

router = APIRouter(tags=["orders"])
templates = Jinja2Templates(directory="templates")

# Тимчасове зберігання кошиків користувачів
shopping_carts: Dict[str, List[Dict]] = {}

@router.get("/cart")
async def view_cart(request: Request):
    current_user = get_current_user()
    if not current_user:
        raise HTTPException(status_code=403, detail="Спочатку увійдіть в систему")
    
    cart_items = shopping_carts.get(current_user["email"], [])
    total = sum(item["price"] * item["quantity"] for item in cart_items)
    
    return templates.TemplateResponse(
        "cart.html",
        {"request": request, "cart_items": cart_items, "total": total, "user": current_user}
    )

@router.post("/cart/add/{product_id}")
async def add_to_cart(
    product_id: int,
    quantity: int = Form(...),
    db: Session = Depends(get_db)
):
    current_user = get_current_user()
    if not current_user:
        raise HTTPException(status_code=403, detail="Спочатку увійдіть в систему")
    
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не знайдено")
    
    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="Недостатньо товару на складі")
    
    if current_user["email"] not in shopping_carts:
        shopping_carts[current_user["email"]] = []
    
    # Перевіряємо, чи товар вже є в кошику
    for item in shopping_carts[current_user["email"]]:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            return RedirectResponse(url="/cart", status_code=303)
    
    # Додаємо новий товар
    shopping_carts[current_user["email"]].append({
        "product_id": product_id,
        "name": product.name,
        "price": product.price,
        "quantity": quantity
    })
    
    return RedirectResponse(url="/cart", status_code=303)

@router.post("/cart/update/{product_id}")
async def update_cart_item(
    product_id: int,
    quantity: int = Form(...),
    db: Session = Depends(get_db)
):
    current_user = get_current_user()
    if not current_user:
        raise HTTPException(status_code=403, detail="Спочатку увійдіть в систему")
    
    cart = shopping_carts.get(current_user["email"], [])
    for item in cart:
        if item["product_id"] == product_id:
            if quantity <= 0:
                cart.remove(item)
            else:
                item["quantity"] = quantity
            break
    
    return RedirectResponse(url="/cart", status_code=303)

@router.post("/cart/remove/{product_id}")
async def remove_from_cart(product_id: int):
    current_user = get_current_user()
    if not current_user:
        raise HTTPException(status_code=403, detail="Спочатку увійдіть в систему")
    
    cart = shopping_carts.get(current_user["email"], [])
    shopping_carts[current_user["email"]] = [
        item for item in cart if item["product_id"] != product_id
    ]
    
    return RedirectResponse(url="/cart", status_code=303)

@router.post("/orders/create")
async def create_order(
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = get_current_user()
    if not current_user:
        raise HTTPException(status_code=403, detail="Спочатку увійдіть в систему")
    
    cart_items = shopping_carts.get(current_user["email"], [])
    if not cart_items:
        raise HTTPException(status_code=400, detail="Кошик порожній")
    
    # Створюємо замовлення
    user = db.query(models.User).filter(models.User.email == current_user["email"]).first()
    order = models.Order(user_id=user.id, status="new")
    db.add(order)
    db.commit()
    
    # Додаємо товари до замовлення
    for item in cart_items:
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=item["product_id"],
            quantity=item["quantity"]
        )
        db.add(order_item)
        
        # Оновлюємо кількість товару на складі
        product = db.query(models.Product).filter(models.Product.id == item["product_id"]).first()
        product.stock -= item["quantity"]
    
    db.commit()
    
    # Очищаємо кошик
    shopping_carts[current_user["email"]] = []
    
    return RedirectResponse(url="/orders", status_code=303)

@router.get("/orders")
async def list_orders(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user()
    if not current_user:
        raise HTTPException(status_code=403, detail="Спочатку увійдіть в систему")
    
    if current_user.get("is_admin"):
        orders = db.query(models.Order).all()
    else:
        user = db.query(models.User).filter(models.User.email == current_user["email"]).first()
        orders = db.query(models.Order).filter(models.Order.user_id == user.id).all()
    
    return templates.TemplateResponse(
        "orders.html",
        {"request": request, "orders": orders, "user": current_user}
    )

@router.get("/admin/crm")
async def admin_crm(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user()
    if not current_user or not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    
    orders = db.query(models.Order).all()
    total_revenue = sum(
        item.product.price * item.quantity 
        for order in orders 
        for item in order.items
    )
    
    stats = {
        "total_orders": len(orders),
        "total_revenue": total_revenue,
        "pending_orders": len([o for o in orders if o.status == "new"]),
        "completed_orders": len([o for o in orders if o.status == "completed"])
    }
    
    return templates.TemplateResponse(
        "admin_crm.html",
        {
            "request": request,
            "orders": orders,
            "stats": stats,
            "user": current_user
        }
    )

@router.post("/admin/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    current_user = get_current_user()
    if not current_user or not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Замовлення не знайдено")
    
    order.status = status
    db.commit()
    
    return RedirectResponse(url="/admin/crm", status_code=303) 