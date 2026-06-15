from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from apps.meters.models import Meter

User = get_user_model()


class MeterAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="meteruser",
            phone_number="254711111111",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def test_add_meter(self):
        response = self.client.post(
            "/api/v1/meters/",
            {"meter_number": "12345678", "nickname": "Home"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Meter.objects.filter(user=self.user).count(), 1)

    def test_list_meters(self):
        Meter.objects.create(user=self.user, meter_number="87654321", nickname="Office")
        response = self.client.get("/api/v1/meters/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
