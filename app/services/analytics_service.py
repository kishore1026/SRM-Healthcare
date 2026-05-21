"""Analytics service – dashboard stats, disease analytics, chart data."""
from datetime import date, timedelta, datetime
from collections import Counter

from sqlalchemy import func, cast, Date

from app.extensions import db
from app.models.patient import Patient
from app.models.visit import PatientVisit
from app.models.medicine import Medicine
from app.utils.helpers import get_date_range


# ---------------------------------------------------------------------------
# Summary Card Statistics
# ---------------------------------------------------------------------------

def get_summary_stats(period='overall'):
    """Return summary card data for the dashboard.

    Returns dict with: total_patients, total_visits, total_medicines,
    low_stock_count, expiring_count, top_diseases.
    """
    from app.services.medicine_service import get_alert_counts

    start_date, end_date = get_date_range(period)

    # Patient count
    total_patients = Patient.query.count()

    # Visit count (filtered by period)
    visit_query = PatientVisit.query
    if start_date:
        visit_query = visit_query.filter(PatientVisit.visit_date >= start_date)
    if end_date:
        visit_query = visit_query.filter(PatientVisit.visit_date <= end_date)
    total_visits = visit_query.count()

    # Medicine count
    total_medicines = Medicine.query.count()

    # Alert counts
    alerts = get_alert_counts()

    # Top 3 diseases for the period
    top_diseases = get_top_diseases(period=period, limit=3)

    return {
        'total_patients': total_patients,
        'total_visits': total_visits,
        'total_medicines': total_medicines,
        'low_stock_count': alerts['low_stock'],
        'expiring_count': alerts['expiring'],
        'expired_count': alerts['expired'],
        'out_of_stock_count': alerts['out_of_stock'],
        'top_diseases': top_diseases,
    }


# ---------------------------------------------------------------------------
# Disease Analytics
# ---------------------------------------------------------------------------

def get_top_diseases(period='overall', limit=10):
    """Return top N diseases with visit counts.

    Returns list of dicts: [{'name': str, 'count': int}, ...]
    """
    start_date, end_date = get_date_range(period)

    query = db.session.query(
        PatientVisit.diagnosis,
        func.count(PatientVisit.visit_id).label('cnt')
    ).filter(
        PatientVisit.diagnosis.isnot(None),
        PatientVisit.diagnosis != ''
    )

    if start_date:
        query = query.filter(PatientVisit.visit_date >= start_date)
    if end_date:
        query = query.filter(PatientVisit.visit_date <= end_date)

    results = query.group_by(PatientVisit.diagnosis)\
                   .order_by(func.count(PatientVisit.visit_id).desc())\
                   .limit(limit).all()

    return [{'name': r[0], 'count': r[1]} for r in results]


def get_disease_distribution(period='overall'):
    """Return disease distribution data for pie chart.

    Returns dict: {labels: [...], data: [...], colors: [...]}
    """
    diseases = get_top_diseases(period=period, limit=8)

    palette = [
        '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e',
        '#e74a3b', '#858796', '#5a5c69', '#2e59d9',
    ]

    labels = [d['name'] for d in diseases]
    data = [d['count'] for d in diseases]
    colors = palette[:len(labels)]

    return {'labels': labels, 'data': data, 'colors': colors}


# ---------------------------------------------------------------------------
# Visit Trend
# ---------------------------------------------------------------------------

def get_visit_trend(days=30):
    """Return daily visit counts for the last N days.

    Returns dict: {labels: ['May 01', ...], data: [5, 3, ...]}
    """
    today = date.today()
    start = today - timedelta(days=days - 1)

    results = db.session.query(
        PatientVisit.visit_date,
        func.count(PatientVisit.visit_id)
    ).filter(
        PatientVisit.visit_date >= start,
        PatientVisit.visit_date <= today
    ).group_by(PatientVisit.visit_date)\
     .order_by(PatientVisit.visit_date).all()

    # Build a complete date series (fill gaps with 0)
    counts_by_date = {r[0]: r[1] for r in results}
    labels = []
    data = []
    for i in range(days):
        d = start + timedelta(days=i)
        labels.append(d.strftime('%d %b'))
        data.append(counts_by_date.get(d, 0))

    return {'labels': labels, 'data': data}


# ---------------------------------------------------------------------------
# Recent Activity
# ---------------------------------------------------------------------------

def get_recent_visits(limit=10):
    """Return the most recent visits with patient info."""
    return PatientVisit.query\
        .order_by(PatientVisit.visit_date.desc(), PatientVisit.visit_time.desc())\
        .limit(limit).all()


def get_monthly_comparison():
    """Return visit count comparison between this month and last month."""
    today = date.today()
    this_month_start = today.replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    this_month = PatientVisit.query.filter(
        PatientVisit.visit_date >= this_month_start,
        PatientVisit.visit_date <= today
    ).count()

    last_month = PatientVisit.query.filter(
        PatientVisit.visit_date >= last_month_start,
        PatientVisit.visit_date <= last_month_end
    ).count()

    if last_month > 0:
        change_pct = round(((this_month - last_month) / last_month) * 100, 1)
    else:
        change_pct = 100.0 if this_month > 0 else 0.0

    return {
        'this_month': this_month,
        'last_month': last_month,
        'change_pct': change_pct,
    }
