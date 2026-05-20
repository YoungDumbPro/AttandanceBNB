"""Application configuration module."""
import os
from dotenv import load_dotenv

load_dotenv()


def get_env_variable(name, default=None, required=False):
    value = os.environ.get(name, default)
    if required and not value:
        raise RuntimeError(f"The {name} environment variable is required.")
    return value


class Config:
    """Base configuration."""
    SECRET_KEY = get_env_variable('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = get_env_variable(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/attendance_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20,
    }
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PREFERRED_URL_SCHEME = 'https'
    JSON_SORT_KEYS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    WTF_CSRF_SSL_STRICT = True

    @staticmethod
    def init_app(app):
        if not app.config.get('SECRET_KEY') or app.config['SECRET_KEY'] == 'dev-secret-key-change-in-production':
            raise RuntimeError('SECRET_KEY must be set to a strong value in production.')
        if not app.config.get('SQLALCHEMY_DATABASE_URI'):
            raise RuntimeError('DATABASE_URL must be set in production.')
        if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:///'):
            raise RuntimeError('Production must use a PostgreSQL DATABASE_URL, not sqlite.')


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
