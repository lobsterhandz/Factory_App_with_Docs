import unittest
from tests.mock_data import seed_test_data, verify_test_data, reset_test_data
from app import create_app
from models import User, Employee, Product

class TestMockData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Runs once before all tests. Sets up the app and seeds data.
        """
        cls.app = create_app()  # Create app instance
        cls.app_context = cls.app.app_context()
        cls.app_context.push()  # Activate app context
        seed_test_data()  # Seed mock data
        verify_test_data()  # Verify seeded data

    @classmethod
    def tearDownClass(cls):
        """
        Runs once after all tests. Resets the database.
        """
        reset_test_data()  # Reset database
        cls.app_context.pop()  # Pop app context

    def test_user_data(self):
        """
        Test if user data is seeded correctly.
        """
        user_count = User.query.count()
        self.assertGreater(user_count, 0, "No users found in the database!")

    def test_employee_data(self):
        """
        Test if employee data is seeded correctly.
        """
        employee_count = Employee.query.count()
        self.assertGreater(employee_count, 0, "No employees found in the database!")

    def test_product_data(self):
        """
        Test if product data is seeded correctly.
        """
        product_count = Product.query.count()
        self.assertGreater(product_count, 0, "No products found in the database!")


if __name__ == '__main__':
    unittest.main()
