from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from .models import File
from .models import UserProfile
from django.contrib.auth.models import User
from rest_framework import serializers
import logging

from djoser.serializers import TokenCreateSerializer

logger = logging.getLogger(__name__)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['file_count', 'total_file_size']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile', 'is_staff']
        read_only_fields = ['id', 'username', 'email']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not hasattr(instance, 'userprofile'):
            representation['profile'] = {
                'file_count': 0,
                'total_file_size': 0
            }
        return representation

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


class CustomTokenCreateSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        if (username or email) and password:
            user = None
            if email:
                user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user and username:
                user = authenticate(request=self.context.get('request'), username=username, password=password)

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include either "username" or "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        self.user = user
        return attrs

    def create(self, validated_data):
        token, created = Token.objects.get_or_create(user=self.user)
        return {'auth_token': token.key, 'user_name': self.user.username}

class TokenResponseSerializer(serializers.Serializer):
    auth_token = serializers.CharField()
    user_name = serializers.CharField()