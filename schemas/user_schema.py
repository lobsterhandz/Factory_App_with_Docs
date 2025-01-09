from marshmallow import Schema, fields, validate, post_dump


class UserSchema(Schema):
    # Fields
    id = fields.Int(dump_only=True)

    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=80)
    )

    password = fields.Str(
        required=True,
        load_only=True,  # Do not expose password in responses
        validate=validate.Length(min=6)
    )

    role = fields.Str(
        required=True,
        validate=validate.OneOf(['super_admin', 'admin', 'user'])
    )

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # ---------------------------
    # Meta Configuration
    # ---------------------------
    class Meta:
        ordered = True  # Preserve field order in serialized output

    # ---------------------------
    # Custom Serialization Rules
    # ---------------------------
    @post_dump
    def remove_null_fields(self, data, **kwargs):
        """Remove null fields from the serialized output."""
        return {key: value for key, value in data.items() if value is not None}


# Single user schema
user_schema = UserSchema()

# Multiple users schema
users_schema = UserSchema(many=True)
