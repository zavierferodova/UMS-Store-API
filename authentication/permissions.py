from rest_framework import permissions

class IsAdminGroup(permissions.BasePermission):
    """Allows access only to users in the 'admin' group."""

    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='admin').exists()

class IsProcurementGroup(permissions.BasePermission):
    """Allows access only to users in the 'procurement' group."""

    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='procurement').exists()

class IsCashierGroup(permissions.BasePermission):
    """Allows access only to users in the 'cashier' group."""

    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='cashier').exists()
