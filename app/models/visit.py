from app.extensions import db
from datetime import datetime, date, time


class PatientVisit(db.Model):
    """Patient visit record model."""

    __tablename__ = 'patient_visits'
    __table_args__ = (
        db.Index('idx_visit_date', 'visit_date'),
        db.Index('idx_diagnosis', 'diagnosis', mysql_length=255),
    )

    visit_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(
        db.Integer, db.ForeignKey('patients.patient_id'), nullable=False
    )
    visit_date = db.Column(db.Date, nullable=False, default=date.today)
    visit_time = db.Column(db.Time, nullable=False, default=lambda: datetime.now().time())
    serial_number = db.Column(db.Integer)
    complaint = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    treatment = db.Column(db.Text)
    doctor_id = db.Column(
        db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    prescriptions = db.relationship('Prescription', backref='visit', lazy='dynamic')

    @property
    def diagnosis_short(self):
        """Return truncated diagnosis for table display."""
        if self.diagnosis and len(self.diagnosis) > 60:
            return self.diagnosis[:60] + '...'
        return self.diagnosis or ''

    def __repr__(self):
        return f'<PatientVisit {self.visit_id} - {self.visit_date}>'
