from flask_restful import Resource
from flask import request
from models import Customer
from database import db
from schemas import CustomerSchema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

customer_schema = CustomerSchema()
customer_list_schema = CustomerSchema(many=True)

class CustomerRegister(Resource):
    def post(self):
        data = request.get_json()
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

class CustomerResource(Resource):
    @jwt_required()
    def get(self, username):
        current_user = get_jwt_identity()
        if current_user != username:
            return {'message': 'Unauthorized access'}, 403

        customer = Customer.query.filter_by(username=username).first()
        if not customer:
            return {'message': 'Customer not found'}, 404
        result = customer_schema.dump(customer)
        return {'customer': result}, 200

    @jwt_required()
    def put(self, username):
        current_user = get_jwt_identity()
        if current_user != username:
            return {'message': 'Unauthorized access'}, 403

        data = request.get_json()
        customer = Customer.query.filter_by(username=username).first()
        if not customer:
            return {'message': 'Customer not found'}, 404

        customer.full_name = data.get('full_name', customer.full_name)
        customer.age = data.get('age', customer.age)
        customer.address = data.get('address', customer.address)
        customer.gender = data.get('gender', customer.gender)
        customer.marital_status = data.get('marital_status', customer.marital_status)

        db.session.commit()
        result = customer_schema.dump(customer)
        return {'message': 'Customer updated', 'customer': result}, 200

    @jwt_required()
    def delete(self, username):
        current_user = get_jwt_identity()
        if current_user != username:
            return {'message': 'Unauthorized access'}, 403

        customer = Customer.query.filter_by(username=username).first()
        if not customer:
            return {'message': 'Customer not found'}, 404

        db.session.delete(customer)
        db.session.commit()
        return {'message': 'Customer deleted'}, 200

class CustomerList(Resource):
    def get(self):
        customers = Customer.query.all()
        result = customer_list_schema.dump(customers)
        return {'customers': result}, 200

# Add this new resource
class DeductBalance(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        username = data.get('username')
        amount = data.get('amount')

        customer = Customer.query.filter_by(username=username).first()
        if not customer:
            return {'message': 'Customer not found'}, 404

        if customer.wallet_balance < amount:
            return {'message': 'Insufficient wallet balance'}, 400

        customer.wallet_balance -= amount
        db.session.commit()

        return {'message': 'Balance deducted', 'new_balance': customer.wallet_balance}, 200