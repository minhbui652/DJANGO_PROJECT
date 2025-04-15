"""
URL configuration for DemoDjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from user.views import UserViewSet
from product.views import ProductViewSet, CartViewSet, get_total_price, product_create, product_update, product_delete, product_get_all, product_get_by_id
from rest_framework import routers

router = routers.DefaultRouter()
router.register('user', UserViewSet, basename='user')
router.register('product', ProductViewSet, basename='product')
router.register('cart', CartViewSet, basename='cart')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/cart/total_price/<int:id>/', get_total_price, name='get_total_price'),
    path('api/FBV/product/create/', product_create, name='product_create'),
    path('api/FBV/product/update/', product_update, name='product_update'),
    path('api/FBV/product/delete/<int:id>/', product_delete, name='product_delete'),
    path('api/product/get_all', product_get_all, name='product_get_all'),
    path('api/product/get_by_id/<int:id>/', product_get_by_id, name='product_get_by_id')
]
