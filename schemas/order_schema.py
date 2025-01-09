from marshmallow import Schema, fields, validate, post_dump


class OrderSchema(Schema):
    # ---------------------------
    # Fields
    # ---------------------------
    id = fields.Int(dump_only=True)

    customer_id = fields.Int(
        required=True,
        error_messages={"required": "Customer ID is required."}
    )

    product_id = fields.Int(
        required=True,
        error_messages={"required": "Product ID is required."}
    )

    quantity = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="Quantity must be at least 1.")
    )

    total_price = fields.Float(
        dump_only=True,
        error_messages={"invalid": "Invalid total price format."}
    )

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)  # Tracks updates
    deleted_at = fields.DateTime(dump_only=True)  # For soft delete handling

    # ---------------------------
    # Meta Configuration
    # ---------------------------
    class Meta:
        ordered = True  # Preserve order of fields in serialized output.

    # ---------------------------
    # Custom Serialization Rules
    # ---------------------------
    @post_dump
    def remove_null_fields(self, data, **kwargs):
        """Removes null fields from serialized output."""
        return {key: value for key, value in data.items() if value is not None}


# ---------------------------
# Example Usage
# ---------------------------
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
