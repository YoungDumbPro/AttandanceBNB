"""Employee model."""
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db, login_manager


class Employee(UserMixin, db.Model):
    """Employee model for authentication and user management.
    
    Attributes:
        id: Primary key
        username: Unique username for login
        password_hash: Securely hashed password
        timezone: IANA timezone name (e.g., Asia/Kolkata)
        country: Employee's country
        role: Either 'employee' or 'admin'
        created_at: Account creation timestamp (UTC)
    """
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    timezone = db.Column(db.String(50), nullable=False, default='Asia/Kolkata')
    country = db.Column(db.String(100), nullable=False, default='India')
    role = db.Column(db.String(20), nullable=False, default='employee')
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationship to attendance records
    attendance_records = db.relationship('Attendance', backref='employee', lazy='dynamic',
                                         order_by='Attendance.check_in_utc.desc()')

    def set_password(self, password):
        """Hash and store password securely."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against stored hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        """Check if employee has admin role."""
        return self.role == 'admin'

    @property
    def is_checked_in(self):
        """Check if employee has an active (open) attendance record."""
        from app.models.attendance import Attendance
        return Attendance.query.filter_by(
            employee_id=self.id,
            check_out_utc=None
        ).first() is not None

    @property
    def active_record(self):
        """Get current active attendance record (checked in, not yet out)."""
        from app.models.attendance import Attendance
        return Attendance.query.filter_by(
            employee_id=self.id,
            check_out_utc=None
        ).first()

    def __repr__(self):
        return f'<Employee {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return Employee.query.get(int(user_id))
