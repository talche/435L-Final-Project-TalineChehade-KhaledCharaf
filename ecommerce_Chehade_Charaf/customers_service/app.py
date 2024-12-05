from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from config import Config
from database import db
from resources.customer import CustomerRegister, CustomerResource, CustomerList, DeductBalance, AddBalance
import os
app = Flask(__name__)
app.config.from_object(Config)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
#     'SQLALCHEMY_DATABASE_URI',
#     'mysql+pymysql://root:khaled1234321@localhost:3307/ecommerce_db'  # Default for local testing
# )
db.init_app(app)
jwt = JWTManager(app)
api = Api(app)
# Register endpoints
api.add_resource(CustomerRegister, '/customers/register')
api.add_resource(CustomerResource, '/customers/<string:username>')
api.add_resource(CustomerList, '/customers')
api.add_resource(DeductBalance, '/customers/deduct-balance')
api.add_resource(AddBalance, '/customers/add-balance')
with app.app_context():
    db.create_all()  # Create tables based on models

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
