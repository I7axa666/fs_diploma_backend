from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from storage.permissions import IsOwnerOrReadOnly
from .models import File
from .serializers import UserSerializer, FileSerializer
from django.contrib.auth.models import User

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return []
        elif self.action in ['destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        file = serializer.validated_data['storage_path']
        serializer.save(
            user=self.request.user,
            original_name=file.name,
            size=file.size
        )
