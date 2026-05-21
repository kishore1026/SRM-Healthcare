from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

from app.forms.patient_forms import PatientForm
from app.services.patient_service import (
    create_patient, update_patient, get_patient_by_id,
    get_patients_paginated, get_patient_visits, advanced_search,
    search_patients_autocomplete,
)
from app.services.audit_service import log_audit
from app.models.audit_log import AuditLog
from app.forms.patient_forms import HOSTEL_CHOICES, GENDER_CHOICES, DESIGNATION_CHOICES

patients_bp = Blueprint('patients', __name__, url_prefix='/patients')


# ---------------------------------------------------------------------------
# Patient list
# ---------------------------------------------------------------------------

@patients_bp.route('/')
@login_required
def index():
    """Alias for list_patients (used by sidebar navigation)."""
    return list_patients()


@patients_bp.route('/list')
@login_required
def list_patients():
    """Display paginated patient listing with quick-search."""
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '', type=str).strip()

    pagination = get_patients_paginated(page=page, per_page=25, search_query=q if q else None)

    return render_template(
        'patients/list.html',
        patients=pagination.items,
        pagination=pagination,
        search_query=q,
    )


# ---------------------------------------------------------------------------
# Add patient
# ---------------------------------------------------------------------------

@patients_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    """Add a new patient with automatic medicine prescription and stock deduction."""
    from app.models.medicine import Medicine
    from app.extensions import db
    from app.models.patient import Patient
    from app.models.visit import PatientVisit
    from app.models.prescription import Prescription, PrescriptionItem
    from app.services.medicine_service import deduct_for_prescription
    from app.services.patient_service import get_next_serial_number
    from datetime import date, datetime

    form = PatientForm()
    
    # Populate medicine dropdown with active medicines
    medicines = Medicine.query.filter(Medicine.available_balance > 0).order_by(Medicine.medicine_name).all()
    form.medicine_id.choices = [(0, '-- Select Medicine --')] + [
        (m.medicine_id, f"{m.medicine_name} (Available: {m.available_balance})") for m in medicines
    ]

    if form.validate_on_submit():
        # Server-side validation for designation conditional fields
        designation = form.designation.data.strip() if form.designation.data else 'Other'
        if designation == 'Student' and not form.student_id.data:
            form.student_id.errors.append('Student ID Number is mandatory for Student designation.')
            return render_template('patients/add.html', form=form, medicines=medicines)

        # Validate medicine selection
        med_id = form.medicine_id.data
        if med_id == 0:
            flash('Please select a valid medicine.', 'danger')
            return render_template('patients/add.html', form=form, medicines=medicines)

        medicine = Medicine.query.get(med_id)
        if not medicine:
            flash('Selected medicine does not exist.', 'danger')
            return render_template('patients/add.html', form=form, medicines=medicines)

        # Validate stock
        qty = form.quantity.data
        if qty > medicine.available_balance:
            flash(f'Quantity exceeds available stock. Only {medicine.available_balance} available.', 'danger')
            return render_template('patients/add.html', form=form, medicines=medicines)

        # Transaction Block for Atomicity
        try:
            # Determine fields based on designation
            if designation == 'Student':
                student_id = form.student_id.data.strip() if form.student_id.data else None
                hostel_name = form.hostel_name.data if form.hostel_name.data else None
                room_number = form.room_number.data.strip() if form.room_number.data else None
                staff_id = None
            else:
                student_id = None
                hostel_name = None
                room_number = None
                staff_id = form.staff_id.data.strip() if form.staff_id.data else None

            # 1. Create Patient
            patient = Patient(
                patient_name=form.patient_name.data.strip(),
                age=form.age.data,
                gender=form.gender.data,
                designation=designation,
                student_id=student_id,
                hostel_name=hostel_name,
                room_number=room_number,
                staff_id=staff_id,
                medical_history=form.medical_history.data.strip() if form.medical_history.data else None
            )
            db.session.add(patient)
            db.session.flush()  # Generate patient.patient_id

            log_details = f'Created patient: {patient.patient_name}'

            # 2. Automatically Create Visit
            visit_date = date.today()
            serial = get_next_serial_number(visit_date)
            
            med_info = form.medical_history.data.strip() if form.medical_history.data else 'Registered new patient.'
            visit = PatientVisit(
                patient_id=patient.patient_id,
                visit_date=visit_date,
                visit_time=datetime.now().time().replace(second=0, microsecond=0),
                serial_number=serial,
                complaint=med_info,
                diagnosis=med_info,
                treatment=f"Prescribed {qty} of {medicine.medicine_name}",
                doctor_id=current_user.doctor_id,
            )
            db.session.add(visit)
            db.session.flush()  # Generate visit.visit_id
            
            log_details += f' and logged Visit #{visit.visit_id}'

            # 3. Create Prescription
            prescription = Prescription(
                visit_id=visit.visit_id,
                notes="Initial prescription on patient registration.",
            )
            db.session.add(prescription)
            db.session.flush()  # Generate prescription.prescription_id

            # 4. Deduct Medicine Stock
            deduct_for_prescription(medicine, qty, prescription.prescription_id)

            # 5. Create Prescription Item
            item = PrescriptionItem(
                prescription_id=prescription.prescription_id,
                medicine_id=medicine.medicine_id,
                dosage="As prescribed",
                frequency="Once daily",
                duration="Until finished",
                quantity=qty,
                instructions="Take as directed by physician",
            )
            db.session.add(item)
            
            log_details += f' with Prescription #{prescription.prescription_id} (Deducted {qty} units of {medicine.medicine_name})'

            # Commit the entire transaction
            db.session.commit()

            # Audit logging
            log_audit(
                action=AuditLog.ACTION_PATIENT_CREATE,
                module=AuditLog.MODULE_PATIENTS,
                record_id=patient.patient_id,
                details=log_details
            )
            log_audit(
                action=AuditLog.ACTION_VISIT_CREATE,
                module=AuditLog.MODULE_VISITS,
                record_id=visit.visit_id,
                details=f'Immediate visit registered during patient registration for {patient.patient_name}'
            )
            log_audit(
                action=AuditLog.ACTION_PRESCRIPTION_CREATE,
                module=AuditLog.MODULE_PRESCRIPTIONS,
                record_id=prescription.prescription_id,
                details=f'Immediate prescription registered during patient registration for {patient.patient_name}'
            )

            flash(f'Patient "{patient.patient_name}" has been registered successfully with medicine prescription.', 'success')
            return redirect(url_for('patients.view_patient', id=patient.patient_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating patient: {str(e)}', 'danger')

    return render_template('patients/add.html', form=form, medicines=medicines)


# ---------------------------------------------------------------------------
# Edit patient
# ---------------------------------------------------------------------------

@patients_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_patient(id):
    """Edit an existing patient's information and medication details with stock reconciliation."""
    from app.forms.patient_forms import EditPatientForm
    from app.models.medicine import Medicine
    from app.models.visit import PatientVisit
    from app.models.prescription import Prescription, PrescriptionItem
    from app.extensions import db
    import json
    
    patient = get_patient_by_id(id)
    if not patient:
        flash('Patient not found.', 'warning')
        return redirect(url_for('patients.list_patients'))

    form = EditPatientForm(obj=patient)
    
    # Get all active medicines for selection
    medicines = Medicine.query.filter(Medicine.available_balance >= 0).order_by(Medicine.medicine_name).all()

    # Get patient's latest visit and prescription
    latest_visit = PatientVisit.query.filter_by(patient_id=patient.patient_id).order_by(PatientVisit.visit_date.desc(), PatientVisit.visit_time.desc()).first()
    prescription = None
    
    if latest_visit:
        prescription = Prescription.query.filter_by(visit_id=latest_visit.visit_id).first()
        if not prescription:
            try:
                prescription = Prescription(visit_id=latest_visit.visit_id, notes="Prescription during edit.")
                db.session.add(prescription)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash(f'Error initializing patient prescription: {str(e)}', 'danger')
    else:
        # Create a default visit and prescription if none exists
        from datetime import date, datetime
        from app.services.patient_service import get_next_serial_number
        try:
            visit_date = date.today()
            serial = get_next_serial_number(visit_date)
            latest_visit = PatientVisit(
                patient_id=patient.patient_id,
                visit_date=visit_date,
                visit_time=datetime.now().time().replace(second=0, microsecond=0),
                serial_number=serial,
                complaint=patient.medical_history or "Initial patient edit.",
                diagnosis=patient.medical_history or "Initial patient edit.",
                treatment="Initial prescription",
                doctor_id=current_user.doctor_id
            )
            db.session.add(latest_visit)
            db.session.flush()
            
            prescription = Prescription(visit_id=latest_visit.visit_id, notes="Prescription during edit.")
            db.session.add(prescription)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Error initializing patient visit and prescription: {str(e)}', 'danger')

    # Re-fetch prescription inside session context
    if latest_visit and not prescription:
        prescription = Prescription.query.filter_by(visit_id=latest_visit.visit_id).first()

    if request.method == 'GET':
        existing_items = []
        if prescription:
            for item in prescription.items:
                existing_items.append({
                    'medicine_id': item.medicine_id,
                    'medicine_name': item.medicine.medicine_name,
                    'quantity': item.quantity,
                    'dosage': item.dosage or '',
                    'frequency': item.frequency or '',
                    'duration': item.duration or '',
                    'instructions': item.instructions or ''
                })
        form.items_json.data = json.dumps(existing_items)

    if form.validate_on_submit():
        # Server-side validation for designation conditional fields
        designation = form.designation.data.strip() if form.designation.data else 'Other'
        if designation == 'Student' and not form.student_id.data:
            form.student_id.errors.append('Student ID Number is mandatory for Student designation.')
            return render_template('patients/edit.html', form=form, patient=patient, medicines=medicines)

        # Parse items from items_json
        try:
            items_data = json.loads(form.items_json.data or '[]')
        except (json.JSONDecodeError, TypeError):
            flash('Invalid medication items data.', 'danger')
            return render_template('patients/edit.html', form=form, patient=patient, medicines=medicines)

        # Build map of new items by medicine_id
        new_items_map = {}
        for idx, item in enumerate(items_data, 1):
            med_id = int(item.get('medicine_id', 0))
            if med_id == 0:
                continue
            try:
                qty = int(item.get('quantity', 0))
            except (TypeError, ValueError):
                flash(f"Invalid quantity format at row {idx}.", "danger")
                return render_template('patients/edit.html', form=form, patient=patient, medicines=medicines)
                
            if qty < 1:
                flash(f"Quantity for row {idx} must be at least 1.", "danger")
                return render_template('patients/edit.html', form=form, patient=patient, medicines=medicines)
            new_items_map[med_id] = {
                'quantity': qty,
                'dosage': item.get('dosage', ''),
                'frequency': item.get('frequency', ''),
                'duration': item.get('duration', ''),
                'instructions': item.get('instructions', '')
            }

        # Load all medicines needed for validation/update to avoid extra queries
        all_med_ids = set(new_items_map.keys())
        if prescription:
            for item in prescription.items:
                all_med_ids.add(item.medicine_id)
        
        medicines_db = {m.medicine_id: m for m in Medicine.query.filter(Medicine.medicine_id.in_(all_med_ids)).all()}

        # 1. Validate stock limits for all changes before committing anything
        for med_id, item_info in new_items_map.items():
            medicine = medicines_db.get(med_id)
            if not medicine:
                flash("One of the selected medicines does not exist.", "danger")
                return render_template('patients/edit.html', form=form, patient=patient, medicines=medicines)
            
            # Find if this item already exists in prescription
            existing_item = next((i for i in prescription.items if i.medicine_id == med_id), None) if prescription else None
            old_qty = existing_item.quantity if existing_item else 0
            new_qty = item_info['quantity']
            
            if new_qty > old_qty:
                diff = new_qty - old_qty
                if medicine.available_balance < diff:
                    flash(f"Insufficient stock for {medicine.medicine_name}. Only {medicine.available_balance} additional units available.", "danger")
                    return render_template('patients/edit.html', form=form, patient=patient, medicines=medicines)
                if medicine.is_expired:
                    flash(f"Medicine {medicine.medicine_name} is expired and cannot be prescribed.", "danger")
                    return render_template('patients/edit.html', form=form, patient=patient, medicines=medicines)

        # 2. Perform the changes atomically in a transaction block
        try:
            # Update Patient Demographics
            update_patient(patient, form)
            
            if prescription:
                from app.models.stock_log import MedicineStockLog
                
                # Keep track of items to delete
                items_to_delete = []
                
                # Update or delete existing items
                for existing_item in list(prescription.items):
                    med_id = existing_item.medicine_id
                    medicine = medicines_db[med_id]
                    
                    if med_id not in new_items_map:
                        # The item has been removed
                        restore_qty = existing_item.quantity
                        medicine.available_balance += restore_qty
                        medicine.stock_deducted -= restore_qty
                        
                        # Log stock restoration
                        log = MedicineStockLog(
                            medicine_id=med_id,
                            action_type=MedicineStockLog.ACTION_ADDED,
                            quantity=restore_qty,
                            remarks=f"Restored from deleted item in Prescription #{prescription.prescription_id} edit"
                        )
                        db.session.add(log)
                        items_to_delete.append(existing_item)
                    else:
                        # Item exists, reconcile quantity
                        item_info = new_items_map[med_id]
                        old_qty = existing_item.quantity
                        new_qty = item_info['quantity']
                        
                        if new_qty != old_qty:
                            if new_qty > old_qty:
                                diff = new_qty - old_qty
                                medicine.available_balance -= diff
                                medicine.stock_deducted += diff
                                
                                log = MedicineStockLog(
                                    medicine_id=med_id,
                                    action_type=MedicineStockLog.ACTION_PRESCRIPTION,
                                    quantity=diff,
                                    remarks=f"Additional quantity in Prescription #{prescription.prescription_id} edit"
                                )
                                db.session.add(log)
                            else:
                                diff = old_qty - new_qty
                                medicine.available_balance += diff
                                medicine.stock_deducted -= diff
                                
                                log = MedicineStockLog(
                                    medicine_id=med_id,
                                    action_type=MedicineStockLog.ACTION_ADDED,
                                    quantity=diff,
                                    remarks=f"Restored reduced quantity from Prescription #{prescription.prescription_id} edit"
                                )
                                db.session.add(log)
                        
                        # Update item attributes
                        existing_item.quantity = new_qty
                        existing_item.dosage = item_info['dosage']
                        existing_item.frequency = item_info['frequency']
                        existing_item.duration = item_info['duration']
                        existing_item.instructions = item_info['instructions']

                # Delete marked items
                for item in items_to_delete:
                    db.session.delete(item)

                # Add completely new items
                for med_id, item_info in new_items_map.items():
                    existing_item = next((i for i in prescription.items if i.medicine_id == med_id), None)
                    if not existing_item:
                        medicine = medicines_db[med_id]
                        qty = item_info['quantity']
                        
                        medicine.available_balance -= qty
                        medicine.stock_deducted += qty
                        
                        log = MedicineStockLog(
                            medicine_id=med_id,
                            action_type=MedicineStockLog.ACTION_PRESCRIPTION,
                            quantity=qty,
                            remarks=f"Prescribed in Prescription #{prescription.prescription_id} edit"
                        )
                        db.session.add(log)
                        
                        new_item = PrescriptionItem(
                            prescription_id=prescription.prescription_id,
                            medicine_id=med_id,
                            dosage=item_info['dosage'],
                            frequency=item_info['frequency'],
                            duration=item_info['duration'],
                            quantity=qty,
                            instructions=item_info['instructions']
                        )
                        db.session.add(new_item)

            # Commit the transaction
            db.session.commit()

            log_audit(
                action=AuditLog.ACTION_PATIENT_EDIT,
                module=AuditLog.MODULE_PATIENTS,
                record_id=patient.patient_id,
                details=f'Updated patient demographics and reconciled medication details for {patient.patient_name}'
            )
            flash(f'Patient "{patient.patient_name}" and medication details have been updated successfully.', 'success')
            return redirect(url_for('patients.view_patient', id=patient.patient_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating patient and medication details: {str(e)}', 'danger')

    return render_template('patients/edit.html', form=form, patient=patient, medicines=medicines)


# ---------------------------------------------------------------------------
# View patient
# ---------------------------------------------------------------------------

@patients_bp.route('/<int:id>')
@login_required
def view_patient(id):
    """View patient details and visit history."""
    patient = get_patient_by_id(id)
    if not patient:
        flash('Patient not found.', 'warning')
        return redirect(url_for('patients.list_patients'))

    page = request.args.get('page', 1, type=int)
    visits_pagination = get_patient_visits(patient.patient_id, page=page, per_page=10)

    return render_template(
        'patients/view.html',
        patient=patient,
        visits=visits_pagination.items,
        pagination=visits_pagination,
    )


# ---------------------------------------------------------------------------
# Advanced search
# ---------------------------------------------------------------------------

@patients_bp.route('/search')
@login_required
def search():
    """Advanced multi-filter search page."""
    filters = {
        'patient_name': request.args.get('patient_name', ''),
        'diagnosis': request.args.get('diagnosis', ''),
        'student_id': request.args.get('student_id', ''),
        'staff_id': request.args.get('staff_id', ''),
        'hostel': request.args.get('hostel', ''),
        'gender': request.args.get('gender', ''),
        'designation': request.args.get('designation', ''),
        'date_from': request.args.get('date_from', ''),
        'date_to': request.args.get('date_to', ''),
    }

    # Check if any filter is set
    has_filters = any(v for v in filters.values())

    page = request.args.get('page', 1, type=int)
    pagination = None
    results = []

    if has_filters:
        pagination = advanced_search(filters, page=page, per_page=25)
        results = pagination.items

    return render_template(
        'patients/search.html',
        filters=filters,
        results=results,
        pagination=pagination,
        has_filters=has_filters,
        hostel_choices=HOSTEL_CHOICES,
        gender_choices=GENDER_CHOICES,
        designation_choices=DESIGNATION_CHOICES,
    )


# ---------------------------------------------------------------------------
# API: Patient autocomplete (for AJAX)
# ---------------------------------------------------------------------------

@patients_bp.route('/api/autocomplete')
@login_required
def autocomplete():
    """JSON endpoint for patient name autocomplete."""
    term = request.args.get('term', '')
    results = search_patients_autocomplete(term, limit=10)
    return jsonify(results)
