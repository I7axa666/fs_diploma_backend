from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user == obj.user

class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff