from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.forms.visit_forms import VisitForm
from app.services.patient_service import (
    get_patient_by_id, create_visit, get_visit_by_id,
)
from app.services.audit_service import log_audit
from app.models.audit_log import AuditLog
from app.models.doctor import Doctor

visits_bp = Blueprint('visits', __name__, url_prefix='/visits')


# ---------------------------------------------------------------------------
# Visits index (redirect to patients since visits are per-patient)
# ---------------------------------------------------------------------------

@visits_bp.route('/')
@login_required
def index():
    """Visits landing — redirects to patients list."""
    return redirect(url_for('patients.list_patients'))



@visits_bp.route('/add/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def add_visit(patient_id):
    """Record a new visit for a patient."""
    patient = get_patient_by_id(patient_id)
    if not patient:
        flash('Patient not found.', 'warning')
        return redirect(url_for('patients.list_patients'))

    form = VisitForm()
    form.patient_id.data = patient_id

    # Populate doctor choices
    doctors = Doctor.query.order_by(Doctor.doctor_name).all()
    form.doctor_id.choices = [(d.doctor_id, d.doctor_name) for d in doctors]

    # Pre-select current logged-in doctor
    if request.method == 'GET':
        form.doctor_id.data = current_user.doctor_id

    if form.validate_on_submit():
        try:
            visit = create_visit(form, patient_id)
            log_audit(
                action=AuditLog.ACTION_VISIT_CREATE,
                module=AuditLog.MODULE_VISITS,
                record_id=visit.visit_id,
                details=f'Visit for patient: {patient.patient_name} (S/N: {visit.serial_number})'
            )
            flash(
                f'Visit recorded successfully for {patient.patient_name}. '
                f'Serial Number: {visit.serial_number}',
                'success'
            )
            return redirect(url_for('visits.view_visit', id=visit.visit_id))
        except Exception as e:
            from app.extensions import db
            db.session.rollback()
            flash(f'Error recording visit: {str(e)}', 'danger')

    return render_template('visits/add.html', form=form, patient=patient)


# ---------------------------------------------------------------------------
# View visit
# ---------------------------------------------------------------------------

@visits_bp.route('/<int:id>')
@login_required
def view_visit(id):
    """View full details of a visit including prescriptions."""
    visit = get_visit_by_id(id)
    if not visit:
        flash('Visit record not found.', 'warning')
        return redirect(url_for('patients.list_patients'))

    prescriptions = visit.prescriptions.all()

    return render_template(
        'visits/view.html',
        visit=visit,
        patient=visit.patient,
        prescriptions=prescriptions,
    )
