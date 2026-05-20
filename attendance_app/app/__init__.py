"""Flask application factory."""
import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

# Configure login manager
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'


def create_app(config_name='default'):
    """Create and configure Flask application.
    
    Args:
        config_name: Configuration name (development, production, testing)
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    config_obj = config.get(config_name, config['default'])
    app.config.from_object(config_obj)
    config_obj.init_app(app)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Register blueprints
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.attendance import attendance_bp
    app.register_blueprint(attendance_bp)

    from app.admin import admin_bp
    app.register_blueprint(admin_bp)

    # Import models for migration support
    from app.models import employee, attendance  # noqa: F401

    # Production logging and proxy support
    if not app.debug and not app.testing:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
        _setup_logging(app)

    # In development and testing, create missing tables automatically.
    if config_name != 'production':
        with app.app_context():
            db.create_all()

    return app


def _setup_logging(app):
    """Configure application logging."""
    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler(
        'logs/attendance_app.log',
        maxBytes=10240000,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Attendance App startup')
