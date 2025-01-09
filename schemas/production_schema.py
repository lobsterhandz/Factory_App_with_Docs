from marshmallow import Schema, fields, validate, post_dump


class ProductionSchema(Schema):
    # ---------------------------
    # Fields
    # ---------------------------
    id = fields.Int(dump_only=True)

    product_id = fields.Int(
        required=True,
        error_messages={"required": "Product ID is required."}
    )

    quantity_produced = fields.Int(
        required=True,
        validate=validate.Range(
            min=1,
            error="Quantity produced must be at least 1."
        )
    )

    date_produced = fields.Date(
        required=True,
        error_messages={"invalid": "Invalid date format. Use YYYY-MM-DD."}
    )

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)  # Tracks updates
    deleted_at = fields.DateTime(dump_only=True)  # Tracks soft deletes

    # ---------------------------
    # Meta Configuration
    # ---------------------------
    class Meta:
        ordered = True  # Ensures fields are serialized in defined order.

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
production_schema = ProductionSchema()
productions_schema = ProductionSchema(many=True)
