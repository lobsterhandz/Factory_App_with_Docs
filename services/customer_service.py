from models import db, Customer


class CustomerService:
    # Allowed sortable fields
    SORTABLE_FIELDS = ['name', 'email', 'phone']

    # ---------------------------
    # Create Customer
    # ---------------------------
    @staticmethod
    def create_customer(name, email, phone):
        """
        Creates a new customer after validating inputs.

        Args:
            name (str): Customer's name.
            email (str): Customer's email.
            phone (str): Customer's phone number.

        Returns:
            Customer: Newly created customer object.

        Raises:
            ValueError: If any validation fails.
        """
        try:
            # Validate required fields
            if not name or not email or not phone:
                raise ValueError("All fields (name, email, phone) are required.")

            # Check for duplicates
            existing_customer = Customer.query.filter(
                (Customer.email == email) | (Customer.phone == phone)
            ).first()
            if existing_customer:
                raise ValueError("Customer with this email or phone already exists.")

            # Create a new customer
            new_customer = Customer(
                name=name,
                email=email,
                phone=phone
            )
            db.session.add(new_customer)
            db.session.commit()
            return new_customer
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error creating customer: {str(e)}")

    # ---------------------------
    # Paginated Customers
    # ---------------------------
    @staticmethod
    def get_paginated_customers(page=1, per_page=10, sort_by='name', sort_order='asc', include_meta=True):
        """
        Retrieves a paginated list of customers with sorting options.

        Args:
            page (int): Current page number.
            per_page (int): Number of records per page.
            sort_by (str): Field to sort by ('name', 'email', 'phone').
            sort_order (str): Sort order ('asc' or 'desc').
            include_meta (bool): Whether to include metadata in the response.

        Returns:
            dict: Paginated customer data with metadata.

        Raises:
            ValueError: If any validation or database query fails.
        """
        try:
            # Validate inputs
            page = max(1, int(page))  # Ensure page >= 1
            per_page = min(max(1, int(per_page)), 100)  # Limit 1 <= per_page <= 100

            # Validate sorting fields
            if sort_by not in CustomerService.SORTABLE_FIELDS:
                raise ValueError(f"Invalid sort_by field. Allowed fields: {CustomerService.SORTABLE_FIELDS}")

            # Determine sort order
            sort_column = getattr(Customer, sort_by, Customer.name)  # Default to 'name'
            if sort_order.lower() == 'desc':
                sort_column = sort_column.desc()

            # Query customers with pagination and sorting
            pagination = Customer.query.order_by(sort_column).paginate(
                page=page, per_page=per_page, error_out=False
            )

            # Prepare response
            response = {"items": pagination.items}
            if include_meta:
                response.update({
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "page": pagination.page,
                    "per_page": pagination.per_page
                })

            return response
        except Exception as e:
            raise ValueError(f"Error retrieving paginated customers: {str(e)}")

    # ---------------------------
    # Get Customer by ID
    # ---------------------------
    @staticmethod
    def get_customer_by_id(customer_id):
        """
        Fetches a customer by ID.

        Args:
            customer_id (int): Customer's ID.

        Returns:
            Customer: Customer object if found.

        Raises:
            ValueError: If customer is not found or query fails.
        """
        try:
            customer = Customer.query.get(customer_id)
            if not customer:
                raise ValueError("Customer not found.")
            return customer
        except Exception as e:
            raise ValueError(f"Error retrieving customer: {str(e)}")

    # ---------------------------
    # Update Customer
    # ---------------------------
    @staticmethod
    def update_customer(customer_id, name=None, email=None, phone=None):
        """
        Updates customer details based on provided fields.

        Args:
            customer_id (int): Customer's ID.
            name (str): Updated name.
            email (str): Updated email.
            phone (str): Updated phone number.

        Returns:
            Customer: Updated customer object.

        Raises:
            ValueError: If validation fails or update fails.
        """
        try:
            customer = Customer.query.get(customer_id)
            if not customer:
                raise ValueError("Customer not found.")

            # Ensure at least one field is provided for update
            if not any([name, email, phone]):
                raise ValueError("At least one field (name, email, phone) must be provided for update.")

            # Validate duplicates if email or phone is updated
            if email and Customer.query.filter(Customer.email == email, Customer.id != customer_id).first():
                raise ValueError("Another customer with this email already exists.")
            if phone and Customer.query.filter(Customer.phone == phone, Customer.id != customer_id).first():
                raise ValueError("Another customer with this phone number already exists.")

            # Update fields
            if name:
                customer.name = name
            if email:
                customer.email = email
            if phone:
                customer.phone = phone

            db.session.commit()
            return customer
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error updating customer: {str(e)}")

    # ---------------------------
    # Delete Customer
    # ---------------------------
    @staticmethod
    def delete_customer(customer_id):
        """
        Deletes a customer by ID.

        Args:
            customer_id (int): Customer's ID.

        Returns:
            bool: True if deleted successfully.

        Raises:
            ValueError: If customer is not found or delete operation fails.
        """
        try:
            customer = Customer.query.get(customer_id)
            if not customer:
                raise ValueError("Customer not found.")
            db.session.delete(customer)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error deleting customer: {str(e)}")
