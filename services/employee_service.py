from models import db, Employee
from sqlalchemy import func
import logging


class EmployeeService:
    # ---------------------------
    # Create an employee
    # ---------------------------
    @staticmethod
    def create_employee(name, position, email, phone):
        try:
            # Validate required fields
            if not name or not position or not email or not phone:
                raise ValueError("All fields are required.")

            # Check for duplicate email or phone
            existing_employee = Employee.query.filter(
                (Employee.email == email) | (Employee.phone == phone)
            ).first()
            if existing_employee:
                raise ValueError("Employee with this email or phone already exists.")

            # Create a new employee
            new_employee = Employee(
                name=name,
                position=position,
                email=email,
                phone=phone
            )
            db.session.add(new_employee)
            db.session.commit()
            return new_employee
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating employee: {str(e)}")
            raise ValueError(f"Error creating employee: {str(e)}")

    # ---------------------------
    # Paginated Employees (ENHANCED)
    # ---------------------------
    @staticmethod
    def get_paginated_employees(page=1, per_page=10, sort_by='name', sort_order='asc', include_meta=True):
        try:
            # Validate inputs
            page = max(1, int(page))  # Ensure page >= 1
            per_page = min(max(1, int(per_page)), 100)  # Limit 1 <= per_page <= 100

            # Sorting options
            sort_column = getattr(Employee, sort_by, Employee.name)
            if sort_order.lower() == 'desc':
                sort_column = sort_column.desc()

            # Query with pagination and sorting
            pagination = Employee.query.order_by(sort_column).paginate(
                page=page, per_page=per_page, error_out=False
            )

            # Prepare response
            response = {
                "items": pagination.items,
            }

            if include_meta:
                response.update({
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "page": pagination.page,
                    "per_page": pagination.per_page
                })

            return response
        except Exception as e:
            logging.error(f"Error retrieving paginated employees: {str(e)}")
            raise ValueError(f"Error retrieving paginated employees: {str(e)}")

    # ---------------------------
    # Get employee by ID
    # ---------------------------
    @staticmethod
    def get_employee_by_id(employee_id):
        try:
            employee = Employee.query.get(employee_id)
            if not employee:
                raise ValueError("Employee not found.")
            return employee
        except Exception as e:
            logging.error(f"Error retrieving employee: {str(e)}")
            raise ValueError(f"Error retrieving employee: {str(e)}")

    # ---------------------------
    # Update an employee
    # ---------------------------
    @staticmethod
    def update_employee(employee_id, name=None, position=None, email=None, phone=None):
        try:
            employee = Employee.query.get(employee_id)
            if not employee:
                raise ValueError("Employee not found.")

            # Check for duplicate email or phone during updates
            if email and Employee.query.filter(Employee.email == email, Employee.id != employee_id).first():
                raise ValueError("Another employee with this email already exists.")
            if phone and Employee.query.filter(Employee.phone == phone, Employee.id != employee_id).first():
                raise ValueError("Another employee with this phone number already exists.")

            # Update fields if provided
            if name:
                employee.name = name
            if position:
                employee.position = position
            if email:
                employee.email = email
            if phone:
                employee.phone = phone

            db.session.commit()
            return employee
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating employee: {str(e)}")
            raise ValueError(f"Error updating employee: {str(e)}")

    # ---------------------------
    # Delete an employee
    # ---------------------------
    @staticmethod
    def delete_employee(employee_id):
        try:
            employee = Employee.query.get(employee_id)
            if not employee:
                raise ValueError("Employee not found.")
            db.session.delete(employee)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error deleting employee: {str(e)}")
            raise ValueError(f"Error deleting employee: {str(e)}")

