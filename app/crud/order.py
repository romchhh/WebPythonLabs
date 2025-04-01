from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate
from models import Order
from schemas import OrderCreate
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from .base import CRUDBase

def get_order(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()

def create_order(db: Session, order: OrderCreate):
    db_order = Order(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

class CRUDOrder(CRUDBase[Order, OrderCreate, Order]):
    async def get_user_orders(
        self,
        db: AsyncIOMotorDatabase,
        *,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Order]:
        filter_query = {"user_id": ObjectId(user_id)}
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filter_query=filter_query
        )

    async def create_with_items(
        self,
        db: AsyncIOMotorDatabase,
        *,
        obj_in: OrderCreate
    ) -> Order:
        # Перевірка наявності товарів
        for item in obj_in.items:
            product = await db["products"].find_one({"_id": ObjectId(item.product_id)})
            if not product or product["stock"] < item.quantity:
                raise ValueError(f"Insufficient stock for product {item.product_id}")
            
            # Оновлення кількості товару
            await db["products"].update_one(
                {"_id": ObjectId(item.product_id)},
                {"$inc": {"stock": -item.quantity}}
            )
        
        return await super().create(db, obj_in=obj_in)

    async def update_status(
        self,
        db: AsyncIOMotorDatabase,
        *,
        order_id: str,
        status: str
    ) -> Optional[Order]:
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        return await self.update(db, id=order_id, obj_in=update_data)

    async def get_orders_by_status(
        self,
        db: AsyncIOMotorDatabase,
        *,
        status: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Order]:
        filter_query = {"status": status}
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filter_query=filter_query
        )

order = CRUDOrder(Order, "orders")
