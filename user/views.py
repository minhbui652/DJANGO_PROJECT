from asyncio import timeout
from django.db.models import Q
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from DemoDjango.settings import EMAIL_HOST_USER
from user.serializers import UserSerializer, LoginDto, SendMailDto, VerifyOtpDto
from user.models import User
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import action, api_view, permission_classes
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.cache import cache
from django.core.cache import caches
from django.core.mail import send_mail
import pyotp
from celery import shared_task
from smtplib import SMTPException

# Create your views here.
class AuthViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(method='post', request_body=LoginDto, permission_classes=[AllowAny])
    @action(detail=False, methods=['post'], url_path='login', permission_classes=[AllowAny])
    def login(self, request):
        user = User.objects.filter(username=request.data['username']).first()
        if user is None:
            return Response({'error': 'User not found'}, status=404)
        if not user.check_password(request.data['password']):
            return Response({'error': 'Password is incorrect'}, status=400)
        if not user.is_active:
            return Response({'error': 'User is inactive'}, status=400)

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        access_token['id'] = user.id
        access_token['first_name'] = user.first_name
        access_token['last_name'] = user.last_name

        return Response({
            'refresh': str(refresh),
            'access': str(access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
            }
        }, status=200)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='register', permission_classes=[AllowAny])
    def register(self, request, *args, **kwargs):
        user = User.objects.filter(
            Q(username=request.data['username']) | Q(email=request.data['email'])
        )
        if user.exists():
            return Response({'error': 'User already exists'}, status=400)
        data = request.data.copy()
        data['password'] = make_password(request.data['password'])
        serialize = UserSerializer(data=data, context={'request': request})
        if serialize.is_valid():
            serialize.save()
            generate_otp.delay(user_id=serialize.data['id'])
            return Response(serialize.data, status=201)
        return Response(serialize.errors, status=400)

    def list(self, request, *args, **kwargs):
        cache_key = "list_user_info"
        list_user = cache.get(cache_key)

        if list_user:
            print('get from cache done...')
            return Response(list_user, status=200)
        else:
            print('Cache miss, fetching from database...')
            users = User.objects.all()
            result = [
                {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                }
                for user in users
            ]
            cache.set(cache_key, list(result), timeout=300)
            return Response(result, status=200)

    #trùng register()
    def create(self, request, *args, **kwargs):
        return Response({'error': 'Method not allowed'}, status=405)

    def update(self, request, *args, **kwargs):
        user = User.objects.get(id=kwargs['pk'])
        if user is None:
            return Response({'error': 'User not found'}, status=404)
        if User.objects.filter(email=request.data['email']).exists() and user.email != request.data['email']:
            return Response({'error': 'Email already exists'}, status=400)
        if User.objects.filter(username=request.data['username']).exists() and user.username != request.data['username']:
            return Response({'error': 'Username already exists'}, status=400)
        user.email = request.data['email']
        user.first_name = request.data['first_name']
        user.last_name = request.data['last_name']
        user.is_active = request.data['is_active']
        user.is_staff = request.data['is_staff']
        user.save()
        cache_key = "list_user_info"
        if cache_key in cache:
            cache.delete(cache_key)
        return Response({'message': 'User updated successfully'}, status=200)

#email api test
@swagger_auto_schema(method='post', request_body=SendMailDto, permission_classes=[AllowAny])
@api_view(['POST'])
@permission_classes([AllowAny])
def send_email(request):
    try:
        subject = request.data['subject']
        message = request.data['message']
        receives = request.data['email']
        send_mail(subject,
            message,
            EMAIL_HOST_USER,
            receives,
            fail_silently=False
        )
        return Response({'message': 'Email sent successfully'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def resend_otp(request, *args, **kwargs):
    try:
        generate_otp.delay(user_id=kwargs['user_id'])
        return Response({'message': 'Resend OTP successfully'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@swagger_auto_schema(method='post', request_body=VerifyOtpDto, permission_classes=[AllowAny])
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    user = User.objects.get(id=request.data['user_id'])
    _cache = caches['default'].get(f'otp_{request.data['user_id']}')
    if not _cache:
        return Response({'error': 'OTP expired'}, status=400)
    elif _cache != request.data['otp']:
        return Response({'error': 'OTP is incorrect'}, status=400)
    else:
        caches['default'].delete(f'otp_{request.data['user_id']}')
        user.is_active = True
        user.save()
        welcome_email.delay(user_id=request.data['user_id'])
        return Response({'message': 'OTP is correct'}, status=200)

@shared_task
def generate_otp(user_id: int):
    try:
        user = User.objects.get(id=user_id)
        if not user:
            return {'error': 'User not found'}

        cache_key = f'otp_{user_id}'
        if caches['default'].get(cache_key):
            caches['default'].delete(cache_key)

        totp = pyotp.TOTP(pyotp.random_base32(), digits=6)
        otp = totp.now()
        caches['default'].set(cache_key, otp, timeout=60)

        try:
            send_mail(
                "OTP Verification",
                f"Mã xác thực OTP của bạn là {otp},\nMã có thời hạn 60 giây.\nVui lòng không chia sẻ mã này với bất kỳ ai.",
                EMAIL_HOST_USER,
                [user.email],
                fail_silently=False
            )
            print(f'OTP: {otp}')
            return {'status': 'OTP sent'}
        except SMTPException as e:
            print(f"SMTP error occurred: {str(e)}")
            return {'error': 'Failed to send OTP, invalid email address or SMTP issue'}

    except Exception as e:
        print(f'Error: {str(e)}')
        return {'error': str(e)}

@shared_task
def welcome_email(user_id:int):
    user = User.objects.get(id=user_id)
    if user is None:
        return Response({'error': 'User not found'}, status=404)
    send_mail(
        "Đăng ký tài khoản thành công",
        f'Chúc mừng {user.username} đã đăng ký thành công tài khoản trên hệ thống của chúng tôi. \nHy vọng bạn sẽ có thời gian vui vẻ khi trải nghiệm hệ thống!',
        EMAIL_HOST_USER,
        [user.email],
        fail_silently=False
    )
    return Response({'Sent welcome email success!'}, status=200)