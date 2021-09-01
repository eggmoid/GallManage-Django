from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):

    def has_permission(self, request, view):
        if request.user.username == 'admin':
            return True
        return False
