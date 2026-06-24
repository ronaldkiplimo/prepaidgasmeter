from django.urls import path

from .views import AdminUserDetailView, AdminUserListView, LoginView, LogoutView, ProfileView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("admin/users/", AdminUserListView.as_view(), name="admin-user-list"),
    path("admin/users/<uuid:pk>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
]
