from app.extensions import db
from datetime import datetime, date, timedelta
from flask import current_app


class Medicine(db.Model):
    """Medicine inventory model with stock tracking."""

    __tablename__ = 'medicines'
    __table_args__ = (
        db.Index('idx_medicine_name', 'medicine_name'),
        db.Index('idx_expiry_date', 'expiry_date'),
    )

    medicine_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    medicine_name = db.Column(db.String(200), nullable=False)
    drug_type = db.Column(
        db.Enum(
            'Tablets', 'Capsules', 'Injections',
            'Eye Drops', 'Ear Drops', 'Ointments',
            name='drug_type_enum'
        ),
        nullable=False
    )
    batch_number = db.Column(db.String(50))
    expiry_date = db.Column(db.Date, nullable=False)
    stock_added = db.Column(db.Integer, nullable=False, default=0)
    stock_deducted = db.Column(db.Integer, nullable=False, default=0)
    available_balance = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    stock_logs = db.relationship('MedicineStockLog', backref='medicine', lazy='dynamic')

    @property
    def is_expired(self):
        return self.expiry_date < date.today()

    @property
    def is_expiring_soon(self):
        threshold = current_app.config.get('EXPIRY_WARNING_DAYS', 30)
        return (
            not self.is_expired
            and self.expiry_date <= date.today() + timedelta(days=threshold)
        )

    @property
    def is_low_stock(self):
        threshold = current_app.config.get('LOW_STOCK_THRESHOLD', 10)
        return self.available_balance > 0 and self.available_balance <= threshold

    @property
    def is_out_of_stock(self):
        return self.available_balance <= 0

    @property
    def stock_status(self):
        """Return stock status string and color class."""
        if self.is_out_of_stock:
            return 'Out of Stock', 'danger'
        elif self.is_low_stock:
            return 'Low Stock', 'warning'
        return 'Safe', 'success'

    @property
    def expiry_status(self):
        """Return expiry status string and color class."""
        if self.is_expired:
            return 'Expired', 'danger'
        elif self.is_expiring_soon:
            return 'Expiring Soon', 'warning'
        return 'Valid', 'success'

    @property
    def days_until_expiry(self):
        delta = self.expiry_date - date.today()
        return delta.days

    def can_issue(self, quantity):
        """Check if medicine can be issued."""
        return (
            not self.is_expired
            and self.available_balance >= quantity
        )

    def __repr__(self):
        return f'<Medicine {self.medicine_name}>'
