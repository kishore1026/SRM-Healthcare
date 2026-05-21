"""Prescription routes – create and view prescriptions with auto stock deduction."""
import json

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models.visit import PatientVisit
from app.models.medicine import Medicine
from app.models.prescription import Prescription, PrescriptionItem
from app.models.audit_log import AuditLog
from app.forms.prescription_forms import PrescriptionForm
from app.services.audit_service import log_audit
from app.services.medicine_service import deduct_for_prescription, validate_prescription_items

prescriptions_bp = Blueprint('prescriptions', __name__, url_prefix='/prescriptions')


@prescriptions_bp.route('/')
@login_required
def index():
    """Redirect to patients list – prescriptions are created per-visit."""
    return redirect(url_for('patients.index'))


@prescriptions_bp.route('/create/<int:visit_id>', methods=['GET', 'POST'])
@login_required
def create(visit_id):
    """Create a prescription for a visit with dynamic medicine rows."""
    visit = PatientVisit.query.get_or_404(visit_id)
    form = PrescriptionForm()

    # Check if a prescription already exists for this visit
    existing = Prescription.query.filter_by(visit_id=visit_id).first()
    if existing:
        flash('A prescription already exists for this visit.', 'warning')
        return redirect(url_for('prescriptions.view', id=existing.prescription_id))

    # Get all non-expired medicines for the dropdown
    medicines = Medicine.query.filter(
        Medicine.available_balance > 0
    ).order_by(Medicine.medicine_name).all()

    if form.validate_on_submit():
        # Parse items from hidden JSON field
        try:
            items_data = json.loads(form.items_json.data or '[]')
        except (json.JSONDecodeError, TypeError):
            flash('Invalid prescription data. Please try again.', 'danger')
            return render_template('prescriptions/create.html',
                                   form=form, visit=visit, medicines=medicines)

        # Validate all items
        valid, errors = validate_prescription_items(items_data)
        if not valid:
            for err in errors:
                flash(err, 'danger')
            return render_template('prescriptions/create.html',
                                   form=form, visit=visit, medicines=medicines)

        # Create prescription
        prescription = Prescription(
            visit_id=visit_id,
            notes=form.notes.data,
        )
        db.session.add(prescription)
        db.session.flush()  # Get prescription_id before adding items

        # Create items and deduct stock
        try:
            for item_data in items_data:
                medicine = Medicine.query.get(int(item_data['medicine_id']))
                quantity = int(item_data['quantity'])

                # Deduct stock
                deduct_for_prescription(medicine, quantity, prescription.prescription_id)

                # Create prescription item
                item = PrescriptionItem(
                    prescription_id=prescription.prescription_id,
                    medicine_id=medicine.medicine_id,
                    dosage=item_data.get('dosage', ''),
                    frequency=item_data.get('frequency', ''),
                    duration=item_data.get('duration', ''),
                    quantity=quantity,
                    instructions=item_data.get('instructions', ''),
                )
                db.session.add(item)

            db.session.commit()

            log_audit(
                AuditLog.ACTION_PRESCRIPTION_CREATE,
                AuditLog.MODULE_PRESCRIPTIONS,
                record_id=prescription.prescription_id,
                details=f'Prescription for Visit #{visit_id} with {len(items_data)} items'
            )

            flash('Prescription created and stock updated successfully!', 'success')
            return redirect(url_for('prescriptions.view', id=prescription.prescription_id))

        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating prescription: {str(e)}', 'danger')

    return render_template('prescriptions/create.html',
                           form=form, visit=visit, medicines=medicines)


@prescriptions_bp.route('/<int:id>')
@login_required
def view(id):
    """View a single prescription's details."""
    prescription = Prescription.query.get_or_404(id)
    visit = prescription.visit
    patient = visit.patient

    return render_template('prescriptions/view.html',
                           prescription=prescription,
                           visit=visit,
                           patient=patient)
