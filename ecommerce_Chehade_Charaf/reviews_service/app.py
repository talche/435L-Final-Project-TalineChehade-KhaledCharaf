# app.py

from flask import Flask
from flask_restful import Api
from config import Config
from database import db
from resources.reviews import ReviewListResource, ReviewResource, ProductReviewsResource, CustomerReviewsResource, ReviewApprovalResource, ReviewRejectionResource
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)
api = Api(app)

# Register endpoints
api.add_resource(ReviewListResource, '/reviews')
api.add_resource(ReviewResource, '/reviews/<int:review_id>')
api.add_resource(ProductReviewsResource, '/products/<int:product_id>/reviews')
api.add_resource(CustomerReviewsResource, '/customers/<string:username>/reviews')
api.add_resource(ReviewApprovalResource, '/reviews/<int:review_id>/approve')
api.add_resource(ReviewRejectionResource, '/reviews/<int:review_id>/reject')

with app.app_context():
    db.create_all()  # Create tables based on models

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8004)
