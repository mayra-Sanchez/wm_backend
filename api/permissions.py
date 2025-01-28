from rest_framework import permissions

class ProductoPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Permitir solo a los administradores
        if request.user.rol == 'admin':
            return True
        return False
