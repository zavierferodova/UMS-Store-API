from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Allows access only to users with 'admin' role."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsProcurement(permissions.BasePermission):
    """Allows access only to users with 'procurement' role."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'procurement'


class IsCashier(permissions.BasePermission):
    """Allows access only to users with 'cashier' role."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'cashier'


class IsChecker(permissions.BasePermission):
    """Allows access only to users with 'checker' role."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'checker'
