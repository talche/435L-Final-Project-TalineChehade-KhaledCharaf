# app.py

from flask import Flask
from flask_restful import Api
from config import Config
from database import db
from resources.reviews import (
    ReviewListResource, ReviewResource, ProductReviewsResource,
    CustomerReviewsResource, ReviewApprovalResource, ReviewRejectionResource
)
from flask_jwt_extended import JWTManager
from werkzeug.middleware.profiler import ProfilerMiddleware
import os

def create_app(config_object=Config):
    """
    Create and configure the Flask application.

    Args:
        config_object (object): Configuration object for Flask.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Initialize extensions
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

    # Add ProfilerMiddleware only if FLASK_ENV is development
    if os.getenv('FLASK_ENV') == 'development':
        # Ensure the profiling directory exists
        profile_dir = '/performance_profiler'
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)

        app.wsgi_app = ProfilerMiddleware(
            app.wsgi_app,
            restrictions=[30],  # Show top 30 functions
            profile_dir=profile_dir
        )
        app.logger.info("ProfilerMiddleware enabled. Profiling data will be saved to /performance_profiler.")

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5004)
