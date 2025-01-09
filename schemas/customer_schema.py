from marshmallow import Schema, fields, validate, post_dump


class CustomerSchema(Schema):
    # Fields
    id = fields.Int(dump_only=True)

    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )

    email = fields.Email(
        required=True,
        validate=validate.Length(max=100)
    )

    phone = fields.Str(
        required=True,
        validate=[
            validate.Length(min=10, max=20),
            validate.Regexp(
                r'^\+?1?\d{9,15}$', 
                error="Invalid phone number format. Must be 10-15 digits with optional +1."
            )
        ]
    )

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)  # Added updated_at field
    deleted_at = fields.DateTime(dump_only=True)  # Added soft delete support

    # ---------------------------
    # Meta Configuration
    # ---------------------------
    class Meta:
        ordered = True  # Preserve field order in JSON output

    # ---------------------------
    # Custom Serialization Rules
    # ---------------------------
    @post_dump
    def remove_null_fields(self, data, **kwargs):
        """Remove null fields from the serialized output."""
        return {key: value for key, value in data.items() if value is not None}


# Example Usage
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
