import os
from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, csrf, sess


def create_app(config_class=Config):
    """Flask application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure session directory exists
    session_dir = app.config.get('SESSION_FILE_DIR')
    if session_dir and not os.path.exists(session_dir):
        os.makedirs(session_dir)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    sess.init_app(app)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.doctor import Doctor
        return Doctor.query.get(int(user_id))

    # Session activity tracking for auto-logout
    @app.before_request
    def before_request_func():
        from flask import session
        from flask_login import current_user
        session.permanent = True
        session.modified = True

    # Template context processors
    @app.context_processor
    def inject_globals():
        from datetime import date, datetime
        from app.utils.helpers import format_date, format_datetime, format_time
        return dict(
            current_date=date.today(),
            current_year=datetime.now().year,
            format_date=format_date,
            format_datetime=format_datetime,
            format_time=format_time,
        )

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.patients import patients_bp
    from app.routes.visits import visits_bp
    from app.routes.prescriptions import prescriptions_bp
    from app.routes.medicines import medicines_bp
    from app.routes.exports import exports_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(visits_bp)
    app.register_blueprint(prescriptions_bp)
    app.register_blueprint(medicines_bp)
    app.register_blueprint(exports_bp)
    app.register_blueprint(api_bp)

    # Root redirect
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('dashboard.index'))

    # Create tables and seed data
    with app.app_context():
        try:
            # Try to create the database if it doesn't exist
            _ensure_database_exists(app)
            db.create_all()
            
            # Dynamically alter designation column to VARCHAR to allow arbitrary user text inputs
            try:
                db.session.execute(db.text("ALTER TABLE patients MODIFY designation VARCHAR(100) NOT NULL;"))
                db.session.commit()
            except Exception as schema_err:
                db.session.rollback()
                print(f"[INFO] Designation ENUM alteration check: {schema_err}")

            _seed_default_doctor(app)
            _seed_default_medicines(app)
            print("[OK] Database connected successfully")
        except Exception as e:
            print("\n" + "=" * 60)
            print("[ERROR] DATABASE CONNECTION ERROR")
            print("=" * 60)
            print(f"Error: {e}")
            print("\nPlease ensure:")
            print("  1. XAMPP is running")
            print("  2. MySQL service is started in XAMPP")
            print("  3. Database credentials in .env are correct")
            print(f"  4. Current config: {app.config.get('DB_USER', 'root')}@{app.config.get('DB_HOST', 'localhost')}:{app.config.get('DB_PORT', '3306')}")
            print("=" * 60 + "\n")

    # Start scheduler for expiry checks (only in main process)
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        _start_scheduler(app)

    return app


def _ensure_database_exists(app):
    """Create the database if it doesn't exist."""
    try:
        import pymysql
        conn = pymysql.connect(
            host=app.config.get('DB_HOST', 'localhost'),
            port=int(app.config.get('DB_PORT', 3306)),
            user=app.config.get('DB_USER', 'root'),
            password=app.config.get('DB_PASSWORD', ''),
        )
        cursor = conn.cursor()
        db_name = app.config.get('DB_NAME', 'srm_healthcare')
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        cursor.close()
        conn.close()
    except Exception:
        pass  # Will be caught by the main error handler


def _seed_default_doctor(app):
    """Create default doctor account if none exists."""
    from app.models.doctor import Doctor
    if Doctor.query.count() == 0:
        doctor = Doctor(
            username='admin',
            doctor_name='Dr. Admin'
        )
        doctor.set_password('admin123')
        db.session.add(doctor)
        db.session.commit()
        print("[OK] Default doctor account created (admin / admin123)")


def _seed_default_medicines(app):
    """Seed default medicines if inventory is empty."""
    from app.models.medicine import Medicine
    from datetime import date, timedelta
    if Medicine.query.count() == 0:
        today = date.today()
        medicines = [
            Medicine(
                medicine_name='Paracetamol 500mg',
                drug_type='Tablets',
                batch_number='BATCH-2025-001',
                expiry_date=today + timedelta(days=400),
                stock_added=500,
                available_balance=500
            ),
            Medicine(
                medicine_name='Amoxicillin 250mg',
                drug_type='Capsules',
                batch_number='BATCH-2025-002',
                expiry_date=today + timedelta(days=300),
                stock_added=300,
                available_balance=300
            ),
            Medicine(
                medicine_name='Cetirizine 10mg',
                drug_type='Tablets',
                batch_number='BATCH-2025-003',
                expiry_date=today + timedelta(days=500),
                stock_added=200,
                available_balance=200
            ),
            Medicine(
                medicine_name='Omeprazole 20mg',
                drug_type='Capsules',
                batch_number='BATCH-2025-004',
                expiry_date=today + timedelta(days=200),
                stock_added=150,
                available_balance=150
            ),
            Medicine(
                medicine_name='Ibuprofen 400mg',
                drug_type='Tablets',
                batch_number='BATCH-2025-005',
                expiry_date=today + timedelta(days=450),
                stock_added=400,
                available_balance=400
            ),
            Medicine(
                medicine_name='Betadine Ointment',
                drug_type='Ointments',
                batch_number='BATCH-2025-006',
                expiry_date=today + timedelta(days=180),
                stock_added=80,
                available_balance=80
            ),
            Medicine(
                medicine_name='Ciprofloxacin Eye Drops',
                drug_type='Eye Drops',
                batch_number='BATCH-2025-007',
                expiry_date=today + timedelta(days=120),
                stock_added=50,
                available_balance=50
            ),
            Medicine(
                medicine_name='Ofloxacin Ear Drops',
                drug_type='Ear Drops',
                batch_number='BATCH-2025-008',
                expiry_date=today + timedelta(days=240),
                stock_added=40,
                available_balance=40
            ),
            Medicine(
                medicine_name='Diclofenac Injection',
                drug_type='Injections',
                batch_number='BATCH-2025-009',
                expiry_date=today + timedelta(days=90),
                stock_added=100,
                available_balance=100
            ),
            Medicine(
                medicine_name='Azithromycin 500mg',
                drug_type='Tablets',
                batch_number='BATCH-2025-010',
                expiry_date=today + timedelta(days=320),
                stock_added=250,
                available_balance=250
            ),
            Medicine(
                medicine_name='Metformin 500mg',
                drug_type='Tablets',
                batch_number='BATCH-2025-011',
                expiry_date=today + timedelta(days=360),
                stock_added=300,
                available_balance=300
            ),
            Medicine(
                medicine_name='Dolo 650mg',
                drug_type='Tablets',
                batch_number='BATCH-2025-012',
                expiry_date=today + timedelta(days=400),
                stock_added=8,
                available_balance=8
            ),
            Medicine(
                medicine_name='Vitamin B Complex',
                drug_type='Tablets',
                batch_number='BATCH-2025-013',
                expiry_date=today + timedelta(days=15),
                stock_added=120,
                available_balance=5
            ),
            Medicine(
                medicine_name='Ranitidine 150mg',
                drug_type='Tablets',
                batch_number='BATCH-2025-014',
                expiry_date=today - timedelta(days=5),
                stock_added=200,
                available_balance=200
            )
        ]
        db.session.add_all(medicines)
        db.session.commit()
        print("[OK] Sample medicines inventory seeded")


def _start_scheduler(app):
    """Start APScheduler for periodic tasks."""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        import atexit

        def check_medicine_alerts():
            with app.app_context():
                from app.models.medicine import Medicine
                from datetime import date, timedelta
                threshold_date = date.today() + timedelta(days=app.config['EXPIRY_WARNING_DAYS'])
                expiring = Medicine.query.filter(
                    Medicine.expiry_date <= threshold_date,
                    Medicine.expiry_date >= date.today()
                ).count()
                if expiring > 0:
                    app.logger.warning(f"⚠ {expiring} medicines expiring within {app.config['EXPIRY_WARNING_DAYS']} days")

        scheduler = BackgroundScheduler()
        scheduler.add_job(func=check_medicine_alerts, trigger='interval', hours=24, id='expiry_check')
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown(wait=False))
    except Exception as e:
        app.logger.error(f"Scheduler error: {e}")
