import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Flask application configuration."""

    # Flask core
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')

    # Database (MySQL via XAMPP)
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'srm_healthcare')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
    }

    # Session
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'flask_session'
    )
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(
        minutes=int(os.environ.get('SESSION_TIMEOUT_MINUTES', 30))
    )
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour

    # App-specific settings
    LOW_STOCK_THRESHOLD = int(os.environ.get('LOW_STOCK_THRESHOLD', 10))
    EXPIRY_WARNING_DAYS = int(os.environ.get('EXPIRY_WARNING_DAYS', 30))
    ITEMS_PER_PAGE = 25
