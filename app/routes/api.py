"""API routes – JSON endpoints for dashboard charts, medicine search, audit logs page."""
from datetime import datetime

from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required

from app.services.analytics_service import (
    get_summary_stats, get_disease_distribution,
    get_visit_trend, get_top_diseases,
)
from app.services.medicine_service import search_medicines, get_alert_counts
from app.services.audit_service import get_audit_logs
from app.models.audit_log import AuditLog

api_bp = Blueprint('api', __name__, url_prefix='/api')


# ---------------------------------------------------------------------------
# Dashboard Chart Data
# ---------------------------------------------------------------------------

@api_bp.route('/dashboard/stats')
@login_required
def dashboard_stats():
    """JSON: Summary card statistics."""
    period = request.args.get('period', 'overall')
    stats = get_summary_stats(period=period)
    return jsonify(stats)


@api_bp.route('/dashboard/disease-chart')
@login_required
def disease_chart():
    """JSON: Disease distribution for pie/bar chart."""
    period = request.args.get('period', 'overall')
    distribution = get_disease_distribution(period=period)
    top_10 = get_top_diseases(period=period, limit=10)
    return jsonify({
        'pie': distribution,
        'bar': {
            'labels': [d['name'] for d in top_10],
            'data': [d['count'] for d in top_10],
        }
    })


@api_bp.route('/dashboard/visit-trend')
@login_required
def visit_trend():
    """JSON: Visit trend line chart data."""
    days = request.args.get('days', 30, type=int)
    trend = get_visit_trend(days=days)
    return jsonify(trend)


# ---------------------------------------------------------------------------
# Medicine Search (Autocomplete)
# ---------------------------------------------------------------------------

@api_bp.route('/medicines/search')
@login_required
def medicine_search():
    """JSON: Medicine autocomplete for prescription form."""
    q = request.args.get('q', '').strip()
    if len(q) < 1:
        return jsonify([])

    medicines = search_medicines(q, limit=20)
    results = []
    for m in medicines:
        stock_text, stock_color = m.stock_status
        expiry_text, expiry_color = m.expiry_status
        results.append({
            'id': m.medicine_id,
            'name': m.medicine_name,
            'drug_type': m.drug_type,
            'batch_number': m.batch_number or '',
            'available_balance': m.available_balance,
            'expiry_date': m.expiry_date.strftime('%d-%b-%Y') if m.expiry_date else '',
            'is_expired': m.is_expired,
            'stock_status': stock_text,
            'stock_color': stock_color,
            'expiry_status': expiry_text,
            'expiry_color': expiry_color,
        })

    return jsonify(results)


# ---------------------------------------------------------------------------
# Audit Logs Page
# ---------------------------------------------------------------------------

@api_bp.route('/audit-logs')
@login_required
def audit_logs():
    """Render audit logs page with filters."""
    page = request.args.get('page', 1, type=int)
    action_filter = request.args.get('action', '').strip() or None
    module_filter = request.args.get('module', '').strip() or None

    date_from = None
    date_to = None
    date_from_str = request.args.get('date_from', '')
    date_to_str = request.args.get('date_to', '')

    if date_from_str:
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    if date_to_str:
        try:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    logs = get_audit_logs(
        page=page,
        per_page=25,
        action_filter=action_filter,
        module_filter=module_filter,
        date_from=date_from,
        date_to=date_to
    )

    # Collect unique actions & modules for filter dropdowns
    actions = [
        AuditLog.ACTION_LOGIN, AuditLog.ACTION_LOGOUT,
        AuditLog.ACTION_PATIENT_CREATE, AuditLog.ACTION_PATIENT_EDIT,
        AuditLog.ACTION_VISIT_CREATE, AuditLog.ACTION_PRESCRIPTION_CREATE,
        AuditLog.ACTION_MEDICINE_ADD, AuditLog.ACTION_MEDICINE_EDIT,
        AuditLog.ACTION_STOCK_ADD, AuditLog.ACTION_STOCK_DEDUCT,
        AuditLog.ACTION_EXPORT,
    ]
    modules = [
        AuditLog.MODULE_AUTH, AuditLog.MODULE_PATIENTS,
        AuditLog.MODULE_VISITS, AuditLog.MODULE_PRESCRIPTIONS,
        AuditLog.MODULE_MEDICINES, AuditLog.MODULE_EXPORT,
    ]

    return render_template('audit/logs.html',
                           logs=logs,
                           actions=actions,
                           modules=modules,
                           current_action=action_filter or '',
                           current_module=module_filter or '',
                           date_from=date_from_str,
                           date_to=date_to_str)
