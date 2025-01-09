from models import db, Production, Product
from datetime import datetime


# Custom Exception for Error Handling
class CustomException(Exception):
    def __init__(self, message):
        super().__init__(message)


class ProductionService:
    # ---------------------------
    # Utility: Date Parsing
    # ---------------------------
    @staticmethod
    def parse_date(date_input):
        """Parses date input and returns a datetime object."""
        if isinstance(date_input, str):
            try:
                return datetime.strptime(date_input, "%Y-%m-%d")
            except ValueError:
                raise CustomException("Invalid date format. Use YYYY-MM-DD.")
        elif isinstance(date_input, datetime):
            return date_input
        else:
            raise CustomException("Invalid date format. Use YYYY-MM-DD.")

    # ---------------------------
    # Create production record
    # ---------------------------
    @staticmethod
    def create_production(product_id, quantity_produced, date_produced):
        """
        Creates a new production record.

        Args:
            product_id (int): ID of the product.
            quantity_produced (int): Quantity produced.
            date_produced (str or datetime): Date produced (YYYY-MM-DD).

        Returns:
            Production: Newly created production record.

        Raises:
            CustomException: If any validation fails.
        """
        try:
            # Validate product
            product = Product.query.get(product_id)
            if not product:
                raise CustomException("Product not found.")

            # Validate quantity
            if quantity_produced <= 0:
                raise CustomException("Quantity produced must be greater than zero.")

            # Parse date
            date_produced = ProductionService.parse_date(date_produced)

            # Create production record
            new_production = Production(
                product_id=product_id,
                quantity_produced=quantity_produced,
                date_produced=date_produced
            )
            db.session.add(new_production)
            db.session.commit()
            return new_production
        except Exception as e:
            db.session.rollback()
            raise CustomException(f"Error creating production record: {str(e)}")

    # ---------------------------
    # Paginated Productions
    # ---------------------------
    @staticmethod
    def get_paginated_productions(page=1, per_page=10, sort_by='date_produced', sort_order='asc', include_meta=True):
        """
        Retrieves paginated production records with sorting.

        Args:
            page (int): Page number.
            per_page (int): Number of records per page.
            sort_by (str): Field to sort by ('date_produced', 'quantity_produced').
            sort_order (str): 'asc' or 'desc'.
            include_meta (bool): Include pagination metadata.

        Returns:
            dict: Paginated results and metadata.
        """
        try:
            # Validate inputs
            page = max(1, int(page))
            per_page = min(max(1, int(per_page)), 100)

            # Sorting
            sort_field = getattr(Production, sort_by, Production.date_produced)
            if sort_order.lower() == 'desc':
                sort_field = sort_field.desc()

            # Paginate
            pagination = Production.query.order_by(sort_field).paginate(page=page, per_page=per_page, error_out=False)

            # Response
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
            raise CustomException(f"Error retrieving paginated production records: {str(e)}")

    # ---------------------------
    # Get production by ID
    # ---------------------------
    @staticmethod
    def get_production_by_id(production_id):
        try:
            production = Production.query.get(production_id)
            if not production:
                raise CustomException("Production record not found.")
            return production
        except Exception as e:
            raise CustomException(f"Error retrieving production record: {str(e)}")

    # ---------------------------
    # Update production record
    # ---------------------------
    @staticmethod
    def update_production(production_id, quantity_produced=None, date_produced=None):
        try:
            production = Production.query.get(production_id)
            if not production:
                raise CustomException("Production record not found.")

            # Update quantity
            if quantity_produced is not None:
                if quantity_produced <= 0:
                    raise CustomException("Quantity produced must be greater than zero.")
                production.quantity_produced = quantity_produced

            # Update date
            if date_produced is not None:
                production.date_produced = ProductionService.parse_date(date_produced)

            db.session.commit()
            return production
        except Exception as e:
            db.session.rollback()
            raise CustomException(f"Error updating production record: {str(e)}")

    # ---------------------------
    # Delete production record
    # ---------------------------
    @staticmethod
    def delete_production(production_id):
        try:
            production = Production.query.get(production_id)
            if not production:
                raise CustomException("Production record not found.")
            db.session.delete(production)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise CustomException(f"Error deleting production record: {str(e)}")
