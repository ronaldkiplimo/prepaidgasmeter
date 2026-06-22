from rest_framework import permissions


class HasRole(permissions.BasePermission):
    """Allow access only to users with one of the specified roles."""

    def __init__(self, *roles):
        self.roles = roles

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.role in self.roles


class IsCustomer(HasRole):
    def __init__(self):
        super().__init__("customer")


class IsLandlord(HasRole):
    def __init__(self):
        super().__init__("landlord")


class IsDistributor(HasRole):
    def __init__(self):
        super().__init__("distributor")


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.role == "admin")
        )


class IsLandlordOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ("landlord", "admin") or request.user.is_superuser


class IsAdminOrDistributor(permissions.BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and (u.is_superuser or u.role in ("admin", "distributor")))


class IsAdminOrLandlordOrDistributor(permissions.BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(
            u and u.is_authenticated
            and (u.is_superuser or u.role in ("admin", "distributor", "landlord"))
        )
