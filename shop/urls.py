from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import auth_views as custom_auth_views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='shop:product_list'), name='logout'),
    path('accounts/register/', custom_auth_views.register, name='register'),
    path('accounts/profile/', custom_auth_views.profile, name='profile'),
    path('accounts/profile/edit/', custom_auth_views.edit_profile, name='edit_profile'),
    path('accounts/password-change/', 
         auth_views.PasswordChangeView.as_view(
             template_name='registration/change_password.html',
             success_url='/accounts/profile/'
         ),
         name='change_password'),
    path('category/<slug:category_slug>/', views.product_list, name='category_list'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('favorite/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorite_products, name='favorite_products'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
] 