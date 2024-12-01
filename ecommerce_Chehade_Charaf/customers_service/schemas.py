from marshmallow import Schema, fields, validate, validates, ValidationError

class CustomerSchema(Schema): # required -> deserialization
    id = fields.Int(dump_only=True)
    full_name = fields.Str(required=True)
    username = fields.Str(required=True, validate=validate.Length(min=3))
    password = fields.Str(load_only=True, required=True)
    age = fields.Int(required=True, validate=validate.Range(min=1, max=120))
    address = fields.Str(required=True)
    gender = fields.Str(required=True)
    marital_status = fields.Str(required=True)
    wallet_balance = fields.Float(dump_only=True)

    @validates('username')
    def validate_username(self, value):
        if not value.isalnum():
            raise ValidationError('Username must be alphanumeric')
