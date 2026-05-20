"""Attendance routes for check-in/check-out functionality."""
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

from app import db
from app.attendance import attendance_bp
from app.models.attendance import Attendance


@attendance_bp.route('/dashboard')
@login_required
def dashboard():
    """Employee attendance dashboard."""
    # Get employee's timezone
    emp_tz = ZoneInfo(current_user.timezone)
    now_local = datetime.now(timezone.utc).astimezone(emp_tz)
    
    # Get today's records in employee's local timezone
    today_start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    today_start_utc = today_start_local.astimezone(timezone.utc)
    
    today_records = Attendance.query.filter(
        Attendance.employee_id == current_user.id,
        Attendance.check_in_utc >= today_start_utc
    ).order_by(Attendance.check_in_utc.desc()).all()
    
    # Calculate today's total worked hours
    total_hours_today = 0.0
    for record in today_records:
        if record.check_out_utc:
            delta = record.check_out_utc - record.check_in_utc
            total_hours_today += delta.total_seconds() / 3600
        else:
            # Active session - calculate up to now
            delta = datetime.now(timezone.utc) - record.check_in_utc
            total_hours_today += delta.total_seconds() / 3600
    
    # Check current status
    is_checked_in = current_user.is_checked_in
    active_record = current_user.active_record
    
    return render_template('attendance/dashboard.html',
                           is_checked_in=is_checked_in,
                           active_record=active_record,
                           today_records=today_records,
                           total_hours_today=round(total_hours_today, 2),
                           current_time=now_local,
                           emp_tz=emp_tz)


@attendance_bp.route('/checkin', methods=['POST'])
@login_required
def checkin():
    """Handle employee check-in."""
    # Prevent duplicate check-ins
    if current_user.is_checked_in:
        flash('You are already checked in.', 'warning')
        return redirect(url_for('attendance.dashboard'))
    
    # Get GPS coordinates from form data
    latitude = request.form.get('latitude', type=float)
    longitude = request.form.get('longitude', type=float)
    
    # Create new attendance record
    record = Attendance(
        employee_id=current_user.id,
        check_in_utc=datetime.now(timezone.utc),
        latitude=latitude,
        longitude=longitude
    )
    
    db.session.add(record)
    db.session.commit()
    
    flash('Successfully checked in!', 'success')
    return redirect(url_for('attendance.dashboard'))


@attendance_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    """Handle employee check-out."""
    # Find active attendance record
    active_record = current_user.active_record
    
    if active_record is None:
        flash('No active check-in found.', 'warning')
        return redirect(url_for('attendance.dashboard'))
    
    # Update with check-out time
    active_record.check_out_utc = datetime.now(timezone.utc)
    db.session.commit()
    
    # Calculate worked hours for display
    worked = active_record.worked_hours
    flash(f'Checked out successfully! Worked {worked:.2f} hours.', 'success')
    return redirect(url_for('attendance.dashboard'))


@attendance_bp.route('/')
def index():
    """Root route - redirect to dashboard or login."""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('attendance.dashboard'))
    return redirect(url_for('auth.login'))
