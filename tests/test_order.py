import unittest
from unittest.mock import patch
from app import app
from services.order_service import OrderService


class TestOrderEndpoints(unittest.TestCase):
    def setUp(self):
        """Set up the test client and headers."""
        self.client = app.test_client()
        self.headers = {"Authorization": "Bearer testtoken"}  # Mocked token for authentication

    @patch("services.order_service.OrderService.get_all_orders")
    def test_get_all_orders_success(self, mock_get_all_orders):
        """Test fetching all orders successfully."""
        # Mock return value
        mock_get_all_orders.return_value = [
            {
                "id": 1,
                "customer_id": 1,
                "product_id": 1,
                "quantity": 2,
                "total_price": 39.98,
            },
            {
                "id": 2,
                "customer_id": 2,
                "product_id": 2,
                "quantity": 1,
                "total_price": 29.99,
            },
        ]
        # Perform GET request
        response = self.client.get("/orders", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)
        self.assertIn("total_price", response.get_data(as_text=True))

    @patch("services.order_service.OrderService.get_all_orders")
    def test_get_all_orders_empty(self, mock_get_all_orders):
        """Test fetching all orders when the list is empty."""
        mock_get_all_orders.return_value = []
        response = self.client.get("/orders", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 0)  # Expecting an empty list

    @patch("services.order_service.OrderService.get_order_by_id")
    def test_get_order_success(self, mock_get_order_by_id):
        """Test fetching an order by ID successfully."""
        # Mock return value
        mock_get_order_by_id.return_value = {
            "id": 1,
            "customer_id": 1,
            "product_id": 1,
            "quantity": 2,
            "total_price": 39.98,
        }
        # Perform GET request
        response = self.client.get("/orders/1", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_price", response.get_data(as_text=True))

    @patch("services.order_service.OrderService.get_order_by_id")
    def test_get_order_not_found(self, mock_get_order_by_id):
        """Test fetching an order when the order does not exist."""
        # Mock side effect to simulate not found
        mock_get_order_by_id.side_effect = ValueError("Order not found.")
        # Perform GET request
        response = self.client.get("/orders/999", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("Order not found", response.get_data(as_text=True))

    @patch("services.order_service.OrderService.create_order")
    def test_create_order_success(self, mock_create_order):
        """Test creating a new order successfully."""
        # Mock return value
        mock_create_order.return_value = {
            "id": 3,
            "customer_id": 1,
            "product_id": 2,
            "quantity": 1,
            "total_price": 29.99,
        }
        # Perform POST request
        response = self.client.post(
            "/orders",
            json={
                "customer_id": 1,
                "product_id": 2,
                "quantity": 1,
                "total_price": 29.99,
            },
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 201)
        self.assertIn("total_price", response.get_data(as_text=True))

    @patch("services.order_service.OrderService.create_order")
    def test_create_order_invalid_data(self, mock_create_order):
        """Test creating an order with invalid data."""
        # Mock side effect to simulate validation error
        mock_create_order.side_effect = ValueError("Invalid order data.")
        # Perform POST request
        response = self.client.post(
            "/orders",
            json={
                "customer_id": 1,
                "product_id": 2,
                "quantity": 0,  # Invalid quantity
            },
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid order data", response.get_data(as_text=True))

    @patch("services.order_service.OrderService.update_order")
    def test_update_order_success(self, mock_update_order):
        """Test updating an order successfully."""
        # Mock return value
        mock_update_order.return_value = {
            "id": 1,
            "customer_id": 1,
            "product_id": 1,
            "quantity": 3,
            "total_price": 59.97,
        }
        # Perform PUT request
        response = self.client.put(
            "/orders/1",
            json={
                "quantity": 3,
                "total_price": 59.97,
            },
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_price", response.get_data(as_text=True))

    @patch("services.order_service.OrderService.delete_order")
    def test_delete_order_success(self, mock_delete_order):
        """Test deleting an order successfully."""
        # Mock return value
        mock_delete_order.return_value = True
        # Perform DELETE request
        response = self.client.delete("/orders/1", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("Order deleted successfully", response.get_data(as_text=True))

    @patch("services.order_service.OrderService.delete_order")
    def test_delete_order_not_found(self, mock_delete_order):
        """Test deleting an order when the order does not exist."""
        # Mock side effect to simulate not found
        mock_delete_order.side_effect = ValueError("Order not found.")
        # Perform DELETE request
        response = self.client.delete("/orders/999", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("Order not found", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
