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
def generate_otp(request, *args, **kwargs):
    user = User.objects.get(id=kwargs['user_id'])
    if user is None:
        return Response({'error': 'User not found'}, status=404)
    check_cache = caches['default'].get(f'otp_{kwargs['user_id']}')
    if check_cache:
        caches['default'].delete(f'otp_{kwargs['user_id']}')
    totp = pyotp.TOTP(pyotp.random_base32(), digits=6)
    otp = totp.now()
    caches['default'].set(f'otp_{kwargs['user_id']}', otp, timeout=60)
    return Response({'Sent otp success!'}, status=200)

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
        return Response({'message': 'OTP is correct'}, status=200)