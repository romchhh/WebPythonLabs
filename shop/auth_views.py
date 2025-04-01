from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Реєстрація успішна!')
            return redirect('shop:product_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    # Тут можна додати логіку для отримання замовлень користувача
    orders = []  # Поки що пустий список
    return render(request, 'shop/profile.html', {'orders': orders})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Тут буде логіка оновлення профілю
        messages.success(request, 'Профіль оновлено!')
        return redirect('shop:profile')
    return render(request, 'shop/edit_profile.html') 