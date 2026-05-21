from app.extensions import db
from datetime import datetime


class AuditLog(db.Model):
    """System-wide audit log for tracking critical actions."""

    __tablename__ = 'audit_logs'

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_id = db.Column(
        db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=True
    )
    action = db.Column(db.String(100), nullable=False)
    module = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Action constants
    ACTION_LOGIN = 'LOGIN'
    ACTION_LOGOUT = 'LOGOUT'
    ACTION_LOGIN_FAILED = 'LOGIN_FAILED'
    ACTION_PATIENT_CREATE = 'PATIENT_CREATE'
    ACTION_PATIENT_EDIT = 'PATIENT_EDIT'
    ACTION_VISIT_CREATE = 'VISIT_CREATE'
    ACTION_PRESCRIPTION_CREATE = 'PRESCRIPTION_CREATE'
    ACTION_MEDICINE_ADD = 'MEDICINE_ADD'
    ACTION_MEDICINE_EDIT = 'MEDICINE_EDIT'
    ACTION_MEDICINE_DELETE = 'MEDICINE_DELETE'
    ACTION_STOCK_ADD = 'STOCK_ADD'
    ACTION_STOCK_DEDUCT = 'STOCK_DEDUCT'
    ACTION_EXPORT = 'EXPORT'

    # Module constants
    MODULE_AUTH = 'AUTH'
    MODULE_PATIENTS = 'PATIENTS'
    MODULE_VISITS = 'VISITS'
    MODULE_PRESCRIPTIONS = 'PRESCRIPTIONS'
    MODULE_MEDICINES = 'MEDICINES'
    MODULE_EXPORT = 'EXPORT'

    def __repr__(self):
        return f'<AuditLog {self.log_id}: {self.action}>'
