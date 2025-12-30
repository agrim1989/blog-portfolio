import os
from pathlib import Path
from decouple import config

basedir = Path(__file__).resolve().parent


class Config:
    """Base configuration"""
    SECRET_KEY = config('SECRET_KEY', default='dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    UPLOAD_FOLDER = basedir / 'static' / 'uploads'
    UPLOAD_IMAGE_FOLDER = basedir / 'static' / 'uploads' / 'images'
    UPLOAD_VIDEO_FOLDER = basedir / 'static' / 'uploads' / 'videos'
    UPLOAD_RESUME_FOLDER = basedir / 'static' / 'uploads' / 'resumes'
    
    # Allowed file extensions
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov', 'avi'}
    
    # Pagination
    POSTS_PER_PAGE = 6
    
    # Razorpay Payment Settings
    RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID', default='')
    RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET', default='')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'instance' / 'site.db'}"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Handle both PostgreSQL (from Render) and SQLite fallback
    database_url = os.getenv('DATABASE_URL', '')
    if database_url:
        # PostgreSQL from Render or other providers
        # Render provides postgres:// but SQLAlchemy needs postgresql://
        if database_url.startswith('postgres://'):
            SQLALCHEMY_DATABASE_URI = database_url.replace('postgres://', 'postgresql://', 1)
        elif database_url.startswith('postgresql://'):
            SQLALCHEMY_DATABASE_URI = database_url
        else:
            # Fallback to SQLite if URL format is unexpected
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'instance' / 'site.db'}"
    else:
        # Fallback to SQLite if no DATABASE_URL is set
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'instance' / 'site.db'}"


config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

