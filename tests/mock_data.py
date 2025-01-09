import json
from models import db, User, Employee, Product, Customer, Order, Production
from werkzeug.security import generate_password_hash
from datetime import datetime

def load_mock_data():
    """Load mock data from mock_data.json."""
    with open('tests/mock_data.json') as f:
        return json.load(f)

def get_mock_users():
    """Return mock users data to be used for seeding."""
    return [
        {
            "username": "superadmin",
            "password": "superadminpassword",
            "role": "super_admin",
            "is_active": True
        },
        {
            "username": "adminuser",
            "password": "adminpassword",
            "role": "admin",
            "is_active": True
        },
        {
            "username": "regularuser",
            "password": "userpassword",
            "role": "user",
            "is_active": True
        }
    ]

def seed_test_data():
    """
    Seeds the database with mock data, clearing all existing data beforehand.
    """
    try:
        # Clear all existing data to avoid conflicts
        clear_test_data()

        # Load mock data
        mock_data = load_mock_data()

        # Seed Users (Ensure valid fields)
        users = [User(**user) for user in get_mock_users()]
        for user in users:
            user.set_password(user.password)  # Hash the passwords
        db.session.add_all(users)

        # Seed Employees (Ensure valid fields are passed)
        employees = [Employee(**{k: v for k, v in e.items() if k in Employee.__table__.columns}) for e in mock_data.get("employees", [])]
        db.session.add_all(employees)

        # Seed other models (Products, Customers, Orders, etc.)
        products = [Product(**p) for p in mock_data.get("products", [])]
        db.session.add_all(products)

        customers = [Customer(**c) for c in mock_data.get("customers", [])]
        db.session.add_all(customers)

        orders = [Order(**o) for o in mock_data.get("orders", [])]
        db.session.add_all(orders)

        production = [Production(**p) for p in mock_data.get("productions", [])]
        db.session.add_all(production)

        # Commit all changes
        db.session.commit()
        print("Test data seeded successfully!")

    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Error seeding data: {e}")

def clear_test_data():
    """
    Clears all existing data from the database.
    """
    try:
        # Clear all data in the correct order to handle foreign key constraints
        db.session.query(Order).delete()
        db.session.query(Production).delete()
        db.session.query(Customer).delete()
        db.session.query(Employee).delete()
        db.session.query(Product).delete()
        db.session.query(User).delete()
        db.session.commit()
        print("Test data cleared successfully!")
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Error clearing data: {e}")

def verify_test_data():
    """
    Verifies if the database is seeded with the mock data.
    """
    try:
        # Perform simple checks to verify seeded data
        if User.query.count() == 0:
            raise AssertionError("No users found in the database!")
        if Employee.query.count() == 0:
            raise AssertionError("No employees found in the database!")
        if Product.query.count() == 0:
            raise AssertionError("No products found in the database!")
        if Customer.query.count() == 0:
            raise AssertionError("No customers found in the database!")
        if Order.query.count() == 0:
            raise AssertionError("No orders found in the database!")
        if Production.query.count() == 0:
            raise AssertionError("No production records found in the database!")
        print("Test data verified successfully!")
    except AssertionError as e:
        raise RuntimeError(f"Verification failed: {e}")
    except Exception as e:
        raise RuntimeError(f"Error verifying data: {e}")

def reset_test_data():
    """
    Resets the database by clearing and re-seeding the test data.
    """
    try:
        clear_test_data()
        seed_test_data()
        verify_test_data()
        print("Test data reset successfully!")
    except Exception as e:
        raise RuntimeError(f"Error resetting test data: {e}")
