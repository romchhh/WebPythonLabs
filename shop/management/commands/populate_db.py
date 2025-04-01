from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files import File
from shop.models import Category, Product
import random
import time
import os

class Command(BaseCommand):
    help = 'Наповнює базу даних тестовими даними'

    def handle(self, *args, **options):
        # Очищаємо існуючі дані
        self.stdout.write('Видалення існуючих даних...')
        Product.objects.all().delete()
        Category.objects.all().delete()

        # Категорії та їх описи
        categories_data = {
            'Ноутбуки': 'Широкий вибір ноутбуків від провідних виробників',
            'Смартфони': 'Сучасні смартфони з передовими технологіями',
            'Планшети': 'Планшети для роботи та розваг',
            'Навушники': 'Якісні навушники для чудового звучання',
            'Аксесуари': 'Корисні аксесуари для ваших гаджетів'
        }

        # Бренди для різних категорій
        brands = {
            'Ноутбуки': ['Apple', 'Dell', 'HP', 'Lenovo', 'Asus'],
            'Смартфони': ['Apple', 'Samsung', 'Xiaomi', 'OnePlus', 'Google'],
            'Планшети': ['Apple', 'Samsung', 'Lenovo', 'Huawei', 'Microsoft'],
            'Навушники': ['Apple', 'Sony', 'Bose', 'JBL', 'Sennheiser'],
            'Аксесуари': ['Anker', 'Belkin', 'Logitech', 'Samsung', 'Xiaomi']
        }

        # Створюємо категорії
        created_categories = []
        for category_name, description in categories_data.items():
            try:
                category = Category.objects.create(
                    name=category_name,
                    slug=slugify(category_name),
                    description=description
                )
                created_categories.append(category)
                self.stdout.write(f'Створено категорію: {category_name}')
            except Exception as e:
                self.stdout.write(f'Помилка при створенні категорії {category_name}: {str(e)}')
                continue

        # Створюємо продукти
        for category in created_categories:
            for i in range(10):
                try:
                    brand = random.choice(brands[category.name])
                    timestamp = int(time.time() * 1000) + i
                    product_name = f"{brand} {category.name[:-1]} {timestamp}"
                    
                    description = f"Високоякісний {category.name.lower()[:-1]} від {brand}. "
                    description += "Оснащений найновішими технологіями та функціями. "
                    description += "Ідеальний вибір для повсякденного використання."
                    
                    price = random.randint(5000, 50000)
                    stock = random.randint(0, 50)
                    rating = round(random.uniform(3.5, 5.0), 1)
                    
                    product = Product.objects.create(
                        category=category,
                        name=product_name,
                        slug=slugify(product_name),
                        description=description,
                        price=price,
                        stock=stock,
                        rating=rating,
                        num_reviews=random.randint(10, 100)
                    )
                    self.stdout.write(f'Створено продукт: {product_name}')
                except Exception as e:
                    self.stdout.write(f'Помилка при створенні продукту для категорії {category.name}: {str(e)}')
                    continue

        self.stdout.write(self.style.SUCCESS('База даних успішно наповнена тестовими даними!')) 