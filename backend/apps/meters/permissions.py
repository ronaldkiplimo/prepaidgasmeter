from rest_framework import permissions


class IsAdminToCreate(permissions.BasePermission):
    """
    Permission that allows only admins to create Meter instances.

    Other actions are allowed for authenticated users and object-level
    access is governed by the view's queryset.
    """

    def has_permission(self, request, view):
        is_create_action = request.method == "POST" or getattr(view, "action", None) == "create"
        if is_create_action:
            user = request.user
            return bool(
                user
                and user.is_authenticated
                and (user.is_superuser or getattr(user, "role", None) == "admin")
            )
        return True
