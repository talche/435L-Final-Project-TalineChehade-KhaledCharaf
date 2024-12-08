from flask import Flask
from flask_restful import Api
from config import Config
from database import db
from resources.goods import GoodsListResource, GoodsResource
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
    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Initialize extensions
    db.init_app(app)
    api = Api(app)

    # Register endpoints
    api.add_resource(GoodsListResource, '/goods')
    api.add_resource(GoodsResource, '/goods/<int:goods_id>')

    # Add ProfilerMiddleware only if FLASK_ENV is development
    if os.getenv('FLASK_ENV') == 'development':
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
    app.run(host='0.0.0.0', port=5002)

