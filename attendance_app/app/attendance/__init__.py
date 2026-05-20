"""Attendance blueprint."""
from flask import Blueprint

attendance_bp = Blueprint('attendance', __name__, url_prefix='')

from app.attendance import routes  # noqa: E402, F401
