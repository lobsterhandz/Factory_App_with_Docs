import unittest
from unittest.mock import patch
from utils.utils import encode_token, decode_token, error_response
from app import create_app


class TestUtils(unittest.TestCase):
    def setUp(self):
        """Set up for utility tests."""
        self.app = create_app()  # Create the app instance
        self.app_context = self.app.app_context()  # Create app context
        self.app_context.push()  # Push the app context to Flask's context stack

        self.user_id = 1
        self.role = "admin"
        self.invalid_token = "invalid.token.string"

    def tearDown(self):
        """Tear down the app context after tests."""
        self.app_context.pop()  # Pop the app context after the test

    def test_encode_token_success(self):
        """Test encoding a JWT token successfully."""
        token = encode_token(self.user_id, self.role)
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 0)

    def test_decode_token_success(self):
        """Test decoding a valid JWT token successfully."""
        token = encode_token(self.user_id, self.role)
        decoded = decode_token(token)
        self.assertEqual(decoded["user_id"], self.user_id)
        self.assertEqual(decoded["role"], self.role)

    def test_decode_token_invalid(self):
        """Test decoding an invalid JWT token."""
        with self.assertRaises(Exception):  # Replace Exception with your custom exception if applicable
            decode_token(self.invalid_token)

    @patch("utils.utils.decode_token")
    def test_decode_token_expired(self, mock_decode_token):
        """Test decoding an expired JWT token."""
        mock_decode_token.side_effect = Exception("Token has expired.")
        with self.assertRaises(Exception) as context:
            decode_token("expired.token")
        self.assertEqual(str(context.exception), "Token has expired.")

    def test_error_response_default_status(self):
        """Test generating an error response with the default status."""
        response = error_response("Default error")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "Default error"})

    def test_error_response_custom_status(self):
        """Test generating an error response with a custom status code."""
        response = error_response("Unauthorized access", 401)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"error": "Unauthorized access"})

    def test_error_response_empty_message(self):
        """Test generating an error response with an empty error message."""
        response = error_response("")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "Bad Request"})  # Assuming default behavior for empty message

    def test_error_response_invalid_status_code(self):
        """Test generating an error response with an invalid status code."""
        response = error_response("Invalid status code test", 999)
        self.assertEqual(response.status_code, 999)
        self.assertEqual(response.get_json(), {"error": "Invalid status code test"})


if __name__ == "__main__":
    unittest.main()
