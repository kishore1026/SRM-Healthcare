from app.extensions import db
from datetime import datetime


class Patient(db.Model):
    """Patient model for storing patient demographics."""

    __tablename__ = 'patients'

    patient_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_name = db.Column(db.String(100), nullable=False, index=True)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.Enum('Male', 'Female', 'Other', name='gender_enum'), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(50), index=True)
    hostel_name = db.Column(db.String(100))
    room_number = db.Column(db.String(20))
    staff_id = db.Column(db.String(50), index=True)
    medical_history = db.Column(db.Text)
    drug_allergy = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    visits = db.relationship(
        'PatientVisit', backref='patient', lazy='dynamic',
        order_by='PatientVisit.visit_date.desc()'
    )

    @property
    def display_id(self):
        """Return student_id or staff_id based on designation."""
        if self.designation == 'Student':
            return self.student_id
        return self.staff_id

    @property
    def total_visits(self):
        return self.visits.count()

    def __repr__(self):
        return f'<Patient {self.patient_name}>'
