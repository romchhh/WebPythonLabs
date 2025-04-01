# Лабораторна робота №5: Розробка інтернет-магазину з використанням Django

## Мета роботи
Розробка функціонального інтернет-магазину з використанням Django, реалізація CRUD операцій для роботи з кошиком користувача та управління товарами.

## Використані технології
- Python 3.x
- Django 5.1.7
- SQLite
- Bootstrap 5
- Font Awesome 6
- HTML/CSS
- JavaScript

## Структура проекту

### Models (моделі даних)
1. **Category** - модель для категорій товарів:
```python
class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/')
```

2. **Product** - модель для товарів:
```python
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    image = models.ImageField(upload_to='products/')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    rating = models.FloatField(default=0)
    num_reviews = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    favorites = models.ManyToManyField(User, related_name='favorite_products', blank=True)
```

3. **Cart** та **CartItem** - моделі для роботи з кошиком:
```python
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
```

### Forms (форми)
1. **CartAddProductForm** - форма для додавання товару в кошик:
```python
class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'value': 1,
                'min': 1,
                'step': 1
            }
        )
    )
```

### CRUD операції для кошика

1. **Create (Створення)**
```python
@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = CartAddProductForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            quantity = cd['quantity']
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
```

2. **Read (Читання)**
```python
@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    total_price = cart.get_total_price()
    return render(request, 'shop/cart/detail.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })
```

3. **Update (Оновлення)**
```python
@login_required
def cart_update(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        cart_item.quantity = quantity
        cart_item.save()
```

4. **Delete (Видалення)**
```python
@login_required
def cart_remove(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    CartItem.objects.filter(cart=cart, product=product).delete()
```

## Особливості реалізації

### Безпека
- Використання декоратора `@login_required` для захисту views
- CSRF захист для всіх форм
- Валідація даних на рівні форм та моделей

### Оптимізація
- Використання related_name для оптимізації запитів
- Кешування кількості товарів у кошику через контекстний процесор
- Оптимізовані запити до бази даних

### Користувацький інтерфейс
- Адаптивний дизайн з використанням Bootstrap 5
- Інтерактивні елементи (динамічна зміна кількості товарів)
- Зручна навігація та інформативні повідомлення
- Стильові покращення з використанням CSS змінних

## Висновок
В ході виконання лабораторної роботи було створено функціональний інтернет-магазин з використанням Django. Реалізовано повний набір CRUD операцій для роботи з кошиком користувача, що дозволяє:
- Додавати товари до кошика
- Переглядати вміст кошика
- Оновлювати кількість товарів
- Видаляти товари з кошика

Особлива увага була приділена розробці моделей та форм, що забезпечують надійне зберігання даних та зручну взаємодію з користувачем. Використання Django Forms дозволило реалізувати надійну валідацію даних та зручний інтерфейс для взаємодії з користувачем.

Проект демонструє практичне застосування принципів розробки веб-додатків з використанням Django, включаючи:
- Розробку моделей даних
- Створення форм
- Реалізацію CRUD операцій
- Розробку користувацького інтерфейсу
- Забезпечення безпеки додатку
