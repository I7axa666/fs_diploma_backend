from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
import logging
import pdb; pdb.set_trace()

from .permissions import IsOwnerOrReadOnly
from .models import File
from .serializers import UserSerializer, FileSerializer
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)
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
        logger.debug("Entering perform_create")
        try:
            file = serializer.validated_data['storage_path']
            logger.debug(f"File received: {file.name}, size: {file.size}")
            serializer.save(
                user=self.request.user,
                original_name=file.name,
                size=file.size
            )
            logger.debug("File saved successfully")
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
