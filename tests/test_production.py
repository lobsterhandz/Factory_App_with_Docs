import unittest
from unittest.mock import patch
from app import app
from services.production_service import ProductionService


class TestProductionEndpoints(unittest.TestCase):
    def setUp(self):
        """Set up the test client and headers."""
        self.client = app.test_client()
        self.headers = {"Authorization": "Bearer testtoken"}  # Mock token for authentication

    @patch("services.production_service.ProductionService.get_all_productions")
    def test_get_all_productions_success(self, mock_get_all_productions):
        """Test fetching all production records successfully."""
        # Mock return value
        mock_get_all_productions.return_value = [
            {"id": 1, "product_id": 1, "quantity_produced": 50, "date_produced": "2025-01-01"},
            {"id": 2, "product_id": 2, "quantity_produced": 30, "date_produced": "2025-01-02"},
        ]
        # Perform GET request
        response = self.client.get("/production", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)
        self.assertIn("quantity_produced", response.get_data(as_text=True))

    @patch("services.production_service.ProductionService.get_all_productions")
    def test_get_all_productions_empty(self, mock_get_all_productions):
        """Test fetching all production records when the list is empty."""
        mock_get_all_productions.return_value = []
        response = self.client.get("/production", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 0)  # Expecting an empty list

    @patch("services.production_service.ProductionService.get_production_by_id")
    def test_get_production_success(self, mock_get_production_by_id):
        """Test fetching a production record by ID successfully."""
        # Mock return value
        mock_get_production_by_id.return_value = {
            "id": 1,
            "product_id": 1,
            "quantity_produced": 50,
            "date_produced": "2025-01-01",
        }
        # Perform GET request
        response = self.client.get("/production/1", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("quantity_produced", response.get_data(as_text=True))

    @patch("services.production_service.ProductionService.get_production_by_id")
    def test_get_production_not_found(self, mock_get_production_by_id):
        """Test fetching a production record when the record does not exist."""
        # Mock side effect to simulate not found
        mock_get_production_by_id.side_effect = ValueError("Production record not found.")
        # Perform GET request
        response = self.client.get("/production/999", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("Production record not found", response.get_data(as_text=True))

    @patch("services.production_service.ProductionService.create_production")
    def test_create_production_success(self, mock_create_production):
        """Test creating a new production record successfully."""
        # Mock return value
        mock_create_production.return_value = {
            "id": 3,
            "product_id": 1,
            "quantity_produced": 100,
            "date_produced": "2025-01-03",
        }
        # Perform POST request
        response = self.client.post(
            "/production",
            json={
                "product_id": 1,
                "quantity_produced": 100,
                "date_produced": "2025-01-03",
            },
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 201)
        self.assertIn("quantity_produced", response.get_data(as_text=True))

    @patch("services.production_service.ProductionService.create_production")
    def test_create_production_invalid_data(self, mock_create_production):
        """Test creating a production record with invalid data."""
        # Mock side effect to simulate validation error
        mock_create_production.side_effect = ValueError("Invalid production data.")
        # Perform POST request
        response = self.client.post(
            "/production",
            json={"quantity_produced": -10},  # Invalid data
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid production data", response.get_data(as_text=True))

    @patch("services.production_service.ProductionService.update_production")
    def test_update_production_success(self, mock_update_production):
        """Test updating a production record successfully."""
        # Mock return value
        mock_update_production.return_value = {
            "id": 1,
            "product_id": 1,
            "quantity_produced": 120,
            "date_produced": "2025-01-04",
        }
        # Perform PUT request
        response = self.client.put(
            "/production/1",
            json={
                "quantity_produced": 120,
                "date_produced": "2025-01-04",
            },
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("quantity_produced", response.get_data(as_text=True))

    @patch("services.production_service.ProductionService.update_production")
    def test_update_production_not_found(self, mock_update_production):
        """Test updating a production record that does not exist."""
        # Mock side effect to simulate not found
        mock_update_production.side_effect = ValueError("Production record not found.")
        # Perform PUT request
        response = self.client.put(
            "/production/999",
            json={"quantity_produced": 150},
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("Production record not found", response.get_data(as_text=True))

    @patch("services.production_service.ProductionService.delete_production")
    def test_delete_production_success(self, mock_delete_production):
        """Test deleting a production record successfully."""
        # Mock return value
        mock_delete_production.return_value = True
        # Perform DELETE request
        response = self.client.delete("/production/1", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("Production record deleted successfully", response.get_data(as_text=True))

    @patch("services.production_service.ProductionService.delete_production")
    def test_delete_production_not_found(self, mock_delete_production):
        """Test deleting a production record when the record does not exist."""
        # Mock side effect to simulate not found
        mock_delete_production.side_effect = ValueError("Production record not found.")
        # Perform DELETE request
        response = self.client.delete("/production/999", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("Production record not found", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
