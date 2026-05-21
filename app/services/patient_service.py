from app.extensions import db
from app.models.patient import Patient
from app.models.visit import PatientVisit
from app.models.doctor import Doctor
from sqlalchemy import or_, and_, func, cast, Date
from datetime import date, datetime


# ---------------------------------------------------------------------------
# Patient CRUD
# ---------------------------------------------------------------------------

def create_patient(form):
    """Create a new patient from form data and return the patient object."""
    designation = form.designation.data.strip() if form.designation.data else 'Other'
    student_id = form.student_id.data.strip() if designation == 'Student' and form.student_id.data else None
    hostel_name = form.hostel_name.data if designation == 'Student' and form.hostel_name.data else None
    room_number = form.room_number.data.strip() if designation == 'Student' and form.room_number.data else None
    staff_id = form.staff_id.data.strip() if designation in ('Staff', 'Other') and form.staff_id.data else None

    patient = Patient(
        patient_name=form.patient_name.data.strip(),
        age=form.age.data,
        gender=form.gender.data,
        designation=designation,
        student_id=student_id,
        hostel_name=hostel_name,
        room_number=room_number,
        staff_id=staff_id,
        medical_history=form.medical_history.data.strip() if form.medical_history.data else None,
    )
    db.session.add(patient)
    db.session.commit()
    return patient


def update_patient(patient, form):
    """Update an existing patient with form data."""
    patient.patient_name = form.patient_name.data.strip()
    patient.age = form.age.data
    patient.gender = form.gender.data
    
    designation = form.designation.data.strip() if form.designation.data else 'Other'
    patient.designation = designation
    
    if designation == 'Student':
        patient.student_id = form.student_id.data.strip() if form.student_id.data else None
        patient.hostel_name = form.hostel_name.data if form.hostel_name.data else None
        patient.room_number = form.room_number.data.strip() if form.room_number.data else None
        patient.staff_id = None
    else:
        patient.student_id = None
        patient.hostel_name = None
        patient.room_number = None
        patient.staff_id = form.staff_id.data.strip() if form.staff_id.data else None
        
    patient.medical_history = form.medical_history.data.strip() if form.medical_history.data else None
    db.session.commit()
    return patient


def get_patient_by_id(patient_id):
    """Get patient by primary key or return None."""
    return Patient.query.get(patient_id)


def get_patients_paginated(page=1, per_page=25, search_query=None):
    """Return paginated patient list, optionally filtered by a quick-search term."""
    query = Patient.query

    if search_query:
        term = f'%{search_query}%'
        query = query.filter(
            or_(
                Patient.patient_name.ilike(term),
                Patient.student_id.ilike(term),
                Patient.staff_id.ilike(term),
            )
        )

    return query.order_by(Patient.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )


# ---------------------------------------------------------------------------
# Visit operations
# ---------------------------------------------------------------------------

def get_next_serial_number(visit_date):
    """Get the next serial number for a given date.
    
    Serial numbers reset daily and auto-increment for each new visit.
    """
    max_serial = db.session.query(func.max(PatientVisit.serial_number)).filter(
        PatientVisit.visit_date == visit_date
    ).scalar()
    return (max_serial or 0) + 1


def create_visit(form, patient_id):
    """Create a new visit from form data."""
    serial = get_next_serial_number(form.visit_date.data)
    visit = PatientVisit(
        patient_id=patient_id,
        visit_date=form.visit_date.data,
        visit_time=form.visit_time.data,
        serial_number=serial,
        complaint=form.complaint.data.strip() if form.complaint.data else None,
        diagnosis=form.diagnosis.data.strip() if form.diagnosis.data else None,
        treatment=form.treatment.data.strip() if form.treatment.data else None,
        doctor_id=form.doctor_id.data,
    )
    db.session.add(visit)
    db.session.commit()
    return visit


def get_visit_by_id(visit_id):
    """Get a visit by primary key or return None."""
    return PatientVisit.query.get(visit_id)


def get_patient_visits(patient_id, page=1, per_page=10):
    """Return paginated visits for a specific patient."""
    return PatientVisit.query.filter_by(patient_id=patient_id).order_by(
        PatientVisit.visit_date.desc(), PatientVisit.visit_time.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)


# ---------------------------------------------------------------------------
# Advanced search
# ---------------------------------------------------------------------------

def advanced_search(filters, page=1, per_page=25):
    """Execute advanced multi-filter search combining patients and visits.

    Args:
        filters: dict with optional keys:
            patient_name, diagnosis, student_id, staff_id,
            hostel, gender, designation, date_from, date_to
        page: page number
        per_page: results per page

    Returns:
        SQLAlchemy pagination object of PatientVisit rows joined to Patient.
    """
    query = PatientVisit.query.join(Patient).join(Doctor)

    # Patient name filter
    name = filters.get('patient_name', '').strip()
    if name:
        query = query.filter(Patient.patient_name.ilike(f'%{name}%'))

    # Diagnosis filter
    diagnosis = filters.get('diagnosis', '').strip()
    if diagnosis:
        query = query.filter(PatientVisit.diagnosis.ilike(f'%{diagnosis}%'))

    # Student ID filter
    sid = filters.get('student_id', '').strip()
    if sid:
        query = query.filter(Patient.student_id.ilike(f'%{sid}%'))

    # Staff ID filter
    stid = filters.get('staff_id', '').strip()
    if stid:
        query = query.filter(Patient.staff_id.ilike(f'%{stid}%'))

    # Hostel filter
    hostel = filters.get('hostel', '').strip()
    if hostel:
        query = query.filter(Patient.hostel_name == hostel)

    # Gender filter
    gender = filters.get('gender', '').strip()
    if gender:
        query = query.filter(Patient.gender == gender)

    # Designation filter
    designation = filters.get('designation', '').strip()
    if designation:
        query = query.filter(Patient.designation == designation)

    # Date range filters
    date_from = filters.get('date_from')
    if date_from:
        if isinstance(date_from, str) and date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            except ValueError:
                date_from = None
        if date_from:
            query = query.filter(PatientVisit.visit_date >= date_from)

    date_to = filters.get('date_to')
    if date_to:
        if isinstance(date_to, str) and date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            except ValueError:
                date_to = None
        if date_to:
            query = query.filter(PatientVisit.visit_date <= date_to)

    return query.order_by(
        PatientVisit.visit_date.desc(),
        PatientVisit.visit_time.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)


# ---------------------------------------------------------------------------
# Statistics helpers
# ---------------------------------------------------------------------------

def get_patient_stats():
    """Return basic patient statistics for dashboards."""
    total_patients = Patient.query.count()
    total_visits_today = PatientVisit.query.filter(
        PatientVisit.visit_date == date.today()
    ).count()
    total_students = Patient.query.filter(Patient.designation == 'Student').count()
    total_staff = Patient.query.filter(Patient.designation == 'Staff').count()

    return {
        'total_patients': total_patients,
        'total_visits_today': total_visits_today,
        'total_students': total_students,
        'total_staff': total_staff,
    }


def search_patients_autocomplete(term, limit=10):
    """Return a list of patients matching a search term (for AJAX autocomplete)."""
    if not term or len(term) < 2:
        return []

    like_term = f'%{term}%'
    patients = Patient.query.filter(
        or_(
            Patient.patient_name.ilike(like_term),
            Patient.student_id.ilike(like_term),
            Patient.staff_id.ilike(like_term),
        )
    ).limit(limit).all()

    return [
        {
            'id': p.patient_id,
            'name': p.patient_name,
            'display_id': p.display_id or '',
            'designation': p.designation,
        }
        for p in patients
    ]
