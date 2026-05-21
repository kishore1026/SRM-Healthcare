from datetime import datetime, date, timedelta
import math


def format_date(d, fmt='%d %b %Y'):
    """Format a date object for display."""
    if isinstance(d, date):
        return d.strftime(fmt)
    return ''


def format_datetime(dt, fmt='%d %b %Y %I:%M %p'):
    """Format a datetime object for display."""
    if isinstance(dt, datetime):
        return dt.strftime(fmt)
    return ''


def format_time(t, fmt='%I:%M %p'):
    """Format a time object for display."""
    if t:
        return t.strftime(fmt)
    return ''


def get_date_range(period):
    """Get start and end date for a period filter.

    Args:
        period: 'today', 'week', 'month', 'overall'

    Returns:
        tuple: (start_date, end_date)
    """
    today = date.today()
    if period == 'today':
        return today, today
    elif period == 'week':
        start = today - timedelta(days=today.weekday())
        return start, today
    elif period == 'month':
        start = today.replace(day=1)
        return start, today
    else:  # overall
        return None, None


def paginate_list(items, page, per_page):
    """Paginate a list of items."""
    total = len(items)
    total_pages = math.ceil(total / per_page) if total > 0 else 1
    start = (page - 1) * per_page
    end = start + per_page
    return {
        'items': items[start:end],
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
    }


def safe_int(value, default=0):
    """Safely convert a value to integer."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
