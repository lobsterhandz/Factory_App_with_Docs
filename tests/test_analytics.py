import unittest
from unittest.mock import patch
from app import app


class TestAnalyticsEndpoints(unittest.TestCase):
    def setUp(self):
        """Set up the test client and headers."""
        self.client = app.test_client()
        self.headers = {"Authorization": "Bearer testtoken"}  # Mocked token for authentication

    @patch("services.analytics_service.AnalyticsService.get_employee_performance")
    def test_get_employee_performance_success(self, mock_get_employee_performance):
        """Test fetching employee performance analytics successfully."""
        # Mock return value
        mock_get_employee_performance.return_value = [
            {"employee_id": 1, "name": "John Doe", "tasks_completed": 50},
            {"employee_id": 2, "name": "Jane Smith", "tasks_completed": 30},
        ]
        # Perform GET request
        response = self.client.get("/analytics/employee-performance", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)
        self.assertIn("John Doe", response.get_data(as_text=True))

    @patch("services.analytics_service.AnalyticsService.get_employee_performance")
    def test_get_employee_performance_empty(self, mock_get_employee_performance):
        """Test fetching employee performance when no data is available."""
        mock_get_employee_performance.return_value = []
        response = self.client.get("/analytics/employee-performance", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 0)  # Expecting an empty list

    @patch("services.analytics_service.AnalyticsService.get_top_selling_products")
    def test_get_top_selling_products_success(self, mock_get_top_selling_products):
        """Test fetching top-selling products successfully."""
        # Mock return value
        mock_get_top_selling_products.return_value = [
            {"product_id": 1, "name": "Widget A", "units_sold": 200},
            {"product_id": 2, "name": "Widget B", "units_sold": 150},
        ]
        # Perform GET request
        response = self.client.get("/analytics/top-products", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)
        self.assertIn("Widget A", response.get_data(as_text=True))

    @patch("services.analytics_service.AnalyticsService.get_top_selling_products")
    def test_get_top_selling_products_empty(self, mock_get_top_selling_products):
        """Test fetching top-selling products when no data is available."""
        mock_get_top_selling_products.return_value = []
        response = self.client.get("/analytics/top-products", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 0)  # Expecting an empty list

    @patch("services.analytics_service.AnalyticsService.get_customer_lifetime_value")
    def test_get_customer_lifetime_value_success(self, mock_get_customer_lifetime_value):
        """Test fetching customer lifetime value analytics successfully."""
        # Mock return value
        mock_get_customer_lifetime_value.return_value = [
            {"customer_id": 1, "name": "Alice Johnson", "lifetime_value": 500.00},
            {"customer_id": 2, "name": "Bob Brown", "lifetime_value": 300.00},
        ]
        # Perform GET request
        response = self.client.get("/analytics/customer-ltv", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)
        self.assertIn("Alice Johnson", response.get_data(as_text=True))

    @patch("services.analytics_service.AnalyticsService.get_customer_lifetime_value")
    def test_get_customer_lifetime_value_empty(self, mock_get_customer_lifetime_value):
        """Test fetching customer lifetime value when no data is available."""
        mock_get_customer_lifetime_value.return_value = []
        response = self.client.get("/analytics/customer-ltv", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 0)  # Expecting an empty list

    @patch("services.analytics_service.AnalyticsService.get_production_efficiency")
    def test_get_production_efficiency_success(self, mock_get_production_efficiency):
        """Test fetching production efficiency analytics successfully."""
        # Mock return value
        mock_get_production_efficiency.return_value = {
            "total_units_produced": 500,
            "average_units_per_day": 50,
            "efficiency_percentage": 85.0,
        }
        # Perform GET request
        response = self.client.get("/analytics/production-efficiency", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("efficiency_percentage", response.get_data(as_text=True))

    @patch("services.analytics_service.AnalyticsService.get_production_efficiency")
    def test_get_production_efficiency_empty_data(self, mock_get_production_efficiency):
        """Test fetching production efficiency with no production data."""
        # Mock return value
        mock_get_production_efficiency.return_value = {
            "total_units_produced": 0,
            "average_units_per_day": 0,
            "efficiency_percentage": 0.0,
        }
        # Perform GET request
        response = self.client.get("/analytics/production-efficiency", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("efficiency_percentage", response.get_data(as_text=True))
        self.assertEqual(response.get_json()["efficiency_percentage"], 0.0)

    @patch("services.analytics_service.AnalyticsService.get_production_efficiency")
    def test_get_production_efficiency_error(self, mock_get_production_efficiency):
        """Test production efficiency analytics with service error."""
        mock_get_production_efficiency.side_effect = Exception("Database error")
        response = self.client.get("/analytics/production-efficiency", headers=self.headers)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Database error", response.get_data(as_text=True))

    @patch("services.analytics_service.AnalyticsService.get_production_efficiency")
    def test_get_production_efficiency_invalid_data(self, mock_get_production_efficiency):
        """Test production efficiency with invalid data format."""
        mock_get_production_efficiency.return_value = "Invalid data"
        response = self.client.get("/analytics/production-efficiency", headers=self.headers)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Invalid data", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
