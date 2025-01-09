Tests for Factory Management System
This folder contains all test scripts and supporting files for the Factory Management System. These tests validate the functionality and reliability of the system, covering both unit and integration scenarios using the unittest framework.

Folder Structure
bash
Copy code
tests/
├── __init__.py                # Marks the folder as a Python package
├── mock_data.json             # Centralized mock data for testing
├── mock_data.py               # Helper functions for loading and preprocessing mock data
├── test_auth.py               # Tests for authentication endpoints
├── test_user.py               # Tests for user management endpoints
├── test_employee.py           # Tests for employee management endpoints
├── test_product.py            # Tests for product management endpoints
├── test_order.py              # Tests for order management endpoints
├── test_customer.py           # Tests for customer management endpoints
├── test_production.py         # Tests for production management endpoints
├── test_analytics.py          # Tests for analytics and reporting endpoints
├── test_utils.py              # Tests for utility functions (e.g., JWT, error responses)
Purpose
The tests folder serves the following purposes:

Validate Functionality:
Ensure that API endpoints work as expected, covering normal operations and edge cases.
Prevent Regressions:
Automatically verify that new changes do not break existing functionality.
Isolate Components:
Use mocking to test individual components independently of the database.
Support Integration Testing:
Seed mock data dynamically to validate the full flow of application features.
Key Files
mock_data.json:

A centralized JSON file containing mock data for users, employees, products, customers, orders, and production records.
Provides consistent test data for all test cases.
mock_data.py:

Contains helper functions to load and preprocess data from mock_data.json.
Includes seed_test_data() to clear existing data and populate the database dynamically with mock data.
Setup
Before running the tests, follow these steps:

Install Dependencies: Ensure all required libraries are installed:

bash
Copy code
pip install -r requirements.txt
Set Up the Database: Create and configure the testing database in TestingConfig (e.g., SQLite or MySQL).

Seed Test Data: Test data is seeded dynamically via seed_test_data() from mock_data.py. This function clears existing data and populates the database with mock data from mock_data.json.

Running Tests
Run all tests in the tests folder:

bash
Copy code
python -m unittest discover tests
Run a specific test file:

bash
Copy code
python -m unittest tests/test_customer.py
Writing Tests
Basic Structure of a Test File
Import the necessary modules and classes:

python
Copy code
import unittest
from unittest.mock import patch
from app import app
Set up the test client and mock data in the setUp() method:

python
Copy code
class TestExample(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.headers = {"Authorization": "Bearer testtoken"}  # Mock token
Write test methods for each scenario:

python
Copy code
@patch("services.example_service.ExampleService.get_example")
def test_get_example(self, mock_get_example):
    mock_get_example.return_value = {"id": 1, "name": "Example"}
    response = self.client.get("/example", headers=self.headers)
    self.assertEqual(response.status_code, 200)
    self.assertIn("Example", response.get_data(as_text=True))
Tear down resources if necessary:

python
Copy code
def tearDown(self):
    pass
Contributing
Add new test files for additional features or endpoints.
Use mock_data.json for consistent data across all tests.
Run all tests before submitting changes to ensure nothing breaks.
This README.md ensures that new contributors or team members can easily understand and work with the tests folder. Let me know if you'd like to add anything else!