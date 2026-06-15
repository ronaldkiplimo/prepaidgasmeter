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
