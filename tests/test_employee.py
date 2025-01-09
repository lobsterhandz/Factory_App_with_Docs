import unittest
from unittest.mock import patch
from app import app
from services.employee_service import EmployeeService


class TestEmployeeEndpoints(unittest.TestCase):
    def setUp(self):
        """Set up the test client and headers."""
        self.client = app.test_client()
        self.headers = {"Authorization": "Bearer testtoken"}  # Mocked token for role validation

    @patch("services.employee_service.EmployeeService.get_all_employees")
    def test_get_all_employees_success(self, mock_get_all_employees):
        """Test fetching all employees successfully."""
        # Mock return value
        mock_get_all_employees.return_value = [
            {"id": 1, "name": "John Doe", "position": "Manager"},
            {"id": 2, "name": "Jane Smith", "position": "Supervisor"},
        ]
        # Perform GET request
        response = self.client.get("/employees", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)
        self.assertIn("John Doe", response.get_data(as_text=True))

    @patch("services.employee_service.EmployeeService.get_all_employees")
    def test_get_all_employees_empty(self, mock_get_all_employees):
        """Test fetching all employees when the list is empty."""
        mock_get_all_employees.return_value = []
        response = self.client.get("/employees", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 0)  # Expecting an empty list

    @patch("services.employee_service.EmployeeService.get_employee_by_id")
    def test_get_employee_success(self, mock_get_employee_by_id):
        """Test fetching an employee by ID successfully."""
        # Mock return value
        mock_get_employee_by_id.return_value = {
            "id": 1,
            "name": "John Doe",
            "position": "Manager",
        }
        # Perform GET request
        response = self.client.get("/employees/1", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("John Doe", response.get_data(as_text=True))

    @patch("services.employee_service.EmployeeService.get_employee_by_id")
    def test_get_employee_not_found(self, mock_get_employee_by_id):
        """Test fetching an employee by ID when the employee does not exist."""
        # Mock side effect to simulate not found
        mock_get_employee_by_id.side_effect = ValueError("Employee not found.")
        # Perform GET request
        response = self.client.get("/employees/999", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("Employee not found", response.get_data(as_text=True))

    @patch("services.employee_service.EmployeeService.create_employee")
    def test_create_employee_success(self, mock_create_employee):
        """Test creating a new employee successfully."""
        # Mock return value
        mock_create_employee.return_value = {
            "id": 3,
            "name": "Alice Johnson",
            "position": "Engineer",
            "email": "alice.johnson@email.com",
        }
        # Perform POST request
        response = self.client.post(
            "/employees",
            json={
                "name": "Alice Johnson",
                "position": "Engineer",
                "email": "alice.johnson@email.com",
                "phone": "555-1234",
            },
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 201)
        self.assertIn("Alice Johnson", response.get_data(as_text=True))

    @patch("services.employee_service.EmployeeService.create_employee")
    def test_create_employee_missing_fields(self, mock_create_employee):
        """Test creating an employee with missing required fields."""
        # Mock side effect to simulate validation error
        mock_create_employee.side_effect = ValueError("Missing required fields.")
        # Perform POST request
        response = self.client.post(
            "/employees",
            json={"name": "Alice Johnson"},
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required fields", response.get_data(as_text=True))

    @patch("services.employee_service.EmployeeService.update_employee")
    def test_update_employee_success(self, mock_update_employee):
        """Test updating an employee successfully."""
        # Mock return value
        mock_update_employee.return_value = {
            "id": 1,
            "name": "John Doe Updated",
            "position": "Senior Manager",
        }
        # Perform PUT request
        response = self.client.put(
            "/employees/1",
            json={
                "name": "John Doe Updated",
                "position": "Senior Manager",
            },
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("John Doe Updated", response.get_data(as_text=True))

    @patch("services.employee_service.EmployeeService.update_employee")
    def test_update_employee_not_found(self, mock_update_employee):
        """Test updating an employee when the employee does not exist."""
        # Mock side effect to simulate not found
        mock_update_employee.side_effect = ValueError("Employee not found.")
        # Perform PUT request
        response = self.client.put(
            "/employees/999",
            json={
                "name": "Nonexistent Employee",
                "position": "Senior Engineer",
            },
            headers=self.headers,
        )
        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("Employee not found", response.get_data(as_text=True))

    @patch("services.employee_service.EmployeeService.delete_employee")
    def test_delete_employee_success(self, mock_delete_employee):
        """Test deleting an employee successfully."""
        # Mock return value
        mock_delete_employee.return_value = True
        # Perform DELETE request
        response = self.client.delete("/employees/1", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("Employee deleted successfully", response.get_data(as_text=True))

    @patch("services.employee_service.EmployeeService.delete_employee")
    def test_delete_employee_not_found(self, mock_delete_employee):
        """Test deleting an employee when the employee does not exist."""
        # Mock side effect to simulate not found
        mock_delete_employee.side_effect = ValueError("Employee not found.")
        # Perform DELETE request
        response = self.client.delete("/employees/999", headers=self.headers)
        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("Employee not found", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
