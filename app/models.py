from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema

class MongoBaseModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

class UserBase(MongoBaseModel):
    email: EmailStr
    username: str
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class User(UserBase):
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProductBase(MongoBaseModel):
    name: str
    description: str
    price: float
    stock: int
    category: Optional[str] = None
    image_url: Optional[str] = None
    tags: List[str] = []

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class OrderItemBase(MongoBaseModel):
    product_id: PyObjectId
    quantity: int
    price: float  # Ціна на момент замовлення
    product_name: str  # Назва продукту на момент замовлення

class OrderBase(MongoBaseModel):
    user_id: PyObjectId
    status: str = "new"  # new, processing, shipped, completed, cancelled
    total_amount: float
    shipping_address: Optional[dict] = None
    payment_info: Optional[dict] = None

class OrderCreate(OrderBase):
    items: List[OrderItemBase]

class Order(OrderBase):
    items: List[OrderItemBase]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Додаткові моделі для розширеної функціональності
class Category(MongoBaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[PyObjectId] = None
    image_url: Optional[str] = None

class Review(MongoBaseModel):
    product_id: PyObjectId
    user_id: PyObjectId
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CartItem(MongoBaseModel):
    product_id: PyObjectId
    quantity: int
    added_at: datetime = Field(default_factory=datetime.utcnow)

class Cart(MongoBaseModel):
    user_id: PyObjectId
    items: List[CartItem] = []
    last_modified: datetime = Field(default_factory=datetime.utcnow) 