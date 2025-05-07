from rest_framework import serializers
from .models import UploadedFile

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['id', 'filename', 'content_type', 'data', 'uploaded_at', 'user']

class FileUploadDto(serializers.Serializer):
    file = serializers.FileField(required=True)