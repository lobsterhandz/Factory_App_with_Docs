import unittest
from unittest.mock import patch
from app import app
from services.user_service import UserService


class TestUserEndpoints(unittest.TestCase):
    def setUp(self):
        """Set up the test client and headers."""
        self.client = app.test_client()
        self.headers = {"Authorization": "Bearer testtoken"}  # Mock token for authentication

    @patch("services.user_service.UserService.get_paginated_users")
    def test_get_all_users_success(self, mock_get_paginated_users):
        """Test fetching all users with pagination successfully."""
        # Mock return value
        mock_get_paginated_users.return_value = {
            "items": [
                {"id": 1, "username": "admin_user", "role": "super_admin"},
                {"id": 2, "username": "regular_user", "role": "user"},
            ],
            "total": 2,
            "pages": 1,
            "page": 1,
            "per_page": 10,
        }
        # Perform GET request
        response = self.client.get("/users", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()["users"]), 2)
        self.assertIn("admin_user", response.get_data(as_text=True))

    @patch("services.user_service.UserService.get_user_by_id")
    def test_get_user_success(self, mock_get_user_by_id):
        """Test fetching a user by ID successfully."""
        # Mock return value
        mock_get_user_by_id.return_value = {"id": 1, "username": "admin_user", "role": "super_admin"}
        # Perform GET request
        response = self.client.get("/users/1", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("admin_user", response.get_data(as_text=True))

    @patch("services.user_service.UserService.get_user_by_id")
    def test_get_user_not_found(self, mock_get_user_by_id):
        """Test fetching a user by ID when the user does not exist."""
        # Mock side effect to simulate not found
        mock_get_user_by_id.side_effect = ValueError("User not found.")
        # Perform GET request
        response = self.client.get("/users/999", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", response.get_data(as_text=True))

    @patch("services.user_service.UserService.create_user")
    def test_create_user_success(self, mock_create_user):
        """Test creating a new user successfully."""
        # Mock return value
        mock_create_user.return_value = {"id": 3, "username": "new_user", "role": "user"}
        # Perform POST request
        response = self.client.post(
            "/users",
            json={"username": "new_user", "password": "password123", "role": "user"},
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 201)
        self.assertIn("new_user", response.get_data(as_text=True))

    @patch("services.user_service.UserService.create_user")
    def test_create_user_duplicate_username(self, mock_create_user):
        """Test creating a user with a duplicate username."""
        # Mock side effect to simulate validation error
        mock_create_user.side_effect = ValueError("Username already exists.")
        # Perform POST request
        response = self.client.post(
            "/users",
            json={"username": "existing_user", "password": "password123", "role": "user"},
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn("Username already exists", response.get_data(as_text=True))

    @patch("services.user_service.UserService.update_user")
    def test_update_user_success(self, mock_update_user):
        """Test updating a user successfully."""
        # Mock return value
        mock_update_user.return_value = {"id": 1, "username": "updated_user", "role": "admin"}
        # Perform PUT request
        response = self.client.put(
            "/users/1",
            json={"password": "newpassword123", "role": "admin"},
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("updated_user", response.get_data(as_text=True))

    @patch("services.user_service.UserService.update_user")
    def test_update_user_not_found(self, mock_update_user):
        """Test updating a user that does not exist."""
        # Mock side effect to simulate not found
        mock_update_user.side_effect = ValueError("User not found.")
        # Perform PUT request
        response = self.client.put(
            "/users/999",
            json={"password": "newpassword123", "role": "user"},
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", response.get_data(as_text=True))

    @patch("services.user_service.UserService.delete_user")
    def test_delete_user_success(self, mock_delete_user):
        """Test deleting a user successfully."""
        # Mock return value
        mock_delete_user.return_value = True
        # Perform DELETE request
        response = self.client.delete("/users/1", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("User deleted successfully", response.get_data(as_text=True))

    @patch("services.user_service.UserService.delete_user")
    def test_delete_user_not_found(self, mock_delete_user):
        """Test deleting a user that does not exist."""
        # Mock side effect to simulate not found
        mock_delete_user.side_effect = ValueError("User not found.")
        # Perform DELETE request
        response = self.client.delete("/users/999", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
