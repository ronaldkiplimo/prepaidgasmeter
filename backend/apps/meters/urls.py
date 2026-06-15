from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MeterViewSet

router = DefaultRouter()
router.register("", MeterViewSet, basename="meter")

urlpatterns = [
    path("", include(router.urls)),
]
