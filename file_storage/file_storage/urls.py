from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from storage.views import UserViewSet, FileViewSet, FileDownloadView, CustomTokenCreateView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'files', FileViewSet, basename='file') # Добавляем basename

# Основные URL-паттерны
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/me/', UserViewSet.as_view({'get': 'me'}), name='current-user'),
    path('api/', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/token/login/', CustomTokenCreateView.as_view(), name='login'),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('files/download/<str:share_token>/', FileDownloadView.as_view(), name='file-download'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
