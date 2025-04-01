from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import Product, ProductCreate
from .base import CRUDBase
from bson import ObjectId

class CRUDProduct(CRUDBase[Product, ProductCreate, Product]):
    async def search_products(
        self,
        db: AsyncIOMotorDatabase,
        *,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Product]:
        filter_query = {
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"category": {"$regex": query, "$options": "i"}}
            ]
        }
        cursor = db[self.collection_name].find(filter_query).skip(skip).limit(limit)
        
        results = await cursor.to_list(length=limit)
        return [Product(**doc) for doc in results]

    async def get_by_category(
        self,
        db: AsyncIOMotorDatabase,
        *,
        category: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Product]:
        filter_query = {"category": category}
        return await self.get_multi(db, skip=skip, limit=limit, filter_query=filter_query)

    async def update_stock(
        self,
        db: AsyncIOMotorDatabase,
        *,
        product_id: str,
        quantity: int
    ) -> Optional[Product]:
        update_data = {
            "$inc": {"stock": quantity}
        }
        result = await db[self.collection_name].find_one_and_update(
            {"_id": ObjectId(product_id)},
            update_data,
            return_document=True
        )
        if result:
            return Product(**result)
        return None

product = CRUDProduct(Product, "products")

