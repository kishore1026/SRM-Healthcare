import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Flask application configuration."""

    # Flask core
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')

    # Database Configuration (PostgreSQL/MySQL with dynamic SQLite fallback)
    _db_url = os.environ.get('DATABASE_URL')
    if _db_url:
        if _db_url.startswith('postgres://'):
            _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = _db_url
    else:
        # Default MySQL parameters (XAMPP local stack)
        DB_HOST = os.environ.get('DB_HOST', 'localhost')
        DB_PORT = os.environ.get('DB_PORT', '3306')
        DB_USER = os.environ.get('DB_USER', 'root')
        DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
        DB_NAME = os.environ.get('DB_NAME', 'srm_healthcare')

        # Check if local MySQL port is active/connectable
        import socket
        mysql_running = False
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect((DB_HOST, int(DB_PORT)))
            mysql_running = True
            s.close()
        except Exception:
            pass

        if mysql_running:
            SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        else:
            # High-reliability SQLite fallback for local test/cloud deployment
            SQLALCHEMY_DATABASE_URI = 'sqlite:///srm_healthcare.db'

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
