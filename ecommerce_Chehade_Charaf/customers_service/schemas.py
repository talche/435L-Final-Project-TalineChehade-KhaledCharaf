from marshmallow import Schema, fields, validate, validates, ValidationError

class CustomerSchema(Schema):
    """
    Schema for serializing and deserializing `Customer` data. This schema is used for validation
    and transformation of input and output data for the `Customer` model.

    Attributes:
        id (int): The unique identifier of the customer (read-only during deserialization).
        full_name (str): The full name of the customer (required).
        username (str): The unique username for the customer (required, alphanumeric with a minimum length of 3 characters).
        password (str): The password for the customer (required during deserialization, hashed before storage).
        age (int): The age of the customer (required, must be between 1 and 120).
        address (str): The address of the customer (required).
        gender (str): The gender of the customer (required).
        marital_status (str): The marital status of the customer (required).
        wallet_balance (float): The current wallet balance of the customer (read-only during deserialization).

    Methods:
        validate_username(value): Validates that the username is alphanumeric.

    """
    
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
        """
        Validates that the username is alphanumeric.

        Args:
            value (str): The username value to be validated.

        Raises:
            ValidationError: If the username is not alphanumeric.
        """
        if not value.isalnum():
            raise ValidationError('Username must be alphanumeric')
