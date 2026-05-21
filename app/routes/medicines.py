"""Medicine routes – CRUD, stock management, and alerts."""
from datetime import date

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models.medicine import Medicine
from app.models.audit_log import AuditLog
from app.forms.medicine_forms import MedicineForm, AddStockForm
from app.services.audit_service import log_audit
from app.services.medicine_service import (
    add_stock, get_low_stock_medicines, get_expiring_medicines,
    get_expired_medicines, get_alert_counts,
)

medicines_bp = Blueprint('medicines', __name__, url_prefix='/medicines')


@medicines_bp.route('/')
@login_required
def index():
    """Redirect to medicine list (alias for sidebar link)."""
    return redirect(url_for('medicines.list_medicines'))


@medicines_bp.route('/list')
@login_required
def list_medicines():
    """List all medicines with pagination and search."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()
    drug_type = request.args.get('type', '').strip()
    status = request.args.get('status', '').strip()

    query = Medicine.query

    if search:
        query = query.filter(Medicine.medicine_name.ilike(f'%{search}%'))
    if drug_type:
        query = query.filter(Medicine.drug_type == drug_type)
    if status == 'low':
        threshold = 10
        query = query.filter(Medicine.available_balance > 0,
                             Medicine.available_balance <= threshold)
    elif status == 'out':
        query = query.filter(Medicine.available_balance <= 0)
    elif status == 'expired':
        query = query.filter(Medicine.expiry_date < date.today())
    elif status == 'expiring':
        from datetime import timedelta
        cutoff = date.today() + timedelta(days=30)
        query = query.filter(Medicine.expiry_date > date.today(),
                             Medicine.expiry_date <= cutoff)

    medicines = query.order_by(Medicine.medicine_name)\
                     .paginate(page=page, per_page=25, error_out=False)

    alerts = get_alert_counts()

    return render_template('medicines/list.html',
                           medicines=medicines,
                           search=search,
                           drug_type=drug_type,
                           status=status,
                           alerts=alerts)


@medicines_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_medicine():
    """Add a new medicine to the inventory."""
    form = MedicineForm()

    if form.validate_on_submit():
        medicine = Medicine(
            medicine_name=form.medicine_name.data.strip(),
            drug_type=form.drug_type.data,
            batch_number=form.batch_number.data.strip() if form.batch_number.data else None,
            expiry_date=form.expiry_date.data,
            stock_added=form.stock_added.data,
            stock_deducted=0,
            available_balance=form.stock_added.data,
        )
        db.session.add(medicine)
        db.session.commit()

        log_audit(
            AuditLog.ACTION_MEDICINE_ADD,
            AuditLog.MODULE_MEDICINES,
            record_id=medicine.medicine_id,
            details=f'Added {medicine.medicine_name} with {medicine.stock_added} units'
        )

        flash(f'Medicine "{medicine.medicine_name}" added successfully!', 'success')
        return redirect(url_for('medicines.list_medicines'))

    return render_template('medicines/add.html', form=form)


@medicines_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_medicine(id):
    """Edit medicine details and optionally add stock."""
    medicine = Medicine.query.get_or_404(id)
    form = MedicineForm(obj=medicine)
    stock_form = AddStockForm()

    if request.method == 'POST':
        action = request.form.get('action', 'edit')

        if action == 'add_stock' and stock_form.validate():
            add_stock(
                medicine,
                stock_form.quantity.data,
                remarks=stock_form.remarks.data
            )
            if stock_form.batch_number.data:
                medicine.batch_number = stock_form.batch_number.data
            if stock_form.expiry_date.data:
                medicine.expiry_date = stock_form.expiry_date.data
            db.session.commit()

            log_audit(
                AuditLog.ACTION_STOCK_ADD,
                AuditLog.MODULE_MEDICINES,
                record_id=medicine.medicine_id,
                details=f'Added {stock_form.quantity.data} units to {medicine.medicine_name}'
            )

            flash(f'Stock updated! New balance: {medicine.available_balance}', 'success')
            return redirect(url_for('medicines.edit_medicine', id=id))

        elif action == 'edit' and form.validate():
            medicine.medicine_name = form.medicine_name.data.strip()
            medicine.drug_type = form.drug_type.data
            medicine.batch_number = form.batch_number.data.strip() if form.batch_number.data else None
            medicine.expiry_date = form.expiry_date.data
            db.session.commit()

            log_audit(
                AuditLog.ACTION_MEDICINE_EDIT,
                AuditLog.MODULE_MEDICINES,
                record_id=medicine.medicine_id,
                details=f'Edited {medicine.medicine_name}'
            )

            flash('Medicine details updated successfully!', 'success')
            return redirect(url_for('medicines.list_medicines'))

    # Pre-populate form for GET
    if request.method == 'GET':
        form.medicine_name.data = medicine.medicine_name
        form.drug_type.data = medicine.drug_type
        form.batch_number.data = medicine.batch_number
        form.expiry_date.data = medicine.expiry_date
        form.stock_added.data = medicine.stock_added

    return render_template('medicines/edit.html',
                           medicine=medicine,
                           form=form,
                           stock_form=stock_form)


@medicines_bp.route('/alerts')
@login_required
def alerts():
    """Medicine alerts dashboard – low stock, expiring, expired."""
    low_stock = get_low_stock_medicines()
    expiring = get_expiring_medicines()
    expired = get_expired_medicines()
    alert_counts = get_alert_counts()

    tab = request.args.get('tab', 'low_stock')

    return render_template('medicines/alerts.html',
                           low_stock=low_stock,
                           expiring=expiring,
                           expired=expired,
                           alert_counts=alert_counts,
                           active_tab=tab)


@medicines_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_medicine(id):
    """Delete a medicine from the inventory."""
    medicine = Medicine.query.get_or_404(id)
    medicine_name = medicine.medicine_name

    try:
        db.session.delete(medicine)
        db.session.commit()

        log_audit(
            AuditLog.ACTION_MEDICINE_DELETE,
            AuditLog.MODULE_MEDICINES,
            record_id=id,
            details=f'Deleted medicine {medicine_name}'
        )

        flash(f'Medicine "{medicine_name}" deleted successfully.', 'success')
    except Exception:
        db.session.rollback()
        flash(f'Cannot delete "{medicine_name}" because it is referenced in prescriptions.', 'danger')

    return redirect(url_for('medicines.list_medicines'))
