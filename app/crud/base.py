from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], collection_name: str):
        self.model = model
        self.collection_name = collection_name

    async def get(self, db: AsyncIOMotorDatabase, id: str) -> Optional[ModelType]:
        if not ObjectId.is_valid(id):
            return None
        doc = await db[self.collection_name].find_one({"_id": ObjectId(id)})
        if doc:
            return self.model(**doc)
        return None

    async def get_multi(
        self,
        db: AsyncIOMotorDatabase,
        *,
        skip: int = 0,
        limit: int = 100,
        filter_query: Dict = None
    ) -> List[ModelType]:
        filter_query = filter_query or {}
        cursor = db[self.collection_name].find(filter_query).skip(skip).limit(limit)
        results = await cursor.to_list(length=limit)
        return [self.model(**doc) for doc in results]

    async def create(
        self,
        db: AsyncIOMotorDatabase,
        *,
        obj_in: CreateSchemaType
    ) -> ModelType:
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        if "_id" not in obj_in_data and "id" in obj_in_data:
            obj_in_data["_id"] = obj_in_data.pop("id")
        result = await db[self.collection_name].insert_one(obj_in_data)
        doc = await db[self.collection_name].find_one({"_id": result.inserted_id})
        return self.model(**doc)

    async def update(
        self,
        db: AsyncIOMotorDatabase,
        *,
        id: str,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Optional[ModelType]:
        if not ObjectId.is_valid(id):
            return None
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        if update_data:
            update_result = await db[self.collection_name].update_one(
                {"_id": ObjectId(id)},
                {"$set": update_data}
            )
            if update_result.modified_count:
                return await self.get(db=db, id=id)
        return None

    async def delete(self, db: AsyncIOMotorDatabase, *, id: str) -> bool:
        if not ObjectId.is_valid(id):
            return False
        delete_result = await db[self.collection_name].delete_one({"_id": ObjectId(id)})
        return delete_result.deleted_count > 0

    async def count(
        self,
        db: AsyncIOMotorDatabase,
        *,
        filter_query: Dict = None
    ) -> int:
        filter_query = filter_query or {}
        return await db[self.collection_name].count_documents(filter_query) 