from app.extensions import db
from datetime import datetime


class MedicineStockLog(db.Model):
    """Audit trail for all medicine stock changes."""

    __tablename__ = 'medicine_stock_logs'

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    medicine_id = db.Column(
        db.Integer, db.ForeignKey('medicines.medicine_id'), nullable=False
    )
    action_type = db.Column(db.String(50), nullable=False)  # ADDED, DEDUCTED, ADJUSTED
    quantity = db.Column(db.Integer, nullable=False)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Action type constants
    ACTION_ADDED = 'ADDED'
    ACTION_DEDUCTED = 'DEDUCTED'
    ACTION_ADJUSTED = 'ADJUSTED'
    ACTION_PRESCRIPTION = 'PRESCRIPTION_DEDUCTION'

    def __repr__(self):
        return f'<StockLog {self.log_id}: {self.action_type} {self.quantity}>'
