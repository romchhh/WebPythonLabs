from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import User, UserCreate
from .base import CRUDBase
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class CRUDUser(CRUDBase[User, UserCreate, User]):
    async def get_by_email(
        self,
        db: AsyncIOMotorDatabase,
        *,
        email: str
    ) -> Optional[User]:
        doc = await db[self.collection_name].find_one({"email": email})
        if doc:
            return User(**doc)
        return None

    async def create(
        self,
        db: AsyncIOMotorDatabase,
        *,
        obj_in: UserCreate
    ) -> User:
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=pwd_context.hash(obj_in.password),
            is_admin=obj_in.is_admin
        )
        return await super().create(db, obj_in=db_obj)

    async def authenticate(
        self,
        db: AsyncIOMotorDatabase,
        *,
        email: str,
        password: str
    ) -> Optional[User]:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not pwd_context.verify(password, user.hashed_password):
            return None
        return user

    async def is_admin(
        self,
        db: AsyncIOMotorDatabase,
        user_id: str
    ) -> bool:
        user = await self.get(db, id=user_id)
        if not user:
            return False
        return user.is_admin

user = CRUDUser(User, "users")