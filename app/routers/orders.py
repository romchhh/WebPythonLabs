from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict
import models
from database import get_async_db
from fastapi.templating import Jinja2Templates
from .users import get_current_user, shopping_carts
from crud.order import order as order_crud
from bson import ObjectId
from crud.product import product as product_crud

router = APIRouter(tags=["orders"])
templates = Jinja2Templates(directory="templates")

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
    product_id: str,
    quantity: int = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    current_user = get_current_user()
    if not current_user:
        raise HTTPException(status_code=403, detail="Спочатку увійдіть в систему")
    
    product = await db["products"].find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не знайдено")
    
    if product["stock"] < quantity:
        raise HTTPException(status_code=400, detail="Недостатньо товару на складі")
    
    if current_user["email"] not in shopping_carts:
        shopping_carts[current_user["email"]] = []
    
    # Перевіряємо, чи товар вже є в кошику
    for item in shopping_carts[current_user["email"]]:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            return RedirectResponse(url="/cart", status_code=303)
    
    # Додаємо новий товар з URL зображення (якщо є)
    shopping_carts[current_user["email"]].append({
        "product_id": product_id,
        "name": product["name"],
        "price": product["price"],
        "quantity": quantity,
        "image_url": product.get("image_url", None)  # Додаємо URL зображення товару
    })
    
    return RedirectResponse(url="/cart", status_code=303)

@router.post("/cart/update/{product_id}")
async def update_cart_item(
    product_id: str,
    quantity: int = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
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
async def remove_from_cart(product_id: str):
    current_user = get_current_user()
    if not current_user:
        raise HTTPException(status_code=403, detail="Спочатку увійдіть в систему")
    
    cart = shopping_carts.get(current_user["email"], [])
    shopping_carts[current_user["email"]] = [
        item for item in cart if item["product_id"] != product_id
    ]
    
    return RedirectResponse(url="/cart", status_code=303)

@router.post("/orders")
async def create_order(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    current_user = get_current_user()
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    cart_items = shopping_carts.get(current_user["email"], [])
    if not cart_items:
        raise HTTPException(status_code=400, detail="Кошик порожній")
    
    # Створюємо список елементів замовлення з усіма необхідними полями
    order_items = [
        models.OrderItemBase(
            product_id=item["product_id"],
            quantity=item["quantity"],
            price=item["price"],
            product_name=item["name"]
        )
        for item in cart_items
    ]
    
    # Обчислюємо загальну суму замовлення
    total_amount = sum(item.price * item.quantity for item in order_items)
    
    order_in = models.OrderCreate(
        user_id=current_user["id"],
        items=order_items,
        total_amount=total_amount
    )
    
    try:
        await order_crud.create_with_items(db, obj_in=order_in)
        # Очищаємо кошик після успішного створення замовлення
        shopping_carts[current_user["email"]] = []
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return RedirectResponse(url="/orders", status_code=303)

@router.get("/orders")
async def list_orders(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    current_user = get_current_user()
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    if current_user.get("is_admin"):
        orders = await order_crud.get_multi(db, limit=100)
    else:
        orders = await order_crud.get_user_orders(db, user_id=current_user["id"])
    
    return templates.TemplateResponse(
        "orders.html",
        {
            "request": request,
            "orders": orders,
            "user": current_user
        }
    )

@router.get("/admin/crm")
async def admin_crm(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    current_user = get_current_user()
    if not current_user or not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    
    # Отримуємо всі замовлення
    orders = await order_crud.get_multi(db, limit=100)
    
    # Статистика по замовленнях
    total_orders = len(orders)
    total_revenue = sum(
        item.price * item.quantity
        for order in orders
        for item in order.items
    )
    
    # Статистика по статусам замовлень
    status_counts = {}
    for order in orders:
        status_counts[order.status] = status_counts.get(order.status, 0) + 1
    
    # Отримуємо всі продукти для інвентаря
    products = await product_crud.get_multi(db, limit=100)
    
    # Статистика по продуктах
    low_stock_products = [p for p in products if p.stock < 10]
    out_of_stock_products = [p for p in products if p.stock == 0]
    
    return templates.TemplateResponse(
        "admin/crm.html",
        {
            "request": request,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "status_counts": status_counts,
            "low_stock_products": low_stock_products,
            "out_of_stock_products": out_of_stock_products,
            "user": current_user
        }
    )

@router.post("/orders/{order_id}/update-status")
async def update_order_status(
    order_id: str,
    status: str = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    current_user = get_current_user()
    if not current_user or not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await order_crud.update_status(db, order_id=order_id, status=status)
    return RedirectResponse(url="/orders", status_code=303) 