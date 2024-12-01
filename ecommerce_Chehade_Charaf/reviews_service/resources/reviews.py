# resources/reviews.py

from flask_restful import Resource
from flask import request
from models import Review
from schemas import ReviewSchema
from database import db
from flask_jwt_extended import jwt_required, get_jwt_identity

review_schema = ReviewSchema()
review_list_schema = ReviewSchema(many=True)

def is_admin(username):
    return username == 'admin'
class ReviewListResource(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        errors = review_schema.validate(data)
        if errors:
            return {'message': 'Validation errors', 'errors': errors}, 400

        username = get_jwt_identity()
        data['username'] = username

        new_review = Review(
            product_id=data['product_id'],
            username=username,
            rating=data['rating'],
            comment=data.get('comment', ''),
            is_approved=False  # Reviews need to be approved by an admin
        )
        db.session.add(new_review)
        db.session.commit()

        result = review_schema.dump(new_review)
        return {'message': 'Review submitted and pending approval', 'review': result}, 201

class ReviewResource(Resource):
    @jwt_required()
    def get(self, review_id):
        review = Review.query.get(review_id)
        if not review:
            return {'message': 'Review not found'}, 404

        if not review.is_approved:
            return {'message': 'Review not approved'}, 403

        result = review_schema.dump(review)
        return {'review': result}, 200

    @jwt_required()
    def put(self, review_id):
        data = request.get_json()
        review = Review.query.get(review_id)
        if not review:
            return {'message': 'Review not found'}, 404

        username = get_jwt_identity()
        if review.username != username:
            return {'message': 'Unauthorized access'}, 403

        review.rating = data.get('rating', review.rating)
        review.comment = data.get('comment', review.comment)
        review.is_approved = False  # Needs re-approval after changes
        db.session.commit()

        result = review_schema.dump(review)
        return {'message': 'Review updated and pending approval', 'review': result}, 200

    @jwt_required()
    def delete(self, review_id):
        review = Review.query.get(review_id)
        if not review:
            return {'message': 'Review not found'}, 404

        username = get_jwt_identity()
        if review.username != username:
            return {'message': 'Unauthorized access'}, 403

        db.session.delete(review)
        db.session.commit()
        return {'message': 'Review deleted'}, 200

class ProductReviewsResource(Resource):
    def get(self, product_id):
        reviews = Review.query.filter_by(product_id=product_id, is_approved=True).all()
        result = review_list_schema.dump(reviews)
        return {'reviews': result}, 200

class CustomerReviewsResource(Resource):
    @jwt_required()
    def get(self, username):
        current_user = get_jwt_identity()
        if current_user != username:
            return {'message': 'Unauthorized access'}, 403

        reviews = Review.query.filter_by(username=username).all()
        result = review_list_schema.dump(reviews)
        return {'reviews': result}, 200
class ReviewApprovalResource(Resource):
    @jwt_required()
    def post(self, review_id):
        # Implement admin check
        current_user = get_jwt_identity()
        if not is_admin(current_user):
            return {'message': 'Admin privileges required'}, 403

        review = Review.query.get(review_id)
        if not review:
            return {'message': 'Review not found'}, 404

        review.is_approved = True
        db.session.commit()
        return {'message': 'Review approved'}, 200

class ReviewRejectionResource(Resource):
    @jwt_required()
    def post(self, review_id):
        # Implement admin check
        current_user = get_jwt_identity()
        if not is_admin(current_user):
            return {'message': 'Admin privileges required'}, 403

        review = Review.query.get(review_id)
        if not review:
            return {'message': 'Review not found'}, 404

        db.session.delete(review)
        db.session.commit()
        return {'message': 'Review rejected and deleted'}, 200
