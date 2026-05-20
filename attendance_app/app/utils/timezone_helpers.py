"""Timezone utility functions.

All timestamps are stored in UTC. This module provides helpers
to convert UTC timestamps to local timezones for display purposes.

Supported timezones:
- Asia/Kolkata (India)
- America/Edmonton (Canada)
- America/Denver (USA)
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# Supported timezones (IANA names)
SUPPORTED_TIMEZONES = [
    'Asia/Kolkata',
    'America/Edmonton',
    'America/Denver',
]


def get_zoneinfo(tz_name):
    """Return a ZoneInfo object for a timezone name.

    Falls back to UTC if the requested timezone cannot be loaded.
    """
    try:
        return ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        return ZoneInfo('UTC')


def ensure_utc(dt):
    """Normalize a datetime to UTC.

    If the datetime is naive, assume it is UTC and attach utc tzinfo.
    If the datetime is aware, convert it to UTC.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def utc_to_local(utc_dt, tz_name):
    """Convert a UTC datetime to local timezone.
    
    Args:
        utc_dt: Naive or aware datetime in UTC.
        tz_name: IANA timezone name (e.g., 'Asia/Kolkata').
    
    Returns:
        Timezone-aware datetime in the specified timezone.
    """
    if utc_dt is None:
        return None
    
    utc_dt = ensure_utc(utc_dt)
    local_tz = get_zoneinfo(tz_name)
    return utc_dt.astimezone(local_tz)


def get_current_time_local(tz_name):
    """Get current time in a specific timezone.
    
    Args:
        tz_name: IANA timezone name.
    
    Returns:
        Current datetime in the specified timezone.
    """
    local_tz = ZoneInfo(tz_name)
    return datetime.now(timezone.utc).astimezone(local_tz)


def format_datetime_local(utc_dt, tz_name, fmt='%Y-%m-%d %I:%M %p'):
    """Format a UTC datetime as a local timezone string.
    
    Args:
        utc_dt: Datetime in UTC.
        tz_name: IANA timezone name.
        fmt: strftime format string.
    
    Returns:
        Formatted datetime string or '-' if utc_dt is None.
    """
    if utc_dt is None:
        return '-'
    
    local_dt = utc_to_local(utc_dt, tz_name)
    return local_dt.strftime(fmt)


def is_valid_timezone(tz_name):
    """Check if a timezone name is in our supported list.
    
    Args:
        tz_name: IANA timezone name to validate.
    
    Returns:
        Boolean indicating if timezone is supported.
    """
    return tz_name in SUPPORTED_TIMEZONES
