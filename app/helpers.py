from datetime import datetime
import uuid


def coerce_uuid(value):
    if not value:
        return None
    if isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(value)
    except (ValueError, TypeError, AttributeError):
        return None


def coerce_date(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    if hasattr(value, 'strftime'):
        return value
    try:
        return datetime.strptime(str(value), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def coerce_money(value):
    if not value:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def coerce_float(value):
    if not value:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def coerce_int(value, default=0):
    if not value and value != 0:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
