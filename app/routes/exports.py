"""Export routes – download Excel reports."""
from datetime import datetime

from flask import Blueprint, render_template, send_file, request, flash, redirect, url_for
from flask_login import login_required, current_user

from app.models.audit_log import AuditLog
from app.services.audit_service import log_audit
from app.services.export_service import (
    export_patients, export_visits, export_medicines,
    export_expiry_report, export_audit_logs,
)

exports_bp = Blueprint('exports', __name__, url_prefix='/exports')


@exports_bp.route('/')
@login_required
def index():
    """Export center – choose what to download."""
    return render_template('exports/index.html')


@exports_bp.route('/patients')
@login_required
def download_patients():
    """Download patients Excel file."""
    output = export_patients()
    log_audit(AuditLog.ACTION_EXPORT, AuditLog.MODULE_EXPORT,
              details='Exported Patient List')
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'patients_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
    )


@exports_bp.route('/visits')
@login_required
def download_visits():
    """Download visit history Excel file."""
    date_from = request.args.get('from')
    date_to = request.args.get('to')

    df = None
    df_from = None
    if date_from:
        try:
            df_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        except ValueError:
            pass
    df_to = None
    if date_to:
        try:
            df_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        except ValueError:
            pass

    output = export_visits(date_from=df_from, date_to=df_to)
    log_audit(AuditLog.ACTION_EXPORT, AuditLog.MODULE_EXPORT,
              details='Exported Visit History')
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'visits_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
    )


@exports_bp.route('/medicines')
@login_required
def download_medicines():
    """Download medicine inventory Excel file."""
    output = export_medicines()
    log_audit(AuditLog.ACTION_EXPORT, AuditLog.MODULE_EXPORT,
              details='Exported Medicine Inventory')
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'medicines_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
    )


@exports_bp.route('/expiry')
@login_required
def download_expiry():
    """Download expiry report Excel file."""
    output = export_expiry_report()
    log_audit(AuditLog.ACTION_EXPORT, AuditLog.MODULE_EXPORT,
              details='Exported Expiry Report')
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'expiry_report_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
    )


@exports_bp.route('/audit')
@login_required
def download_audit():
    """Download audit log Excel file."""
    output = export_audit_logs()
    log_audit(AuditLog.ACTION_EXPORT, AuditLog.MODULE_EXPORT,
              details='Exported Audit Logs')
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'audit_logs_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
    )
