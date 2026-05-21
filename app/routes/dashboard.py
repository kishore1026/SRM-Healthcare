"""Dashboard routes – summary cards, charts, alerts."""
from flask import Blueprint, render_template, request
from flask_login import login_required

from app.services.analytics_service import (
    get_summary_stats, get_recent_visits, get_monthly_comparison,
)
from app.services.medicine_service import (
    get_low_stock_medicines, get_expiring_medicines, get_expired_medicines,
)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard with summary cards, charts, and alerts."""
    period = request.args.get('period', 'overall')

    stats = get_summary_stats(period=period)
    recent_visits = get_recent_visits(limit=10)
    comparison = get_monthly_comparison()

    # Alert medicines for the sidebar
    low_stock = get_low_stock_medicines()[:5]
    expiring = get_expiring_medicines()[:5]
    expired = get_expired_medicines()[:5]

    return render_template('dashboard/index.html',
                           stats=stats,
                           recent_visits=recent_visits,
                           comparison=comparison,
                           low_stock=low_stock,
                           expiring=expiring,
                           expired=expired,
                           period=period)
