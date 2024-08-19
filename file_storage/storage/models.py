from django.contrib.auth.models import User
from django.db import models
import os
from file_storage.settings import SITE_URL
from django.utils.crypto import get_random_string

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
    is_shared = models.BooleanField(default=False)
    share_token = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return self.original_name

    def generate_share_link(self):
        self.share_token = get_random_string(32)
        self.download_link = f"{SITE_URL}files/download/{self.share_token}/"
        self.is_shared = True
        self.save()

    def revoke_share_link(self):
        self.share_token = None
        self.download_link = None
        self.is_shared = False
        self.save()
