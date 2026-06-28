from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username="testuser",
            phone_number="254712345678",
            password="testpass123",
        )
        self.assertEqual(user.phone_number, "254712345678")
        self.assertTrue(user.check_password("testpass123"))


class AuthAPITest(APITestCase):
    def test_register_and_login(self):
        register_data = {
            "username": "newuser",
            "email": "new@example.com",
            "phone_number": "254798765432",
            "password": "securepass123",
            "password_confirm": "securepass123",
            "first_name": "Test",
            "last_name": "User",
        }
        response = self.client.post("/api/v1/auth/register/", register_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)

        login_response = self.client.post(
            "/api/v1/auth/login/",
            {"phone_number": "254798765432", "password": "securepass123"},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_response.data)

    def test_register_normalizes_local_phone_number(self):
        register_data = {
            "username": "localuser",
            "email": "local@example.com",
            "phone_number": "0798765432",
            "password": "securepass123",
            "password_confirm": "securepass123",
            "first_name": "Local",
            "last_name": "User",
        }
        response = self.client.post("/api/v1/auth/register/", register_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["phone_number"], "254798765432")
        self.assertIn("tokens", response.data)

    def test_login_normalizes_plus_prefixed_phone_number_in_response_user_lookup(self):
        User.objects.create_user(
            username="plususer",
            email="plus@example.com",
            phone_number="254798765433",
            password="securepass123",
        )

        response = self.client.post(
            "/api/v1/auth/login/",
            {"phone_number": "+254798765433", "password": "securepass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["phone_number"], "254798765433")


class AdminUserAPITest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="adminuser",
            phone_number="254700000001",
            password="testpass123",
            role=User.Role.ADMIN,
        )
        self.user = User.objects.create_user(
            username="customer",
            phone_number="254700000002",
            password="testpass123",
        )

    def test_admin_can_deactivate_user(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f"/api/v1/auth/admin/users/{self.user.id}/",
            {"is_active": False},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_customer_cannot_deactivate_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f"/api/v1/auth/admin/users/{self.admin.id}/",
            {"is_active": False},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_admin_cannot_deactivate_self(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f"/api/v1/auth/admin/users/{self.admin.id}/",
            {"is_active": False},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)
