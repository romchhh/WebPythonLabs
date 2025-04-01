from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Category, Product, Review
from .forms import ReviewForm

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
