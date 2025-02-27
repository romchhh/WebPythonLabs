# Лабораторна робота: E-Commerce на FastAPI

## Хід виконання роботи

### 1. Перехід з SQLite на PostgreSQL
Встановлено PostgreSQL та необхідні пакети:
```bash
sudo apt-get install postgresql postgresql-contrib
pip install psycopg2-binary python-dotenv
```

### 2. Налаштування бази даних
Створено файл .env:
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=0333
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=fastapi_db
```

Оновлено конфігурацію database.py:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### 3. Оновлення функціоналу
Оновлено модель Product:
```python
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    stock = Column(Integer)
```

### 4. Технічні покращення
Налаштування статичних файлів:
```python
app.mount("/static", StaticFiles(directory="static"), name="static")
```


## Результати
- Успішний перехід на PostgreSQL
- Покращено дизайн та UX
- Забезпечено безпеку конфігураційних даних
- Додано адаптивність

## Висновок
В ході роботи було успішно модернізовано E-Commerce додаток: впроваджено PostgreSQL для кращої масштабованості, покращено безпеку через використання .env файлу та оновлено дизайн. Отримано практичний досвід роботи з FastAPI, PostgreSQL, Alembic та сучасними підходами до веб-розробки. Проект демонструє вдале поєднання технічних рішень та користувацького досвіду.
