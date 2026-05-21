from app.extensions import db
from app.models.audit_log import AuditLog
from flask_login import current_user
from flask import request


def log_audit(action, module, record_id=None, details=None):
    """Log an action to the audit trail.

    Args:
        action: Action constant from AuditLog (e.g., AuditLog.ACTION_LOGIN)
        module: Module constant from AuditLog (e.g., AuditLog.MODULE_AUTH)
        record_id: Optional ID of the affected record
        details: Optional text details about the action
    """
    try:
        doctor_id = current_user.doctor_id if current_user and current_user.is_authenticated else None
        ip_address = request.remote_addr if request else None

        log = AuditLog(
            doctor_id=doctor_id,
            action=action,
            module=module,
            record_id=record_id,
            details=details,
            ip_address=ip_address
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Audit log error: {e}")


def get_audit_logs(page=1, per_page=25, action_filter=None, module_filter=None,
                   date_from=None, date_to=None):
    """Retrieve paginated audit logs with optional filters."""
    query = AuditLog.query

    if action_filter:
        query = query.filter(AuditLog.action == action_filter)
    if module_filter:
        query = query.filter(AuditLog.module == module_filter)
    if date_from:
        query = query.filter(AuditLog.created_at >= date_from)
    if date_to:
        from datetime import datetime, timedelta
        end = datetime.combine(date_to, datetime.max.time())
        query = query.filter(AuditLog.created_at <= end)

    return query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
