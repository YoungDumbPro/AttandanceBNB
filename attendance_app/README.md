# Employee Attendance Tracker

A production-ready Flask-based employee attendance and work-hours tracking web application with a mobile-first responsive UI.

## Features

- **Employee Authentication** - Secure login/logout with password hashing
- **Check-In / Check-Out** - One-tap attendance with GPS location capture
- **Timezone-Aware** - All timestamps stored in UTC, displayed in employee's local timezone
- **Admin Dashboard** - View all employees, their status, and monthly worked hours
- **Excel Reports** - Download attendance reports as .xlsx files
- **Mobile-First UI** - Responsive design with large touch-friendly buttons
- **GPS Tracking** - Captures latitude/longitude on check-in via browser Geolocation API

## Tech Stack

- **Backend**: Flask, Flask-SQLAlchemy, Flask-Login, Flask-Migrate, Flask-WTF
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5, Jinja2 Templates, Vanilla JavaScript
- **Export**: openpyxl for Excel generation
- **Server**: Gunicorn (production)

## Supported Timezones

- Asia/Kolkata (India)
- America/Edmonton (Canada)
- America/Denver (USA)

## Project Structure

```
attendance_app/
├── app/
│   ├── admin/          # Admin blueprint (dashboard, employee detail, export)
│   ├── attendance/     # Attendance blueprint (check-in, check-out, dashboard)
│   ├── auth/           # Auth blueprint (login, logout)
│   ├── models/         # SQLAlchemy models (Employee, Attendance)
│   ├── templates/      # Jinja2 templates
│   ├── static/         # CSS, JavaScript
│   ├── utils/          # Timezone helpers, Excel export
│   └── __init__.py     # App factory
├── config.py           # Configuration classes
├── run.py              # Application entry point
├── seed.py             # Database seeder script
├── requirements.txt    # Python dependencies
├── .env                # Environment variables
└── README.md           # This file
```

## Quick Start (Local Development)

### Prerequisites

- Python 3.11+
- PostgreSQL (running locally or via Docker)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd attendance_app
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

```bash
# Create database
createdb attendance_db

# Or via psql
psql -c "CREATE DATABASE attendance_db;"
```

### 5. Configure Environment Variables

Copy `.env.example` to `.env` and set your values:

```env
FLASK_APP=run.py
FLASK_ENV=development
PORT=5000
SECRET_KEY=your-strong-secret-key-here
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/attendance_db
```

For Neon PostgreSQL, use the provided connection string. Example:

```env
DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<database>?sslmode=require
```

Do not commit the `.env` file to source control.

### 6. Initialize Database

```bash
# Using Flask-Migrate
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Or simply run the app (tables are auto-created)
python run.py
```

### 7. Seed Sample Data

```bash
python seed.py
```

This creates:
- **Admin user**: `admin` / `admin123`
- **Employee 1**: `rajesh` / `pass123` (Asia/Kolkata)
- **Employee 2**: `john` / `pass123` (America/Edmonton)
- **Employee 3**: `mike` / `pass123` (America/Denver)

### 8. Run the Application

```bash
python run.py
```

Visit: http://localhost:5000

## Production Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### With systemd (Linux)

Create `/etc/systemd/system/attendance.service`:

```ini
[Unit]
Description=Attendance Tracker
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/attendance_app
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 run:app

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable attendance
sudo systemctl start attendance
```

### Environment Variables for Production

```env
FLASK_ENV=production
PORT=8000
SECRET_KEY=generate-a-strong-random-key
DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<database>?sslmode=require
```

For Neon, use the secure connection string from the Neon console. If the string already contains `sslmode=require`, do not add it again.

In production, `SECRET_KEY` is required and the app will refuse to start if it is missing or uses the default development secret.

### Docker (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
```

## API Routes

| Route | Method | Access | Description |
|-------|--------|--------|-------------|
| `/login` | GET/POST | Public | User login |
| `/logout` | GET | Authenticated | User logout |
| `/dashboard` | GET | Authenticated | Employee dashboard |
| `/checkin` | POST | Authenticated | Check in with GPS |
| `/checkout` | POST | Authenticated | Check out |
| `/admin/` | GET | Admin only | Admin dashboard |
| `/admin/employee/<id>` | GET | Admin only | Employee detail |
| `/admin/export/employee/<id>` | GET | Admin only | Download Excel report |

## Security

- Passwords hashed with Werkzeug (PBKDF2)
- CSRF protection via Flask-WTF
- Session-based authentication via Flask-Login
- Role-based access control (admin decorator)
- Login required for all protected routes

## License

MIT
