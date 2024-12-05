# app.py

from flask import Flask
from flask_restful import Api
from config import Config
from database import db
from resources.sales import PurchaseResource, PurchaseHistoryResource
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)
api = Api(app)

# Register endpoints
api.add_resource(PurchaseResource, '/purchase')
api.add_resource(PurchaseHistoryResource, '/purchase-history/<string:username>')

with app.app_context():
    db.create_all()  # Create tables based on models

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
