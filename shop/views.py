from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Category, Product, Review, Cart, CartItem
from .forms import ReviewForm, CartAddProductForm

# Create your views here.

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    return render(request, 'shop/product/list.html',
                 {'category': category,
                  'categories': categories,
                  'products': products})

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    reviews = product.reviews.all()
    
    # Форма відгуку
    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Ваш відгук додано!')
            return redirect('shop:product_detail', id=id, slug=slug)
    else:
        form = ReviewForm()
    
    # Перевірка чи товар у обраному
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = request.user.favorite_products.filter(id=product.id).exists()
    
    context = {
        'product': product,
        'reviews': reviews,
        'form': form,
        'is_favorite': is_favorite
    }
    return render(request, 'shop/product/detail.html', context)

@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.favorites.filter(id=request.user.id).exists():
        product.favorites.remove(request.user)
        messages.success(request, f'{product.name} видалено з обраного')
    else:
        product.favorites.add(request.user)
        messages.success(request, f'{product.name} додано до обраного')
    return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))

@login_required
def favorite_products(request):
    products = request.user.favorite_products.all()
    return render(request, 'shop/product/favorites.html', {'products': products})

@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = CartAddProductForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            quantity = cd['quantity']
            
            # Перевіряємо наявність товару
            if product.stock < quantity:
                messages.error(request, 'Недостатньо товару на складі')
                return redirect('shop:product_detail', id=product.id, slug=product.slug)
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            messages.success(request, 'Товар додано до кошика')
            return redirect('shop:cart_detail')
    return redirect('shop:product_detail', id=product.id, slug=product.slug)

@login_required
def cart_remove(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    CartItem.objects.filter(cart=cart, product=product).delete()
    messages.success(request, 'Товар видалено з кошика')
    return redirect('shop:cart_detail')

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    total_price = cart.get_total_price()
    return render(request, 'shop/cart/detail.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@login_required
def cart_update(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > product.stock:
            messages.error(request, 'Недостатньо товару на складі')
            return redirect('shop:cart_detail')
            
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Кількість товару оновлено')
        else:
            cart_item.delete()
            messages.success(request, 'Товар видалено з кошика')
            
    return redirect('shop:cart_detail')
