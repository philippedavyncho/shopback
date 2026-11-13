from django.urls import reverse
from rest_framework.test import APITestCase

class AccountApiTests(APITestCase):
    def test_register_and_obtain_jwt(self):
        response = self.client.post("/api/v1/auth/register/", {
            "email": "client@example.test", "username": "client", "password": "long-safe-password-123",
        }, format="json")
        self.assertEqual(response.status_code, 201)
        token = self.client.post("/api/v1/auth/token/", {
            "email": "client@example.test", "password": "long-safe-password-123",
        }, format="json")
        self.assertEqual(token.status_code, 200)
        self.assertIn("access", token.data)
