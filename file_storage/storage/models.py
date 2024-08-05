from django.contrib.auth.models import User
from django.db import models
import os

def user_directory_path(instance, filename):
    return f'user_{instance.user.id}/{filename}'

class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_name = models.CharField(max_length=255)
    size = models.PositiveIntegerField()
    upload_date = models.DateTimeField(auto_now_add=True)
    last_download_date = models.DateTimeField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    storage_path = models.FileField(upload_to=user_directory_path)
    download_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.original_name
