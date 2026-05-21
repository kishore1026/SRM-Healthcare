from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class Doctor(UserMixin, db.Model):
    """Doctor model for authentication and user management."""

    __tablename__ = 'doctors'

    doctor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    doctor_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    visits = db.relationship('PatientVisit', backref='doctor', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='doctor', lazy='dynamic')

    def get_id(self):
        return str(self.doctor_id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Doctor {self.username}>'
