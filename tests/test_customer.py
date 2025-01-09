import unittest
from unittest.mock import patch
from app import app
from services.customer_service import CustomerService


class TestCustomerEndpoints(unittest.TestCase):
    def setUp(self):
        """Set up the test client and headers."""
        self.client = app.test_client()
        self.headers = {"Authorization": "Bearer testtoken"}  # Mocked token for authentication

    @patch("services.customer_service.CustomerService.get_all_customers")
    def test_get_all_customers_success(self, mock_get_all_customers):
        """Test fetching all customers successfully."""
        # Mock return value
        mock_get_all_customers.return_value = [
            {"id": 1, "name": "Alice Johnson", "email": "alice.johnson@email.com", "phone": "555-4321"},
            {"id": 2, "name": "Bob Brown", "email": "bob.brown@email.com", "phone": "555-8765"},
        ]
        # Perform GET request
        response = self.client.get("/customers", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)
        self.assertIn("Alice Johnson", response.get_data(as_text=True))

    @patch("services.customer_service.CustomerService.get_all_customers")
    def test_get_all_customers_empty(self, mock_get_all_customers):
        """Test fetching all customers when the list is empty."""
        mock_get_all_customers.return_value = []
        response = self.client.get("/customers", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 0)  # Expecting an empty list

    @patch("services.customer_service.CustomerService.get_customer_by_id")
    def test_get_customer_success(self, mock_get_customer_by_id):
        """Test fetching a customer by ID successfully."""
        # Mock return value
        mock_get_customer_by_id.return_value = {
            "id": 1,
            "name": "Alice Johnson",
            "email": "alice.johnson@email.com",
            "phone": "555-4321",
        }
        # Perform GET request
        response = self.client.get("/customers/1", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("Alice Johnson", response.get_data(as_text=True))

    @patch("services.customer_service.CustomerService.get_customer_by_id")
    def test_get_customer_not_found(self, mock_get_customer_by_id):
        """Test fetching a customer when the customer does not exist."""
        # Mock side effect to simulate not found
        mock_get_customer_by_id.side_effect = ValueError("Customer not found.")
        # Perform GET request
        response = self.client.get("/customers/999", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("Customer not found", response.get_data(as_text=True))

    @patch("services.customer_service.CustomerService.create_customer")
    def test_create_customer_success(self, mock_create_customer):
        """Test creating a new customer successfully."""
        # Mock return value
        mock_create_customer.return_value = {
            "id": 3,
            "name": "Charlie Green",
            "email": "charlie.green@email.com",
            "phone": "555-6789",
        }
        # Perform POST request
        response = self.client.post(
            "/customers",
            json={
                "name": "Charlie Green",
                "email": "charlie.green@email.com",
                "phone": "555-6789",
            },
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 201)
        self.assertIn("Charlie Green", response.get_data(as_text=True))

    @patch("services.customer_service.CustomerService.create_customer")
    def test_create_customer_invalid_data(self, mock_create_customer):
        """Test creating a customer with invalid data."""
        # Mock side effect to simulate validation error
        mock_create_customer.side_effect = ValueError("Invalid customer data.")
        # Perform POST request
        response = self.client.post(
            "/customers",
            json={"name": "Charlie Green"},  # Missing email and phone
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid customer data", response.get_data(as_text=True))

    @patch("services.customer_service.CustomerService.update_customer")
    def test_update_customer_success(self, mock_update_customer):
        """Test updating a customer successfully."""
        # Mock return value
        mock_update_customer.return_value = {
            "id": 1,
            "name": "Alice Johnson Updated",
            "email": "alice.updated@email.com",
            "phone": "555-9999",
        }
        # Perform PUT request
        response = self.client.put(
            "/customers/1",
            json={
                "name": "Alice Johnson Updated",
                "email": "alice.updated@email.com",
                "phone": "555-9999",
            },
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("Alice Johnson Updated", response.get_data(as_text=True))

    @patch("services.customer_service.CustomerService.update_customer")
    def test_update_customer_not_found(self, mock_update_customer):
        """Test updating a customer when the customer does not exist."""
        # Mock side effect to simulate not found
        mock_update_customer.side_effect = ValueError("Customer not found.")
        # Perform PUT request
        response = self.client.put(
            "/customers/999",
            json={
                "name": "Nonexistent Customer",
                "email": "nonexistent@email.com",
                "phone": "555-8888",
            },
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("Customer not found", response.get_data(as_text=True))

    @patch("services.customer_service.CustomerService.delete_customer")
    def test_delete_customer_success(self, mock_delete_customer):
        """Test deleting a customer successfully."""
        # Mock return value
        mock_delete_customer.return_value = True
        # Perform DELETE request
        response = self.client.delete("/customers/1", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("Customer deleted successfully", response.get_data(as_text=True))

    @patch("services.customer_service.CustomerService.delete_customer")
    def test_delete_customer_not_found(self, mock_delete_customer):
        """Test deleting a customer when the customer does not exist."""
        # Mock side effect to simulate not found
        mock_delete_customer.side_effect = ValueError("Customer not found.")
        # Perform DELETE request
        response = self.client.delete("/customers/999", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("Customer not found", response.get_data(as_text=True))

if __name__ == "__main__":
    unittest.main()
