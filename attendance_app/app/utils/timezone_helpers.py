"""Timezone utility functions.

All timestamps are stored in UTC. This module provides helpers
to convert UTC timestamps to local timezones for display purposes.

Supported timezones:
- Asia/Kolkata (India)
- America/Edmonton (Canada)
- America/Denver (USA)
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Supported timezones (IANA names)
SUPPORTED_TIMEZONES = [
    'Asia/Kolkata',
    'America/Edmonton',
    'America/Denver',
]


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
    
    # Ensure the datetime is timezone-aware (UTC)
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    
    local_tz = ZoneInfo(tz_name)
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
