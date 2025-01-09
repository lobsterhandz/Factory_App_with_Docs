# Factory Management System

## Project Overview

This Flask-based Factory Management System provides an API to manage employees, products, orders, customers, and production records in a factory setting. Additionally, it supports **advanced analytics** for analyzing employee performance, customer lifetime value, and production efficiency. Built with Flask, SQLAlchemy, Flask-Migrate, and Flask-Limiter, it ensures scalability, database migrations, and API rate-limiting.

---

## Features

- **Employee Management:** CRUD operations to manage employees.
- **Product Management:** CRUD operations to manage products.
- **Order Management:** CRUD operations to manage orders.
- **Customer Management:** CRUD operations to manage customers.
- **Production Management:** CRUD operations to manage production records.
- **Advanced Analytics:** SQLAlchemy-powered queries for performance tracking and business insights.
- **Rate Limiting:** Prevents abuse with defined API limits.
- **Database Migrations:** Tracks schema changes using Alembic and Flask-Migrate.
- **Error Logging:** Logs errors and server activities using RotatingFileHandler.
- **JWT Security:** Implements token-based authentication and authorization with role-based access control.
- **Multi-Level Admin Roles:** Supports 'super_admin', 'admin', and 'user' roles for scalability and secure access.

---

## Tech Stack

- **Backend:** Flask (Python)
- **Database:** MySQL with SQLAlchemy ORM
- **API Testing:** Postman
- **Rate Limiting:** Flask-Limiter
- **Migrations:** Flask-Migrate
- **Authentication:** PyJWT

---

## Folder Structure

```
factory_management/
├── blueprints/                      # Blueprints for modular route management
│   ├── employee_blueprint.py
│   ├── product_blueprint.py
│   ├── order_blueprint.py
│   ├── customer_blueprint.py
│   ├── production_blueprint.py
│   ├── analytics_blueprint.py       # Analytics API routes for reporting and insights
│   ├── user_blueprint.py            # User routes for 
├── migrations/                      # Database migration files
├── models/                          # Database models
│   ├── __init__.py                  # Initializes database models
│   ├── employee.py
│   ├── product.py
│   ├── order.py
│   ├── customer.py
│   ├── production.py
│   ├── user.py                      # User model for authentication
├── schemas/                         # Schemas for data validation and serialization
│   ├── __init__.py
│   ├── customer_schema.py
│   ├── employee_schema.py
│   ├── order_schema.py
│   ├── product_schema.py
│   ├── production_schema.py
│   ├── user_schema.py               # User schema for validation
├── services/                        # Business logic for API endpoints
│   ├── __init__.py
│   ├── customer_service.py
│   ├── employee_service.py
│   ├── order_service.py
│   ├── product_service.py
│   ├── production_service.py
│   ├── user_service.py              # User-specific service layer
├── queries/                         # Advanced SQLAlchemy queries
│   ├── __init__.py
│   ├── analytic_queries.py          # Complex queries for analytics
├── logs/ # Logs generated for debugging and monitoring
│   ├── factory_management.log
├── Tests/ 
│   ├── __init__.py                # Marks the folder as a Python package
│   ├── mock_data.json             # Centralized mock data for testing
│   ├── mock_data.py               # Script to load and preprocess mock data
│   ├── seed_test_data.py          # Script for seeding mock data into the database
│   ├── test_auth.py               # Tests for authentication endpoints
│   ├── test_user.py               # Tests for user management endpoints
│   ├── test_employee.py           # Tests for employee management endpoints
│   ├── test_product.py            # Tests for product management endpoints
│   ├── test_order.py              # Tests for order management endpoints
│   ├── test_customer.py           # Tests for customer management endpoints
│   ├── test_production.py         # Tests for production management endpoints
│   ├── test_analytics.py          # Tests for analytics and reporting endpoints
│   ├── test_utils.py              # Tests for utility functions (e.g., JWT, error responses)
├── config.py                         # Configuration settings
├── limiter.py                        # Rate limiter setup
├── requirements.txt                  # Required Python packages
├── README.md                         # Project documentation
├── app.py                            # Main application entry point
├── utils.py                          # Utility functions (JWT Token Generation)
├── install.txt                       # Instructions for installation
├── test_data.py                      # Script to seed test ├── test_auth.py

---

## Assignment Requirements and Tasks

### Task 1: Define User Model
- Create a User model to represent users of the factory management system.
- Attributes:
  - `id`: Integer, primary key.
  - `username`: Unique username.
  - `password`: Hashed password.
  - `role`: String ('super_admin', 'admin', or 'user').
- Implement relationships and methods for database interactions.

### Task 2: Implement JWT Token Generation
- Add `pyjwt` to `requirements.txt`.
- Create `utils.py` to handle token creation and validation.
- Define a secret key for signing tokens.
- Implement a function `encode_token(user_id)` to generate tokens with expiration.

### Task 3: Authentication Logic
- Create a login function to authenticate users.
- Generate JWT tokens using `encode_token`.
- Return the token with a success message.

### Task 4: Role-Based Access Control
- Add `@role_required` decorator to validate admin and user roles.
- Restrict access to sensitive endpoints based on user roles.
- Ensure **super_admin** can create or manage other admin accounts, while **admin** can only manage non-admin users.
- Test endpoints to ensure proper authorization enforcement.

---

## Route and Role Mapping

| Endpoint                          | HTTP Method | Role Required   | Description                                      |
|------------------------------------|-------------|------------------|--------------------------------------------------|
| `/auth/register`                   | POST        | super_admin      | Register new users, including admins.            |
| `/auth/login`                      | POST        | none             | Authenticate users and generate JWT tokens.      |
| `/auth/<id>`                       | GET, PUT, DELETE | super_admin   | View, edit, or delete specific users.            |
| `/employees`                       | GET, POST   | admin            | Manage employee records.                         |
| `/employees/<id>`                  | GET, PUT, DELETE | admin         | View, edit, or delete specific employee records. |
| `/products`                        | GET, POST   | admin            | Manage product records.                          |
| `/products/<id>`                   | GET, PUT, DELETE | admin         | View, edit, or delete specific product records.  |
| `/orders`                          | GET, POST   | admin, user      | Manage order records.                            |
| `/orders/<id>`                     | GET, PUT, DELETE | admin         | View, edit, or delete specific order records.    |
| `/customers`                       | GET, POST   | admin            | Manage customer records.                         |
| `/customers/<id>`                  | GET, PUT, DELETE | admin         | View, edit, or delete specific customer records. |
| `/production`                      | GET, POST   | admin            | Manage production records.                       |
| `/analytics/employee-performance`  | GET         | admin            | Analyze employee performance metrics.            |
| `/analytics/top-products`          | GET         | admin            | Identify top-selling products.                   |
| `/analytics/customer-ltv`          | GET         | admin            | Analyze customer lifetime value.                 |
| `/analytics/production-efficiency` | GET         | admin            | Analyze production efficiency metrics.           |

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any suggestions or bug fixes.
