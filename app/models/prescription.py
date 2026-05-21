from app.extensions import db
from datetime import datetime


class Prescription(db.Model):
    """Prescription header linked to a patient visit."""

    __tablename__ = 'prescriptions'

    prescription_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    visit_id = db.Column(
        db.Integer, db.ForeignKey('patient_visits.visit_id'), nullable=False
    )
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship(
        'PrescriptionItem', backref='prescription', lazy='joined',
        cascade='all, delete-orphan'
    )

    @property
    def total_items(self):
        return len(self.items)

    def __repr__(self):
        return f'<Prescription {self.prescription_id}>'


class PrescriptionItem(db.Model):
    """Individual medicine item within a prescription."""

    __tablename__ = 'prescription_items'

    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prescription_id = db.Column(
        db.Integer, db.ForeignKey('prescriptions.prescription_id'), nullable=False
    )
    medicine_id = db.Column(
        db.Integer, db.ForeignKey('medicines.medicine_id', use_alter=True, name='fk_pi_medicine'),
        nullable=False
    )
    dosage = db.Column(db.String(100))
    frequency = db.Column(db.String(100))
    duration = db.Column(db.String(100))
    quantity = db.Column(db.Integer, nullable=False, default=1)
    instructions = db.Column(db.Text)

    # Relationships
    medicine = db.relationship('Medicine', backref='prescription_items')

    def __repr__(self):
        return f'<PrescriptionItem {self.item_id}>'
