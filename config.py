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


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'instance' / 'site.db'}"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = config('DATABASE_URL', default=f"sqlite:///{basedir / 'instance' / 'site.db'}")


config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

