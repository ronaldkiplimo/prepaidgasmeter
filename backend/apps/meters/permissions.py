from rest_framework import permissions


class IsAdminToCreate(permissions.BasePermission):
    """
    Permission that allows only admin (staff) users to create Meter instances.

    Other actions are allowed for authenticated users and object-level
    access is governed by the view's queryset.
    """

    def has_permission(self, request, view):
        # Treat POST/create as the action that requires admin privileges.
        is_create_action = request.method == "POST" or getattr(view, "action", None) == "create"
        if is_create_action:
            return bool(request.user and request.user.is_authenticated and request.user.is_staff)
        return True
