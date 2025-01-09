import unittest
from unittest.mock import patch
from app import create_app
from models import db
from utils.utils import encode_token, decode_token
from models.user import User


class TestAuthEndpoints(unittest.TestCase):
    def setUp(self):
        """Set up the test client and database."""
        self.app = create_app("config.TestingConfig")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            # Creating a mock user for testing
            self.test_user = User(username="test_user", role="admin")
            self.test_user.set_password("testpassword123")
            db.session.add(self.test_user)
            db.session.commit()

    def tearDown(self):
        """Clean up after tests."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    @patch("utils.utils.encode_token")
    def test_encode_decode_token_success(self, mock_encode_token):
        """Test encoding and decoding a token."""
        # Mock encoding to return a predictable token
        mock_encode_token.return_value = "mocked_token"
        
        token = encode_token(self.test_user.id, self.test_user.role)
        decoded = decode_token(token)
        
        # Assertions
        self.assertEqual(decoded["user_id"], self.test_user.id)
        self.assertEqual(decoded["role"], self.test_user.role)

    def test_encode_token_invalid(self):
        """Test encoding a token with invalid user data."""
        with self.assertRaises(ValueError):
            encode_token(None, None)  # Invalid user data should raise an error

    def test_decode_token_invalid(self):
        """Test decoding an invalid token."""
        with self.assertRaises(ValueError):
            decode_token("invalid_token")  # This should raise an error due to an invalid token

    def test_register_user_success(self):
        """Test the user registration endpoint."""
        new_user_data = {
            "username": "new_user",
            "password": "newpassword123",
            "role": "user"
        }
        response = self.client.post("/auth/register", json=new_user_data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("new_user", response.get_data(as_text=True))

    def test_register_user_invalid(self):
        """Test user registration with invalid data."""
        new_user_data = {
            "username": "",  # Empty username should trigger an error
            "password": "newpassword123",
            "role": "user"
        }
        response = self.client.post("/auth/register", json=new_user_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid username", response.get_data(as_text=True))

    @patch("utils.utils.decode_token")
    def test_login_success(self, mock_decode_token):
        """Test login with valid credentials."""
        mock_decode_token.return_value = {"user_id": self.test_user.id, "role": self.test_user.role}
        response = self.client.post(
            "/auth/login",
            json={"username": "test_user", "password": "testpassword123"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.get_json())

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post(
            "/auth/login",
            json={"username": "wrong_user", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid credentials", response.get_data(as_text=True))

    def test_get_user_success(self):
        """Test fetching a user's information."""
        token = encode_token(self.test_user.id, self.test_user.role)
        response = self.client.get(
            f"/auth/{self.test_user.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("test_user", response.get_data(as_text=True))

    def test_get_user_unauthorized(self):
        """Test fetching a user without authorization."""
        response = self.client.get(f"/auth/{self.test_user.id}")
        self.assertEqual(response.status_code, 401)
        self.assertIn("Authorization required", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
