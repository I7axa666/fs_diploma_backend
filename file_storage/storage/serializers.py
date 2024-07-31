from .models import File
from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = [
            'id',
            'user',
            'original_name',
            'size',
            'upload_date',
            'last_download_date',
            'comment',
            'storage_path',
            'download_link'
        ]
        read_only_fields = ['user',]