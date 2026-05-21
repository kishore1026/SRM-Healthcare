from functools import wraps
from flask import request, flash, redirect, url_for
from flask_login import current_user, login_required


def audit_action(action, module):
    """Decorator to automatically log actions to audit trail."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            # Log after successful execution
            try:
                from app.services.audit_service import log_audit
                record_id = kwargs.get('id') or kwargs.get('patient_id') or kwargs.get('medicine_id')
                log_audit(
                    action=action,
                    module=module,
                    record_id=record_id
                )
            except Exception:
                pass  # Don't let audit logging break the main flow
            return result
        return decorated_function
    return decorator


def admin_required(f):
    """Ensure user is authenticated (single-doctor system)."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
