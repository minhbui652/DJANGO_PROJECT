from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.permissions import AllowAny
from user.views import UserViewSet, AuthViewSet, send_email, resend_otp, verify_otp
from product.views import CartViewSet, get_total_price, product_create, product_update, product_delete, product_get_all, product_get_by_id
from user.view_permissions import (view_permissions, view_permissions_by_id, add_permission, delete_permission,
                                   view_group, view_group_by_user_id, add_group, update_group, delete_group)
from file_upload.views import upload_file, download_file, get_file_path
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

    #api permission
    path('api/permission/view_permissions/', view_permissions, name='view_permissions'),
    path('api/permission/view_permissions/<int:id>/', view_permissions_by_id, name='view_permissions_by_id'),
    path('api/permission/add_permission/', add_permission, name='add_permission'),
    path('api/permission/delete_permission/', delete_permission, name='delete_permission'),

    #api group
    path('api/group/view_groups/', view_group, name='view_groups'),
    path('api/group/view_groups/<int:id>/', view_group_by_user_id, name='view_groups_by_user_id'),
    path('api/group/add_group/', add_group, name='add_group'),
    path('api/group/update_group/', update_group, name='update_group'),
    path('api/group/delete_group/<int:id>/', delete_group, name='delete_group'),

    #api send mail
    path('api/mail/send_mail/', send_email, name='send_email'),

    #api generate otp
    path('api/otp/resend_otp/user_id=<int:user_id>', resend_otp, name='resend_otp'),
    path('api/otp/verify_otp/', verify_otp, name='verify_otp'),

    #api file upload
    path('api/file/upload_file/', upload_file, name='upload_file'),
    path('api/file/download_file/<int:file_id>/', download_file, name='download_file'),
    path('api/file/get_file_path/<int:file_id>/', get_file_path, name='get_file_path'),
]
