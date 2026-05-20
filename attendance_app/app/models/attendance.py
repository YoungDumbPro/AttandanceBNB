"""Attendance model."""
from datetime import datetime, timezone

from app import db


class Attendance(db.Model):
    """Attendance model for tracking check-in/check-out times.
    
    All timestamps are stored in UTC. Timezone conversion happens
    only during display in templates.
    
    Attributes:
        id: Primary key
        employee_id: Foreign key to employees table
        check_in_utc: Check-in timestamp in UTC
        check_out_utc: Check-out timestamp in UTC (null if still checked in)
        latitude: GPS latitude at check-in
        longitude: GPS longitude at check-in
        created_at: Record creation timestamp (UTC)
    """
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    check_in_utc = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    check_out_utc = db.Column(db.DateTime(timezone=True), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def _ensure_utc(self, dt):
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    @property
    def worked_hours(self):
        """Calculate hours worked for this record.
        
        Returns:
            Float of hours worked, or None if still checked in.
        """
        check_in = self._ensure_utc(self.check_in_utc)
        if self.check_out_utc is None:
            now = datetime.now(timezone.utc)
            delta = now - check_in
            return round(delta.total_seconds() / 3600, 2)

        check_out = self._ensure_utc(self.check_out_utc)
        delta = check_out - check_in
        return round(delta.total_seconds() / 3600, 2)

    @property
    def is_active(self):
        """Check if this is an active (open) attendance record."""
        return self.check_out_utc is None

    def __repr__(self):
        return f'<Attendance {self.employee_id} - {self.check_in_utc}>'
