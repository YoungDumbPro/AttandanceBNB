"""Admin routes for employee management and reporting."""
from datetime import datetime, timezone, timedelta
from functools import wraps

from flask import render_template, redirect, url_for, flash, abort, send_file
from flask_login import login_required, current_user

from app import db
from app.admin import admin_bp
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.utils.excel_export import generate_excel_report
from app.utils.timezone_helpers import ensure_utc, get_zoneinfo


def admin_required(f):
    """Decorator to restrict access to admin users only."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard showing all employees and their status."""
    employees = Employee.query.all()
    
    # Build employee data with status and monthly hours
    employee_data = []
    now = datetime.now(timezone.utc)
    
    # Calculate start of current month (UTC)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    for emp in employees:
        # Get last activity
        last_record = Attendance.query.filter_by(
            employee_id=emp.id
        ).order_by(Attendance.check_in_utc.desc()).first()
        
        # Calculate monthly worked hours
        monthly_records = Attendance.query.filter(
            Attendance.employee_id == emp.id,
            Attendance.check_in_utc >= month_start
        ).all()
        
        monthly_hours = 0.0
        for record in monthly_records:
            if record.check_out_utc:
                check_out = ensure_utc(record.check_out_utc)
                check_in = ensure_utc(record.check_in_utc)
                delta = check_out - check_in
                monthly_hours += delta.total_seconds() / 3600
            else:
                # Active session
                check_in = ensure_utc(record.check_in_utc)
                delta = now - check_in
                monthly_hours += delta.total_seconds() / 3600
        
        employee_data.append({
            'employee': emp,
            'is_checked_in': emp.is_checked_in,
            'last_activity': last_record.check_in_utc if last_record else None,
            'monthly_hours': round(monthly_hours, 2)
        })
    
    return render_template('admin/dashboard.html',
                           employee_data=employee_data,
                           current_month=now.strftime('%B %Y'))


@admin_bp.route('/employee/<int:employee_id>')
@admin_required
def employee_detail(employee_id):
    """Employee detail page with last 30 days attendance."""
    employee = Employee.query.get_or_404(employee_id)
    
    # Get last 30 days of records
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    
    records = Attendance.query.filter(
        Attendance.employee_id == employee_id,
        Attendance.check_in_utc >= thirty_days_ago
    ).order_by(Attendance.check_in_utc.desc()).all()
    
    # Get employee timezone for display
    emp_tz = get_zoneinfo(employee.timezone)
    
    # Calculate summary stats
    total_hours = 0.0
    days_worked = set()
    
    for record in records:
        if record.check_out_utc:
            check_out = ensure_utc(record.check_out_utc)
            check_in = ensure_utc(record.check_in_utc)
            delta = check_out - check_in
            total_hours += delta.total_seconds() / 3600
        else:
            check_in = ensure_utc(record.check_in_utc)
            delta = datetime.now(timezone.utc) - check_in
            total_hours += delta.total_seconds() / 3600
        
        # Track unique days worked (in employee's timezone)
        local_checkin = record.check_in_utc.replace(tzinfo=timezone.utc).astimezone(emp_tz)
        days_worked.add(local_checkin.date())
    
    num_days_worked = len(days_worked)
    avg_hours = round(total_hours / num_days_worked, 2) if num_days_worked > 0 else 0
    
    return render_template('admin/employee_detail.html',
                           employee=employee,
                           records=records,
                           emp_tz=emp_tz,
                           total_hours=round(total_hours, 2),
                           days_worked=num_days_worked,
                           avg_hours=avg_hours)


@admin_bp.route('/export/employee/<int:employee_id>')
@admin_required
def export_employee(employee_id):
    """Export employee attendance as Excel file."""
    employee = Employee.query.get_or_404(employee_id)
    
    # Get last 30 days of records
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    
    records = Attendance.query.filter(
        Attendance.employee_id == employee_id,
        Attendance.check_in_utc >= thirty_days_ago
    ).order_by(Attendance.check_in_utc.asc()).all()
    
    # Generate Excel file
    emp_tz = get_zoneinfo(employee.timezone)
    excel_file = generate_excel_report(employee, records, emp_tz)
    
    filename = f"attendance_{employee.username}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    return send_file(
        excel_file,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
