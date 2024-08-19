from .models import File
from django.contrib.auth.models import User
from rest_framework import serializers
import logging

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = ['id', 'username', 'email', 'is_staff']
        # fields = '__all__'
        fields = ['id', 'is_staff', 'username', 'email']

class FileSerializer(serializers.ModelSerializer):
    storage_path = serializers.SerializerMethodField()
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
            'download_link',
            'is_shared'
        ]
        read_only_fields = [
            'user',
            'original_name',
            'size',
            'upload_date',
            'last_download_date',
            'download_link',
            'is_shared'
        ]

    def get_storage_path(self, obj):
        request = self.context.get('request')
        if obj.storage_path and hasattr(obj.storage_path, 'url'):
            if request:
                return request.build_absolute_uri(obj.storage_path.url)
            return obj.storage_path.url
        return None

    def validate_storage_path(self, value):
        logger.debug(f"Validating storage_path: {value}")
        return value

    def create(self, validated_data):
        logger.debug(f"Creating file with data: {validated_data}")
        return super().create(validated_data)
