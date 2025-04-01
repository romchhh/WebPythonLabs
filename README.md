# Лабораторна робота №4: Розробка E-commerce веб-додатку на Django

## Мета роботи
Розробити веб-додаток інтернет-магазину з використанням фреймворку Django, реалізувати основні функції e-commerce платформи та створити сучасний адаптивний інтерфейс.

## Використані технології та інструменти
- Python 3.11
- Django 4.2
- Bootstrap 5
- SQLite
- Pillow для обробки зображень
- HTML/CSS/JavaScript

## Хід роботи

### 1. Налаштування проекту

#### 1.1. Створення віртуального середовища та встановлення залежностей
```bash
# Створення віртуального середовища
python -m venv venv
source venv/bin/activate  # для Linux/Mac

# Встановлення необхідних пакетів
pip install django pillow
pip freeze > requirements.txt
```

#### 1.2. Створення проекту та додатку
```bash
# Створення проекту Django
django-admin startproject myshop
cd myshop

# Створення додатку shop
python manage.py startapp shop
```

#### 1.3. Налаштування settings.py
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shop.apps.ShopConfig',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

LOGIN_REDIRECT_URL = 'shop:product_list'
LOGOUT_REDIRECT_URL = 'shop:product_list'
```

### 2. Розробка моделей даних

#### 2.1. Створення моделей (models.py)
```python
class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/')

    def get_absolute_url(self):
        return reverse('shop:category_list', args=[self.slug])

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    available = models.BooleanField(default=True)
    rating = models.FloatField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])
```

### 3. Налаштування URL-маршрутизації

#### 3.1. Головний urls.py
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls', namespace='shop')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

#### 3.2. URLs додатку shop (shop/urls.py)
```python
from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='category_list'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register/', views.register, name='register'),
]
```

### 4. Розробка представлень (views.py)

#### 4.1. Представлення для списку продуктів
```python
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
        
    # Сортування
    sort = request.GET.get('sort', '')
    if sort == 'price-asc':
        products = products.order_by('price')
    elif sort == 'price-desc':
        products = products.order_by('-price')
    elif sort == 'rating':
        products = products.order_by('-rating')
        
    return render(request, 'shop/product/list.html',
                 {'category': category,
                  'categories': categories,
                  'products': products})
```

### 5. Розробка шаблонів

#### 5.1. Базовий шаблон (base.html)
```html
{% load static %}
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <!-- Навігаційне меню -->
    </nav>
    
    <main class="container mt-4">
        {% block content %}
        {% endblock %}
    </main>
    
    <footer class="footer mt-auto py-3 bg-dark">
        <!-- Футер -->
    </footer>
</body>
</html>
```

#### 5.2. Шаблон списку продуктів (list.html)
```html
{% extends "shop/base.html" %}
{% load static %}

{% block content %}
<div class="container">
    <!-- Фільтри та сортування -->
    <div class="row mb-4">
        <div class="col-md-8">
            <div class="dropdown me-3">
                <button class="btn btn-outline-primary dropdown-toggle">
                    Сортування
                </button>
                <ul class="dropdown-menu">
                    <li><a class="dropdown-item" href="?sort=price-asc">Ціна: від низької до високої</a></li>
                    <li><a class="dropdown-item" href="?sort=price-desc">Ціна: від високої до низької</a></li>
                    <li><a class="dropdown-item" href="?sort=rating">За рейтингом</a></li>
                </ul>
            </div>
        </div>
    </div>

    <!-- Список товарів -->
    <div class="row">
        {% for product in products %}
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <img src="{{ product.image.url }}" class="card-img-top" alt="{{ product.name }}">
                    <div class="card-body">
                        <h5 class="card-title">{{ product.name }}</h5>
                        <p class="card-text">{{ product.description|truncatewords:20 }}</p>
                        <p class="card-text"><strong>Ціна: </strong>${{ product.price }}</p>
                    </div>
                </div>
            </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
```

### 6. Наповнення бази даних

#### 6.1. Створення команди для наповнення даними (management/commands/populate_db.py)
```python
from django.core.management.base import BaseCommand
from shop.models import Category, Product
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        # Очищення існуючих даних
        Category.objects.all().delete()
        Product.objects.all().delete()

        # Створення категорій
        categories = [
            'Ноутбуки',
            'Смартфони',
            'Планшети',
            'Аксесуари',
            'Гаджети'
        ]

        for category_name in categories:
            category = Category.objects.create(
                name=category_name,
                slug=slugify(category_name)
            )
            
            # Створення продуктів для кожної категорії
            for i in range(10):
                Product.objects.create(
                    category=category,
                    name=f'{category_name} {i+1}',
                    slug=slugify(f'{category_name}-{i+1}'),
                    price=round(random.uniform(100, 1000), 2),
                    stock=random.randint(0, 100),
                    rating=round(random.uniform(0, 5), 1)
                )
```

## Результати роботи
1. Створено повноцінний e-commerce веб-додаток на Django
2. Реалізовано основні функції інтернет-магазину:
   - Каталог товарів з категоріями
   - Фільтрація та сортування товарів
   - Система аутентифікації користувачів
   - Адаптивний дизайн для різних пристроїв
3. Розроблено зручний користувацький інтерфейс
4. Реалізовано систему управління товарами через адмін-панель
5. Створено скрипт для автоматичного наповнення бази даних тестовими даними

## Висновок
В ході виконання лабораторної роботи було створено функціональний веб-додаток інтернет-магазину з використанням Django. Проект демонструє практичне застосування MVT архітектури та сучасних підходів до веб-розробки. Особлива увага була приділена структуруванню коду, створенню зручного користувацького інтерфейсу та реалізації основних функцій e-commerce платформи.

Набуті практичні навички:
- Розробка веб-додатків на Django
- Робота з системою шаблонів Django
- Налаштування URL-маршрутизації
- Створення моделей даних та міграцій
- Інтеграція фронтенд-фреймворків
- Реалізація користувацької аутентифікації
- Робота з статичними файлами та медіа
- Створення команд управління Django
