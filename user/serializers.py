from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer, TokenObtainPairSerializer

from user.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'is_active', 'is_staff', 'is_superuser']

class LoginDto(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)

class AddPermissionDto(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'permission_ids']

    id = serializers.IntegerField()
    permission_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

class DeletePermissionDto(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'permission_ids']

    id = serializers.IntegerField()
    permission_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

class AddGroupDto(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'permission_ids']

    name = serializers.CharField(max_length=150)
    permission_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

class UpdateGroupDto(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'permission_ids']

    id = serializers.IntegerField()
    name = serializers.CharField(max_length=150)
    permission_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

class SendMailDto(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'subject', 'message']

    email = serializers.ListField(child=serializers.EmailField(), write_only=True)
    subject = serializers.CharField(max_length=255)
    message = serializers.CharField(max_length=2000)

class VerifyOtpDto(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'otp']

    user_id = serializers.IntegerField()
    otp = serializers.CharField(max_length=6, write_only=True)