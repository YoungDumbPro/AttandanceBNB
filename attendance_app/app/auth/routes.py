"""Authentication routes."""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.auth import auth_bp
from app.models.employee import Employee


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    # Redirect if already logged in
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('attendance.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('auth/login.html')

        # Find employee by username
        employee = Employee.query.filter_by(username=username).first()

        if employee is None or not employee.check_password(password):
            flash('Invalid username or password.', 'danger')
            return render_template('auth/login.html')

        # Log the user in
        login_user(employee, remember=True)
        
        # Redirect to requested page or default dashboard
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        
        if employee.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('attendance.dashboard'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
