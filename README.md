# Factory Management System

## Overview
The Factory Management System is a Flask-based API designed to streamline factory operations. It supports comprehensive management of employees, products, orders, customers, and production records. Additionally, the system includes analytics capabilities for tracking performance, customer behavior, and production efficiency. Security is ensured through JWT-based authentication and role-based access control.

---

## Key Features

### Comprehensive Management
- **Employees**: Add, update, delete, and retrieve employee records.
- **Products**: Manage factory products, including prices.
- **Orders**: Place and track orders with pagination and sorting.
- **Customers**: Handle customer details and lifetime value analysis.
- **Production**: Record and monitor production data.

### Analytics
- Employee performance metrics.
- Top-selling products analysis.
- Customer lifetime value insights.
- Production efficiency evaluations.

### Security
- **JWT Authentication**: Token-based access control.
- **Role-Based Access**: Restrict access to endpoints based on user roles (`super_admin`, `admin`, `user`).

### Performance Optimization
- **Caching**: Efficiently handle GET requests using Flask-Caching.
- **Rate Limiting**: Prevent abuse of endpoints using Flask-Limiter.

### Documentation
- **Interactive API Documentation**: Flasgger-powered Swagger UI for easy exploration and testing of APIs.

### Logging
- Track errors and server activities for debugging and monitoring.

---

## Tech Stack

- **Backend Framework**: Flask
- **Database**: MySQL (with SQLAlchemy ORM)
- **Authentication**: JWT (PyJWT)
- **Caching**: Flask-Caching
- **Rate Limiting**: Flask-Limiter
- **Migrations**: Flask-Migrate
- **API Documentation**: Flasgger (Swagger UI)
- **Testing**: Postman

---

## File Structure

```
factory_management/
├── app.py                        # Main application entry point
├── blueprints/                   # Modular route management
│   ├── analytics_blueprint.py    # Analytics API routes
│   ├── customer_blueprint.py     # Customer API routes
│   ├── employee_blueprint.py     # Employee API routes
│   ├── order_blueprint.py        # Order API routes
│   ├── product_blueprint.py      # Product API routes
│   ├── production_blueprint.py   # Production API routes
│   ├── user_blueprint.py         # User authentication and management
├── config.py                     # Configuration settings
├── limiter.py                    # Rate limiter setup
├── logs/                         # Log files for debugging and monitoring
│   ├── factory_management.log    # Log file
├── migrations/                   # Database migration files
├── models/                       # Database models
│   ├── customer.py
│   ├── employee.py
│   ├── order.py
│   ├── product.py
│   ├── production.py
│   ├── user.py
├── queries/                      # Advanced SQLAlchemy queries
│   ├── analytics_queries.py
├── requirements.txt              # Python dependencies
├── schemas/                      # Marshmallow schemas for data validation
│   ├── customer_schema.py
│   ├── employee_schema.py
│   ├── order_schema.py
│   ├── product_schema.py
│   ├── production_schema.py
│   ├── user_schema.py
├── services/                     # Business logic layer
│   ├── customer_service.py
│   ├── employee_service.py
│   ├── order_service.py
│   ├── product_service.py
│   ├── production_service.py
│   ├── user_service.py
├── tests/                        # Unit tests
├── utils/                        # Utility functions
│   ├── utils.py                  # Token handling and error response
└── README.md                     # Project documentation
```

---

## Installation

### Prerequisites
- Python 3.10 or higher
- MySQL 8.0 or higher
- pip package manager

### Steps

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-repo/factory-management.git
   cd factory-management
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the database**:
   - Update `config.py` and `.env` with your MySQL connection detail / api settings.

4. **Initialize the database**:

   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. **Seed test data (optional)**:

   ```bash
   python tests/mock_data.py
   ```

6. **Run the application**:

   ```bash
   python app.py
   ```

---

## Usage

### Swagger Documentation
- **URL**: [http://127.0.0.1:5000/docs](http://127.0.0.1:5000/docs)

- **Capabilities**:
  - Explore available endpoints.
  - Test API functionality interactively.
  - View expected parameters and responses.

### JWT Authentication
- Obtain a token via the `/login` endpoint.
- Include the token in the `Authorization` header for protected routes:

   ```http
   Authorization: Bearer <your_token>
   ```

### Caching
- **Caching Layer**: Flask-Caching stores results for GET endpoints to improve performance.
- **Invalidate Cache**: Modify relevant data (e.g., via POST, PUT, DELETE) to automatically refresh cached results.

**Cached Endpoints Include**:
- `/employees` (GET)
- `/products` (GET)
- `/orders` (GET)
- `/customers` (GET)
- `/analytics/*` (GET)

---

## Testing

1. **Install pytest**:

   ```bash
   pip install pytest
   ```

2. **Run tests**:

   ```bash
   pytest tests/
   ```

3. **Check logs**:
   - Logs are available in `logs/factory_management.log` for debugging and insights.

---

## Flasgger Implementation and Benefits

### Implementation
- **Integration**: Flasgger provides an interactive Swagger UI for API documentation.
- **Configuration**: Defined in `app.py` with details like title, description, and security settings.
- **Route-level documentation**: Added using `@swag_from` decorators.

**Example Route Documentation**:

```python
@swag_from({
    "tags": ["Employees"],
    "summary": "Create a new employee",
    "description": "Creates a new employee in the system.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["name", "position", "email", "phone"],
                "properties": {
                    "name": {"type": "string", "description": "Employee's name."},
                    "position": {"type": "string", "description": "Job position."},
                    "email": {"type": "string", "description": "Employee's email."},
                    "phone": {"type": "string", "description": "Employee's phone number."}
                }
            }
        }
    ],
    "responses": {
        "201": {"description": "Employee created successfully."},
        "400": {"description": "Validation or creation error."},
        "500": {"description": "Internal server error."}
    }
})
def create_employee():
    ...
```

### Benefits
- **Interactive Documentation**: Explore and test API endpoints through an intuitive UI.
- **Simplified Testing**: Test APIs directly in the browser without external tools.
- **Standardized Format**: Follows OpenAPI Specification (OAS) for compatibility with external tools.
- **Developer-Friendly**: Reduces the learning curve by clearly defining request and response formats.

---

## Contributions

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request with a clear description of your changes.

---

## License

This project is licensed under the MIT License.

