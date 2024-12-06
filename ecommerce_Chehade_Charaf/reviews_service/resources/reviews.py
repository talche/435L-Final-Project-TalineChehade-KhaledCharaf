# resources/reviews.py

from flask_restful import Resource
from flask import request
from models import Review
from schemas import ReviewSchema
from database import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from memory_profiler import profile  # Import the profile decorator

review_schema = ReviewSchema()
review_list_schema = ReviewSchema(many=True)

def is_admin(username):
    """
    Check if the given username belongs to an admin.

    Args:
        username (str): The username to check.

    Returns:
        bool: True if the user is 'admin', False otherwise.
    """
    return username == 'admin'

class ReviewListResource(Resource):
    """
    Resource for creating new reviews.
    """

    @profile  # Memory profiler decorator
    @jwt_required()
    def post(self):
        """
        Submit a new product review.

        This endpoint allows authenticated users to submit a review for a product.
        The review is marked as pending approval by an admin.

        Returns:
            tuple: A tuple containing a JSON response and an HTTP status code.
        """
        data = request.get_json()
        username = get_jwt_identity()
        data['username'] = username
        errors = review_schema.validate(data)
        if errors:
            return {'message': 'Validation errors', 'errors': errors}, 400

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
    """
    Resource for retrieving, updating, and deleting specific reviews.
    """

    @profile
    @jwt_required()
    def get(self, review_id):
        """
        Retrieve a specific review by its ID.

        Args:
            review_id (int): The ID of the review to retrieve.

        Returns:
            tuple: A tuple containing a JSON response and an HTTP status code.
        """
        review = Review.query.get(review_id)
        if not review:
            return {'message': 'Review not found'}, 404

        if not review.is_approved:
            return {'message': 'Review not approved'}, 403

        result = review_schema.dump(review)
        return {'review': result}, 200

    @profile
    @jwt_required()
    def put(self, review_id):
        """
        Update an existing review.

        Args:
            review_id (int): The ID of the review to update.

        Returns:
            tuple: A tuple containing a JSON response and an HTTP status code.
        """
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

    @profile
    @jwt_required()
    def delete(self, review_id):
        """
        Delete a specific review.

        Args:
            review_id (int): The ID of the review to delete.

        Returns:
            tuple: A tuple containing a JSON response and an HTTP status code.
        """
        review = Review.query.get(review_id)
        if not review:
            return {'message': 'Review not found'}, 404

        username = get_jwt_identity()
        if review.username != username and not is_admin(username):
            return {'message': 'Unauthorized access'}, 403

        db.session.delete(review)
        db.session.commit()
        return {'message': 'Review deleted'}, 200

class ProductReviewsResource(Resource):
    """
    Resource for retrieving all approved reviews for a specific product.
    """

    @profile
    def get(self, product_id):
        """
        Retrieve all approved reviews for a given product.

        Args:
            product_id (int): The ID of the product.

        Returns:
            tuple: A tuple containing a JSON response and an HTTP status code.
        """
        reviews = Review.query.filter_by(product_id=product_id, is_approved=True).all()
        result = review_list_schema.dump(reviews)
        return {'reviews': result}, 200

class CustomerReviewsResource(Resource):
    """
    Resource for retrieving all reviews written by a specific customer.
    """

    @profile
    @jwt_required()
    def get(self, username):
        """
        Retrieve all reviews written by the authenticated user.

        Args:
            username (str): The username of the customer.

        Returns:
            tuple: A tuple containing a JSON response and an HTTP status code.
        """
        current_user = get_jwt_identity()
        if current_user != username:
            return {'message': 'Unauthorized access'}, 403

        reviews = Review.query.filter_by(username=username).all()
        result = review_list_schema.dump(reviews)
        return {'reviews': result}, 200

class ReviewApprovalResource(Resource):
    """
    Resource for approving a review by an admin.
    """

    @profile
    @jwt_required()
    def post(self, review_id):
        """
        Approve a specific review.

        Args:
            review_id (int): The ID of the review to approve.

        Returns:
            tuple: A tuple containing a JSON response and an HTTP status code.
        """
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
    """
    Resource for rejecting and deleting a review by an admin.
    """

    @profile
    @jwt_required()
    def post(self, review_id):
        """
        Reject and delete a specific review.

        Args:
            review_id (int): The ID of the review to reject and delete.

        Returns:
            tuple: A tuple containing a JSON response and an HTTP status code.
        """
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
