from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

USER_CREATE_URL = reverse("users:create")
TOKEN_OBTAIN_URL = reverse("users:token_obtain_pair")
ME_URL = reverse("users:manage")


class UserApiTests(APITestCase):
    """
    Testing user management functionality (registration, tokens, profile)
    """

    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "Ivan",
            "last_name": "Ivanov",
        }

    def test_create_user_success(self):
        """Verification of successful new user registration"""
        response = self.client.post(USER_CREATE_URL, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=self.user_data["email"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertEqual(user.first_name, self.user_data["first_name"])
        # The password must not be returned in the response.
        self.assertNotIn(
            "password", response.data
        )

    def test_user_with_email_exists_error(self):
        """
        Verifying that registration with an existing email is not possible
        """
        get_user_model().objects.create_user(**self.user_data)
        response = self.client.post(USER_CREATE_URL, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Password length validation check (minimum 5 characters)"""
        payload = self.user_data.copy()
        payload["password"] = "123"
        response = self.client.post(USER_CREATE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_success(self):
        """Verification of JWT token retrieval with valid credentials"""
        get_user_model().objects.create_user(**self.user_data)
        payload = {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        }
        response = self.client.post(TOKEN_OBTAIN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_create_token_invalid_credentials_fails(self):
        """
        Verification of token retrieval error with an incorrect password
        """
        get_user_model().objects.create_user(**self.user_data)
        payload = {
            "email": self.user_data["email"],
            "password": "wrongpassword"
        }
        response = self.client.post(TOKEN_OBTAIN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_profile_success(self):
        """
        Verification of profile data retrieval by an authorized user
        """
        user = get_user_model().objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)

        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user_data["email"])
        self.assertEqual(
            response.data["first_name"], self.user_data["first_name"]
        )

    def test_update_profile_success(self):
        """Testing partial profile data update (PATCH)"""
        user = get_user_model().objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)

        payload = {"first_name": "NewName", "password": "newpassword123"}
        response = self.client.patch(ME_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.first_name, "NewName")
        self.assertTrue(user.check_password("newpassword123"))

    def test_auth_required_for_me_endpoint(self):
        """
        Verify that an unauthorized user cannot access /me/
        """
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
