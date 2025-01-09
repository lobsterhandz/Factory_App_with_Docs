from marshmallow import Schema, fields, validate, post_dump

class ProductSchema(Schema):
    # ---------------------------
    # Fields
    # ---------------------------
    id = fields.Int(dump_only=True)

    name = fields.Str(
        required=True,
        validate=validate.Length(
            min=1,
            max=100,
            error="Product name must be between 1 and 100 characters."
        )
    )

    price = fields.Decimal(
        required=True,
        places=2,  # Ensures 2 decimal places
        validate=validate.Range(
            min=0,
            error="Price must be a positive number or zero."
        ),
        error_messages={"invalid": "Invalid price format. Use a valid decimal value."}
    )

    stock_quantity = fields.Int(
        required=True,
        validate=validate.Range(
            min=0,
            error="Stock quantity must be zero or a positive integer."
        ),
        error_messages={"invalid": "Invalid stock quantity format. Must be an integer."}
    )

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)  # Tracks updates
    deleted_at = fields.DateTime(dump_only=True)  # Tracks soft deletes

    # ---------------------------
    # Meta Configuration
    # ---------------------------
    class Meta:
        ordered = True  # Ensures fields appear in the defined order.

    # ---------------------------
    # Custom Serialization Rules
    # ---------------------------
    @post_dump
    def remove_null_fields(self, data, **kwargs):
        """Removes null fields from the serialized output."""
        return {key: value for key, value in data.items() if value is not None}


# ---------------------------
# Example Usage
# ---------------------------
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
