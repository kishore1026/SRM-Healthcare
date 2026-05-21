from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.forms.auth_forms import LoginForm
from app.models.doctor import Doctor

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Doctor login page."""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()

    if form.validate_on_submit():
        doctor = Doctor.query.filter_by(username=form.username.data.strip()).first()

        if doctor and doctor.check_password(form.password.data):
            login_user(doctor, remember=False)  # Don't use remember=True — it overrides session timeout

            # Log the login action
            try:
                from app.services.audit_service import log_audit
                log_audit(
                    action='LOGIN',
                    module='AUTH',
                    record_id=doctor.doctor_id,
                    details=f'Doctor {doctor.doctor_name} logged in'
                )
            except Exception:
                pass  # Don't block login if audit logging fails

            flash(f'Welcome back, {doctor.doctor_name}!', 'success')

            # Redirect to requested page or dashboard
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current doctor."""
    doctor_name = current_user.doctor_name

    # Log the logout action
    try:
        from app.services.audit_service import log_audit
        log_audit(
            action='LOGOUT',
            module='AUTH',
            record_id=current_user.doctor_id,
            details=f'Doctor {doctor_name} logged out'
        )
    except Exception:
        pass

    logout_user()
    return redirect(url_for('auth.login'))
