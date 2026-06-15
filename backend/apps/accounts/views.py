from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema

from apps.audit.services import log_audit
from .tokens import PhoneTokenObtainPairSerializer
from .serializers import ProfileUpdateSerializer, RegisterSerializer, UserSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(tags=["Authentication"], summary="Register a new user")
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            user = User.objects.get(phone_number=request.data.get("phone_number"))
            refresh = RefreshToken.for_user(user)
            log_audit(
                user=user,
                action="USER_REGISTERED",
                resource_type="User",
                resource_id=str(user.id),
                ip_address=self._get_ip(request),
            )
            response.data = {
                "user": UserSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            }
        return response

    def _get_ip(self, request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


class LoginView(TokenObtainPairView):
    serializer_class = PhoneTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(tags=["Authentication"], summary="Login with phone number and password")
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            phone = request.data.get("phone_number") or request.data.get("username")
            try:
                user = User.objects.get(phone_number=phone)
                log_audit(
                    user=user,
                    action="USER_LOGIN",
                    resource_type="User",
                    resource_id=str(user.id),
                    ip_address=self._get_ip(request),
                )
                response.data["user"] = UserSerializer(user).data
            except User.DoesNotExist:
                pass
        return response

    def _get_ip(self, request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return ProfileUpdateSerializer
        return UserSerializer

    @extend_schema(tags=["Authentication"], summary="Get or update user profile")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class LogoutView(APIView):
    @extend_schema(tags=["Authentication"], summary="Logout and blacklist refresh token")
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            log_audit(
                user=request.user,
                action="USER_LOGOUT",
                resource_type="User",
                resource_id=str(request.user.id),
                ip_address=self._get_ip(request),
            )
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

    def _get_ip(self, request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
