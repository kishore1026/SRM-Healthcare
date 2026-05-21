"""Medicine service – stock operations, validation, and alert queries."""
from datetime import date, timedelta
from flask import current_app
from app.extensions import db
from app.models.medicine import Medicine
from app.models.stock_log import MedicineStockLog


# ---------------------------------------------------------------------------
# Stock Operations
# ---------------------------------------------------------------------------

def add_stock(medicine, quantity, remarks=None):
    """Add stock to a medicine and log the change."""
    medicine.stock_added += quantity
    medicine.available_balance += quantity

    log = MedicineStockLog(
        medicine_id=medicine.medicine_id,
        action_type=MedicineStockLog.ACTION_ADDED,
        quantity=quantity,
        remarks=remarks or f'Added {quantity} units',
    )
    db.session.add(log)
    db.session.commit()
    return medicine


def deduct_stock(medicine, quantity, remarks=None):
    """Deduct stock from a medicine and log the change.

    Returns:
        Medicine on success, raises ValueError on failure.
    """
    if not medicine.can_issue(quantity):
        raise ValueError(
            f"Cannot issue {quantity} of {medicine.medicine_name}. "
            f"Available: {medicine.available_balance}, Expired: {medicine.is_expired}"
        )

    medicine.stock_deducted += quantity
    medicine.available_balance -= quantity

    log = MedicineStockLog(
        medicine_id=medicine.medicine_id,
        action_type=MedicineStockLog.ACTION_DEDUCTED,
        quantity=quantity,
        remarks=remarks or f'Deducted {quantity} units',
    )
    db.session.add(log)
    return medicine  # caller commits the session


def deduct_for_prescription(medicine, quantity, prescription_id):
    """Deduct stock specifically for a prescription."""
    if not medicine.can_issue(quantity):
        raise ValueError(
            f"Cannot issue {quantity} of {medicine.medicine_name}. "
            f"Available: {medicine.available_balance}"
        )

    medicine.stock_deducted += quantity
    medicine.available_balance -= quantity

    log = MedicineStockLog(
        medicine_id=medicine.medicine_id,
        action_type=MedicineStockLog.ACTION_PRESCRIPTION,
        quantity=quantity,
        remarks=f'Prescription #{prescription_id}',
    )
    db.session.add(log)
    return medicine


# ---------------------------------------------------------------------------
# Alert Queries
# ---------------------------------------------------------------------------

def get_low_stock_medicines():
    """Return medicines with stock at or below the low-stock threshold."""
    threshold = current_app.config.get('LOW_STOCK_THRESHOLD', 10)
    return Medicine.query.filter(
        Medicine.available_balance > 0,
        Medicine.available_balance <= threshold
    ).order_by(Medicine.available_balance.asc()).all()


def get_expiring_medicines():
    """Return non-expired medicines expiring within the warning window."""
    threshold = current_app.config.get('EXPIRY_WARNING_DAYS', 30)
    cutoff = date.today() + timedelta(days=threshold)
    return Medicine.query.filter(
        Medicine.expiry_date > date.today(),
        Medicine.expiry_date <= cutoff
    ).order_by(Medicine.expiry_date.asc()).all()


def get_expired_medicines():
    """Return medicines that have already expired."""
    return Medicine.query.filter(
        Medicine.expiry_date < date.today()
    ).order_by(Medicine.expiry_date.asc()).all()


def get_out_of_stock_medicines():
    """Return medicines with zero balance."""
    return Medicine.query.filter(
        Medicine.available_balance <= 0
    ).order_by(Medicine.medicine_name.asc()).all()


# ---------------------------------------------------------------------------
# Search & Validation
# ---------------------------------------------------------------------------

def search_medicines(query_text, limit=20):
    """Search medicines by name for autocomplete."""
    return Medicine.query.filter(
        Medicine.medicine_name.ilike(f'%{query_text}%')
    ).order_by(Medicine.medicine_name).limit(limit).all()


def validate_prescription_items(items):
    """Validate a list of prescription item dicts before saving.

    Args:
        items: list of dicts with keys: medicine_id, quantity, ...

    Returns:
        (valid, errors) – valid is bool, errors is list of strings
    """
    errors = []
    if not items:
        return False, ['At least one medicine item is required.']

    for idx, item in enumerate(items, 1):
        med_id = item.get('medicine_id')
        qty = item.get('quantity', 0)

        if not med_id:
            errors.append(f'Row {idx}: Medicine is required.')
            continue

        med = Medicine.query.get(med_id)
        if not med:
            errors.append(f'Row {idx}: Medicine not found.')
            continue

        if med.is_expired:
            errors.append(f'Row {idx}: {med.medicine_name} is expired.')
            continue

        try:
            qty = int(qty)
        except (TypeError, ValueError):
            errors.append(f'Row {idx}: Invalid quantity.')
            continue

        if qty < 1:
            errors.append(f'Row {idx}: Quantity must be at least 1.')
        elif qty > med.available_balance:
            errors.append(
                f'Row {idx}: Insufficient stock for {med.medicine_name}. '
                f'Requested: {qty}, Available: {med.available_balance}'
            )

    return len(errors) == 0, errors


def get_alert_counts():
    """Return a dict with counts of each alert type."""
    threshold = current_app.config.get('LOW_STOCK_THRESHOLD', 10)
    expiry_days = current_app.config.get('EXPIRY_WARNING_DAYS', 30)
    cutoff = date.today() + timedelta(days=expiry_days)

    low_stock = Medicine.query.filter(
        Medicine.available_balance > 0,
        Medicine.available_balance <= threshold
    ).count()

    expiring = Medicine.query.filter(
        Medicine.expiry_date > date.today(),
        Medicine.expiry_date <= cutoff
    ).count()

    expired = Medicine.query.filter(
        Medicine.expiry_date < date.today()
    ).count()

    out_of_stock = Medicine.query.filter(
        Medicine.available_balance <= 0
    ).count()

    return {
        'low_stock': low_stock,
        'expiring': expiring,
        'expired': expired,
        'out_of_stock': out_of_stock,
        'total_alerts': low_stock + expiring + expired,
    }
