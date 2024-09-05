from django.utils import timezone
from djoser.views import TokenCreateView
from rest_framework import viewsets, status, serializers, generics, permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import HttpResponse, Http404, JsonResponse
from django.views import View
from django.conf import settings
import logging
import os

from .permissions import IsOwnerOrReadOnly, IsStaffUser
from .models import File
from .serializers import UserSerializer, FileSerializer, CustomTokenCreateSerializer, TokenResponseSerializer
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all() # Добавляем атрибут queryset
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return File.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            return response
        except ValueError as e:
            logger.error(f"Error in list view: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        try:
            file = self.request.FILES['storage_path']
            logger.debug(f"File received: {file.name}, size: {file.size}")
            instance = serializer.save(
                user=self.request.user,
                original_name=file.name,
                size=file.size,
                storage_path=file
            )
        except Exception as e:
            raise serializers.ValidationError({'error': str(e)})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        file_path = instance.storage_path.path
        self.perform_destroy(instance)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOwnerOrReadOnly])
    def rename(self, request, pk=None):
        file_instance = self.get_object()
        new_name = request.data.get('new_name')

        if not new_name:
            return Response({'error': 'New name is required'}, status=status.HTTP_400_BAD_REQUEST)

        old_path = file_instance.storage_path.path
        new_path = os.path.join(os.path.dirname(old_path), new_name)

        try:
            os.rename(old_path, new_path)
            file_instance.storage_path.name = os.path.relpath(new_path, settings.MEDIA_ROOT)
            file_instance.original_name = new_name
            file_instance.save()
            return Response({'status': 'File renamed successfully'})
        except Exception as e:
            logger.error(f"Error renaming file: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOwnerOrReadOnly])
    def share(self, request, pk=None):
        file = self.get_object()
        file.generate_share_link()
        return Response({'download_link': file.download_link}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOwnerOrReadOnly])
    def revoke(self, request, pk=None):
        file = self.get_object()
        file.revoke_share_link()
        return Response({'message': 'Доступ к файлу закрыт'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsStaffUser])
    def user_files(self, request):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        files = File.objects.filter(user=user)
        serializer = self.get_serializer(files, many=True)
        return Response(serializer.data)

class FileDownloadView(View):
    def get(self, request, share_token):
        try:
            file = File.objects.get(share_token=share_token, is_shared=True)
            file.last_download_date = timezone.now()
            file.save()

            serializer = FileSerializer(file, context={'request': request})
            return JsonResponse(serializer.data, safe=False)
        except File.DoesNotExist:
            raise Http404("Файл не найден или доступ Вам запрещен")

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsStaffUser, IsAuthenticated]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return response

    def get_permissions(self):
        if self.action in ['create']:
            return []
        elif self.action in ['destroy']:
            return [IsAdminUser()]
        elif self.action in ['me']:
            return [IsAuthenticated()]
        return [IsStaffUser()]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

class CustomTokenCreateView(TokenCreateView):
    serializer_class = CustomTokenCreateSerializer

    def _action(self, serializer):
        token_data = serializer.save()
        response_serializer = TokenResponseSerializer(token_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
