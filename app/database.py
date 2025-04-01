import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

# Завантажуємо змінні середовища
load_dotenv()

# MongoDB налаштування
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB", "shop_db")

# Асинхронний клієнт
async def get_async_db():
    client = AsyncIOMotorClient(MONGODB_URL)
    try:
        yield client[DB_NAME]
    finally:
        client.close()

# Синхронний клієнт (для утиліт та адмін-операцій)
def get_sync_db():
    client = MongoClient(MONGODB_URL)
    try:
        return client[DB_NAME]
    finally:
        client.close()

# Індекси для колекцій
async def create_indexes():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
    # Користувачі
    await db.users.create_index("email", unique=True)
    await db.users.create_index("username")
    
    # Продукти
    await db.products.create_index("name")
    await db.products.create_index([("name", "text"), ("description", "text")])
    
    # Замовлення
    await db.orders.create_index("user_id")
    await db.orders.create_index("created_at")
    
    client.close()