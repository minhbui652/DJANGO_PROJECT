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
from django.urls import path, include, re_path
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from user.views import UserViewSet, AuthViewSet
from product.views import ProductViewSet, CartViewSet, get_total_price, product_create, product_update, product_delete, product_get_all, product_get_by_id
from rest_framework import routers, permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="Demo API",
        default_version='v1',
        description="test swagger",
    ),
    public=True,
    permission_classes=[AllowAny],
    authentication_classes=[]
)

router = routers.DefaultRouter()
router.register('user', UserViewSet, basename='user')
router.register('product', ProductViewSet, basename='product')
router.register('cart', CartViewSet, basename='cart')
router.register('auth', AuthViewSet, basename='auth')

urlpatterns = [
    #swagger
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path('^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('admin/', admin.site.urls),
    #api user, product, cart using viewset
    path('api/', include(router.urls)),

    #api product, cart using api_view
    path('api/cart/total_price/<int:id>/', get_total_price, name='get_total_price'),
    path('api/FBV/product/create/', product_create, name='product_create'),
    path('api/FBV/product/update/', product_update, name='product_update'),
    path('api/FBV/product/delete/<int:id>/', product_delete, name='product_delete'),
    path('api/FBV/product/get_all', product_get_all, name='product_get_all'),
    path('api/FBV/product/get_by_id/<int:id>/', product_get_by_id, name='product_get_by_id'),

    #api authen
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
