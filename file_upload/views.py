from django.shortcuts import render
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg import openapi
from .models import UploadedFile
from .serializer import FileUploadDto
import jwt
from django.conf import settings
from user.models import User

@swagger_auto_schema(
    method='post',
    request_body=FileUploadDto,
    operation_description='Upload a file (save as binary)',
    permission_classes=[IsAuthenticated],
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def upload_file(request):
    try:
        #decode access token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return HttpResponse("Authorization header is missing or invalid", status=401)
        access_token = auth_header.split(' ')[1]
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('id')
        if not user_id:
            return HttpResponse("User ID not found in token", status=401)
        user = User.objects.get(id=user_id)


        file_serializer = FileUploadDto(data=request.data)
        if file_serializer.is_valid():
            uploaded = request.FILES['file']

            UploadedFile.objects.create(
                filename=uploaded.name,
                content_type=uploaded.content_type,
                data=uploaded.read(),
                user=user
            )

            return HttpResponse("File uploaded successfully", status=200)
        else:
            return HttpResponse("File upload failed", status=400)
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}", status=500)

@swagger_auto_schema(
    method='get',
    operation_description='Download a file by ID',
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_file(request, file_id):
    try:
        uploaded_file = UploadedFile.objects.get(id=file_id)
        response = HttpResponse(uploaded_file.data, content_type=uploaded_file.content_type)
        response['Content-Disposition'] = f'attachment; filename={uploaded_file.filename}'
        return response
    except UploadedFile.DoesNotExist:
        return HttpResponse("File not found", status=404)
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}", status=500)

@swagger_auto_schema(
    method='get',
    operation_description='Get file path by ID',
)
@api_view(['GET'])
def get_file_path(request, file_id):
    try:
        uploaded_file = UploadedFile.objects.get(id=file_id)
        return HttpResponse(uploaded_file.data, content_type=uploaded_file.content_type)
    except UploadedFile.DoesNotExist:
        return None
    except Exception as e:
        return None
