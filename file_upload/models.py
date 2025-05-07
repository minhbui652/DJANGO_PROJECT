from django.db import models
from user.models import User

class UploadedFile(models.Model):
    filename = models.CharField(max_length=1000)
    content_type = models.CharField(max_length=255)
    data = models.BinaryField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.filename

