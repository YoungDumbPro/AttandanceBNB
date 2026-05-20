"""Database seeder script.

Creates sample employees for testing the application.
Run with: python seed.py
"""
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.employee import Employee


def seed_database():
    """Create sample employees for development/testing."""
    app = create_app('development')
    
    with app.app_context():
        # Check if data already exists
        if Employee.query.first() is not None:
            print("Database already has data. Skipping seed.")
            print("Existing employees:")
            for emp in Employee.query.all():
                print(f"  - {emp.username} ({emp.role}) [{emp.timezone}]")
            return
        
        # Create admin user
        admin = Employee(
            username='admin',
            timezone='Asia/Kolkata',
            country='India',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create employee - India
        emp1 = Employee(
            username='rajesh',
            timezone='Asia/Kolkata',
            country='India',
            role='employee'
        )
        emp1.set_password('pass123')
        db.session.add(emp1)
        
        # Create employee - Canada
        emp2 = Employee(
            username='john',
            timezone='America/Edmonton',
            country='Canada',
            role='employee'
        )
        emp2.set_password('pass123')
        db.session.add(emp2)
        
        # Create employee - USA
        emp3 = Employee(
            username='mike',
            timezone='America/Denver',
            country='USA',
            role='employee'
        )
        emp3.set_password('pass123')
        db.session.add(emp3)
        
        db.session.commit()
        
        print("Database seeded successfully!")
        print("Created users:")
        print("  Admin:    admin / admin123  (Asia/Kolkata)")
        print("  Employee: rajesh / pass123  (Asia/Kolkata)")
        print("  Employee: john / pass123    (America/Edmonton)")
        print("  Employee: mike / pass123    (America/Denver)")


if __name__ == '__main__':
    seed_database()
