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
        self.admin = User.objects.create_user(
            username="adminuser",
            phone_number="254722222222",
            password="testpass123",
            role=User.Role.ADMIN,
        )
        self.other_user = User.objects.create_user(
            username="newtenant",
            phone_number="254733333333",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def test_customer_cannot_add_meter(self):
        response = self.client.post(
            "/api/v1/meters/",
            {"meter_number": "12345678", "nickname": "Home"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Meter.objects.filter(user=self.user).count(), 0)

    def test_admin_can_add_meter_for_user(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            "/api/v1/meters/",
            {"user": str(self.user.id), "meter_number": "12345678", "nickname": "Home"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Meter.objects.filter(user=self.user).count(), 1)
        self.assertEqual(str(response.data["user"]), str(self.user.id))

    def test_admin_must_select_user_when_adding_meter(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            "/api/v1/meters/",
            {"meter_number": "12345678", "nickname": "Home"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("user", response.data)

    def test_admin_can_reassign_meter_to_another_user(self):
        meter = Meter.objects.create(user=self.user, meter_number="87654321", nickname="Apartment")
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f"/api/v1/meters/{meter.id}/",
            {"user": str(self.other_user.id)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        meter.refresh_from_db()
        self.assertEqual(meter.user, self.other_user)
        self.assertEqual(meter.phone_number, self.other_user.phone_number)

    def test_cannot_create_duplicate_meter_number(self):
        self.client.force_authenticate(user=self.admin)
        # Admin creates a meter for self.user
        response1 = self.client.post(
            "/api/v1/meters/",
            {"user": str(self.user.id), "meter_number": "12345678", "nickname": "Home"},
            format="json",
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Admin attempts to create the same meter number for another user
        response2 = self.client.post(
            "/api/v1/meters/",
            {"user": str(self.other_user.id), "meter_number": "12345678", "nickname": "Other"},
            format="json",
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("meter_number", response2.data)

    def test_customer_cannot_reassign_meter(self):
        meter = Meter.objects.create(user=self.user, meter_number="87654321", nickname="Apartment")
        response = self.client.patch(
            f"/api/v1/meters/{meter.id}/",
            {"user": str(self.other_user.id)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        meter.refresh_from_db()
        self.assertEqual(meter.user, self.user)

    def test_list_meters(self):
        Meter.objects.create(user=self.user, meter_number="87654321", nickname="Office")
        Meter.objects.create(user=self.other_user, meter_number="99999999", nickname="Other")
        response = self.client.get("/api/v1/meters/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("results", response.data) if isinstance(response.data, dict) else response.data
        meter_numbers = {meter["meter_number"] for meter in data}
        self.assertEqual(meter_numbers, {"87654321"})

    def test_customer_cannot_retrieve_other_users_meter(self):
        meter = Meter.objects.create(user=self.other_user, meter_number="99999999", nickname="Other")
        response = self.client.get(f"/api/v1/meters/{meter.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_retrieve_any_active_meter(self):
        meter = Meter.objects.create(user=self.other_user, meter_number="99999999", nickname="Other")
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f"/api/v1/meters/{meter.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
