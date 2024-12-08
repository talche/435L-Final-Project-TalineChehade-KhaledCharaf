from database import db
from werkzeug.security import generate_password_hash, check_password_hash

class Customer(db.Model):
    """
    The `Customer` model represents a customer in the system. It maps to the `customers` table in the database.

    Attributes:
        id (int): Unique identifier for the customer (Primary Key).
        full_name (str): The full name of the customer.
        username (str): The username of the customer (Unique and not nullable).
        password_hash (str): The hashed password of the customer (Used for authentication).
        age (int): The age of the customer.
        address (str): The address of the customer.
        gender (str): The gender of the customer.
        marital_status (str): The marital status of the customer.
        wallet_balance (float): The balance in the customer's wallet (defaults to 0.0).

    Methods:
        password (setter): Hashes the password and stores it in the `password_hash` field.
        verify_password(password): Verifies if the provided password matches the stored hashed password.
    """

    # Table name for the database
    __tablename__ = 'customers'

    # Columns representing the fields in the customers table
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)
    address = db.Column(db.String(200))
    gender = db.Column(db.String(20))
    marital_status = db.Column(db.String(20))
    wallet_balance = db.Column(db.Float, default=0.0)

    @property
    def password(self):
        """
        Prevents direct access to the password attribute. Raises an error if accessed.

        This method prevents direct access to the `password` field, enforcing
        the use of the `password.setter` to assign the password securely.
        """
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """
        Sets the password by hashing it before storing it in the `password_hash` field.

        Args:
            password (str): The plain text password to hash and store.
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Verifies if the provided password matches the stored hashed password.

        Args:
            password (str): The plain text password to verify.

        Returns:
            bool: True if the password matches the stored hash, otherwise False.
        """
        return check_password_hash(self.password_hash, password)

