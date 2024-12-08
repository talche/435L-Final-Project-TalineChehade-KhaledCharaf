import pybreaker
import logging
from flask_restful import Resource
from flask import request
from models import Customer
from database import db
from schemas import CustomerSchema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# Initialize the circuit breaker
circuit_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=60)  # Max 3 failures, reset after 60 seconds

customer_schema = CustomerSchema()
customer_list_schema = CustomerSchema(many=True)

def simulate_failure():
    """
    Simulate a failure, such as a database unavailability.

    This function raises an exception to simulate a failure in the system.
    It can be used to test the circuit breaker and fault-tolerant behavior.
    """
    raise Exception("Database is down or not reachable")

class CustomerRegister(Resource):
    """
    Resource for registering a new customer.

    Allows users to register a new customer by providing the required details.
    It also validates the data and checks if the username already exists.
    """
    def post(self):
        """
        Handle POST request to register a new customer.

        This method validates input data, checks if the username already exists,
        and creates a new customer record in the database. If an error occurs, 
        it returns the appropriate error message.
        
        Returns:
            dict: The response containing the status message and customer details
            or error information.
        """
        data = request.get_json()

        try:
            # Simulate failure before database operation
            #simulate_failure()

            # Normal logic if no failure occurs
            errors = customer_schema.validate(data)
            if errors:
                return {'message': 'Validation errors', 'errors': errors}, 400

            if Customer.query.filter_by(username=data['username']).first():
                return {'message': 'Username already exists'}, 400

            new_customer = Customer(
                full_name=data['full_name'],
                username=data['username'],
                password=data['password'],
                age=data['age'],
                address=data['address'],
                gender=data['gender'],
                marital_status=data['marital_status']
            )
            db.session.add(new_customer)
            db.session.commit()

            access_token = create_access_token(identity=new_customer.username)
            result = customer_schema.dump(new_customer)
            return {'message': 'Customer registered', 'customer': result, 'access_token': access_token}, 201

        except Exception as e:
            # Wrap the failure in the circuit breaker
            try:
                circuit_breaker.call(lambda: 1 / 0)  # Trigger failure
                logging.error(f"Simulated error: {str(e)}")
                return {'message': 'Simulated error occurred, please try again later'}, 503
            except pybreaker.CircuitBreakerError:
                return {'message': 'Circuit breaker is open, service unavailable'}, 503

class CustomerResource(Resource):
    """
    Resource for handling operations related to a specific customer.
    
    Supports GET, PUT, and DELETE requests for customer data.
    """
    
    @jwt_required()
    def get(self, username):
        """
        Handle GET request to retrieve a customer's details.

        This method checks if the current user is authorized to access the data,
        retrieves the customer information from the database, and returns it.
        
        Args:
            username (str): The username of the customer.

        Returns:
            dict: Customer data or error message.
        """
        current_user = get_jwt_identity()
        if current_user != username:
            return {'message': 'Unauthorized access'}, 403

        try:
            customer = circuit_breaker.call(Customer.query.filter_by, username=username).first()
        except pybreaker.CircuitBreakerError:
            return {'message': 'Circuit breaker triggered, unable to fetch customer'}, 503

        if not customer:
            return {'message': 'Customer not found'}, 404
        result = customer_schema.dump(customer)
        return {'customer': result}, 200

    @jwt_required()
    def put(self, username):
        """
        Handle PUT request to update a customer's details.

        This method allows updating the customer details like name, age, etc., 
        but only if the current user is the one making the request.

        Args:
            username (str): The username of the customer to update.

        Returns:
            dict: The updated customer information or error message.
        """
        current_user = get_jwt_identity()
        if current_user != username:
            return {'message': 'Unauthorized access'}, 403

        data = request.get_json()
        try:
            customer = circuit_breaker.call(Customer.query.filter_by, username=username).first()
        except pybreaker.CircuitBreakerError:
            return {'message': 'Circuit breaker triggered, unable to fetch customer'}, 503

        if not customer:
            return {'message': 'Customer not found'}, 404

        customer.full_name = data.get('full_name', customer.full_name)
        customer.age = data.get('age', customer.age)
        customer.address = data.get('address', customer.address)
        customer.gender = data.get('gender', customer.gender)
        customer.marital_status = data.get('marital_status', customer.marital_status)

        try:
            circuit_breaker.call(db.session.commit)
        except pybreaker.CircuitBreakerError:
            return {'message': 'Circuit breaker triggered, unable to update customer'}, 503

        result = customer_schema.dump(customer)
        return {'message': 'Customer updated', 'customer': result}, 200

    @jwt_required()
    def delete(self, username):
        """
        Handle DELETE request to remove a customer from the database.

        This method deletes the customer if they exist and the current user is authorized.
        
        Args:
            username (str): The username of the customer to delete.

        Returns:
            dict: Status message indicating success or failure.
        """
        current_user = get_jwt_identity()
        if current_user != username:
            return {'message': 'Unauthorized access'}, 403

        try:
            customer = circuit_breaker.call(Customer.query.filter_by, username=username).first()
        except pybreaker.CircuitBreakerError:
            return {'message': 'Circuit breaker triggered, unable to fetch customer'}, 503

        if not customer:
            return {'message': 'Customer not found'}, 404

        try:
            circuit_breaker.call(db.session.delete, customer)
            circuit_breaker.call(db.session.commit)
        except pybreaker.CircuitBreakerError:
            return {'message': 'Circuit breaker triggered, unable to delete customer'}, 503

        return {'message': 'Customer deleted'}, 200

class CustomerList(Resource):
    """
    Resource to retrieve a list of all customers.
    
    Supports GET requests to fetch the list of all customers from the database.
    """
    def get(self):
        """
        Handle GET request to retrieve all customers.

        This method retrieves all customers and returns their details in a list.

        Returns:
            dict: List of all customers or an error message.
        """
        try:
            customers = circuit_breaker.call(Customer.query.all)
        except pybreaker.CircuitBreakerError:
            return {'message': 'Circuit breaker triggered, unable to fetch customers'}, 503
        result = customer_list_schema.dump(customers)
        return {'customers': result}, 200

class DeductBalance(Resource):
    """
    Resource to deduct balance from a customer's wallet.
    
    Allows a customer to deduct a specified amount from their wallet.
    """
    @jwt_required()
    def post(self):
        """
        Handle POST request to deduct balance from a customer's wallet.

        Args:
            username (str): The username of the customer.
            amount (float): The amount to deduct from the wallet.

        Returns:
            dict: Status message with the new balance or an error message.
        """
        data = request.get_json()
        username = data.get('username')
        amount = data.get('amount')

        try:
            customer = circuit_breaker.call(Customer.query.filter_by, username=username).first()
        except pybreaker.CircuitBreakerError:
            return {'message': 'Circuit breaker triggered, unable to fetch customer'}, 503

        if not customer:
            return {'message': 'Customer not found'}, 404

        if customer.wallet_balance < amount:
            return {'message': 'Insufficient wallet balance'}, 400

        customer.wallet_balance -= amount

        try:
            circuit_breaker.call(db.session.commit)
        except pybreaker.CircuitBreakerError:
            return {'message': 'Circuit breaker triggered, unable to update balance'}, 503

        return {'message': 'Balance deducted', 'new_balance': customer.wallet_balance}, 200

class AddBalance(Resource):
    """
    Resource to add balance to a customer's wallet.

    Allows a customer to add a specified amount to their wallet.
    """
    @jwt_required()
    def post(self):
        """
        Handle POST request to add balance to a customer's wallet.

        Args:
            username (str): The username of the customer.
            amount (float): The amount to add to the wallet.

        Returns:
            dict: Status message with the new balance or an error message.
        """
        data = request.get_json()
        username = data.get('username')
        amount = data.get('amount')

        try:
            customer = circuit_breaker.call(Customer.query.filter_by, username=username).first()
        except pybreaker.CircuitBreakerError:
            return {'message': 'Circuit breaker triggered, unable to fetch customer'}, 503

        if not customer:
            return {'message': 'Customer not found'}, 404

        customer.wallet_balance += amount

        try:
            circuit_breaker.call(db.session.commit)
        except pybreaker.CircuitBreakerError:
            return {'message': 'Circuit breaker triggered, unable to update balance'}, 503

        return {'message': 'Balance Added', 'new_balance': customer.wallet_balance}, 200
