import unittest
from unittest.mock import patch
from app import app
from services.product_service import ProductService


class TestProductEndpoints(unittest.TestCase):
    def setUp(self):
        """Set up the test client and headers."""
        self.client = app.test_client()
        self.headers = {"Authorization": "Bearer testtoken"}  # Mocked token for authentication

    @patch("services.product_service.ProductService.get_all_products")
    def test_get_all_products_success(self, mock_get_all_products):
        """Test fetching all products successfully."""
        # Mock return value
        mock_get_all_products.return_value = [
            {"id": 1, "name": "Widget A", "price": 19.99},
            {"id": 2, "name": "Widget B", "price": 29.99},
        ]
        # Perform GET request
        response = self.client.get("/products", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)
        self.assertIn("Widget A", response.get_data(as_text=True))

    @patch("services.product_service.ProductService.get_all_products")
    def test_get_all_products_empty(self, mock_get_all_products):
        """Test fetching all products when the list is empty."""
        mock_get_all_products.return_value = []
        response = self.client.get("/products", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 0)  # Expecting an empty list

    @patch("services.product_service.ProductService.get_product_by_id")
    def test_get_product_success(self, mock_get_product_by_id):
        """Test fetching a product by ID successfully."""
        # Mock return value
        mock_get_product_by_id.return_value = {"id": 1, "name": "Widget A", "price": 19.99}
        # Perform GET request
        response = self.client.get("/products/1", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("Widget A", response.get_data(as_text=True))

    @patch("services.product_service.ProductService.get_product_by_id")
    def test_get_product_not_found(self, mock_get_product_by_id):
        """Test fetching a product when the product does not exist."""
        # Mock side effect to simulate not found
        mock_get_product_by_id.side_effect = ValueError("Product not found.")
        # Perform GET request
        response = self.client.get("/products/999", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("Product not found", response.get_data(as_text=True))

    @patch("services.product_service.ProductService.create_product")
    def test_create_product_success(self, mock_create_product):
        """Test creating a new product successfully."""
        # Mock return value
        mock_create_product.return_value = {"id": 3, "name": "Widget C", "price": 39.99}
        # Perform POST request
        response = self.client.post(
            "/products",
            json={"name": "Widget C", "price": 39.99},
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 201)
        self.assertIn("Widget C", response.get_data(as_text=True))

    @patch("services.product_service.ProductService.create_product")
    def test_create_product_invalid_data(self, mock_create_product):
        """Test creating a product with invalid data."""
        # Mock side effect to simulate validation error
        mock_create_product.side_effect = ValueError("Invalid product data.")
        # Perform POST request
        response = self.client.post(
            "/products",
            json={"name": ""},  # Invalid data
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid product data", response.get_data(as_text=True))

    @patch("services.product_service.ProductService.update_product")
    def test_update_product_success(self, mock_update_product):
        """Test updating a product successfully."""
        # Mock return value
        mock_update_product.return_value = {"id": 1, "name": "Widget A+", "price": 24.99}
        # Perform PUT request
        response = self.client.put(
            "/products/1",
            json={"name": "Widget A+", "price": 24.99},
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("Widget A+", response.get_data(as_text=True))

    @patch("services.product_service.ProductService.update_product")
    def test_update_product_not_found(self, mock_update_product):
        """Test updating a product when the product does not exist."""
        # Mock side effect to simulate not found
        mock_update_product.side_effect = ValueError("Product not found.")
        # Perform PUT request
        response = self.client.put(
            "/products/999",
            json={"name": "Nonexistent Widget", "price": 49.99},
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("Product not found", response.get_data(as_text=True))

    @patch("services.product_service.ProductService.delete_product")
    def test_delete_product_success(self, mock_delete_product):
        """Test deleting a product successfully."""
        # Mock return value
        mock_delete_product.return_value = True
        # Perform DELETE request
        response = self.client.delete("/products/1", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("Product deleted successfully", response.get_data(as_text=True))

    @patch("services.product_service.ProductService.delete_product")
    def test_delete_product_not_found(self, mock_delete_product):
        """Test deleting a product when the product does not exist."""
        # Mock side effect to simulate not found
        mock_delete_product.side_effect = ValueError("Product not found.")
        # Perform DELETE request
        response = self.client.delete("/products/999", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("Product not found", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
