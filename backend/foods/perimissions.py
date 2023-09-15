from rest_framework import permissions

class Is_Author_Permission(permissions.BasePermission):
    def has_permission(self, request, view):
        return super().has_permission(request, view)


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS