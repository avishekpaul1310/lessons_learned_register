# Detailed Installation Guide

This document provides comprehensive installation instructions for the Lessons Learned System for both development and production environments.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git
- virtualenv or venv (recommended)
- PostgreSQL (for production)

## Development Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/lessons-learned-system.git
cd lessons-learned-system
```

### 2. Create and Activate a Virtual Environment

```bash
# Option 1: Using venv (Python 3.3+)
python -m venv venv

# Option 2: Using virtualenv
virtualenv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your settings
# Especially the DJANGO_SECRET_KEY
```

Generate a secure Django secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Update the `DJANGO_SECRET_KEY` in your `.env` file with this value.

### 5. Database Setup

```bash
# Apply migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser
```

### 6. Create Media Directories and Default Files

```bash
# Run the script to create required directories and default profile images
python create_default_jpg.py
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at http://localhost:8000

### 8. (Optional) Load Test Data

```bash
python create_test_data.py
```

## Production Environment Setup

### 1. Server Preparation

Install required packages on your server:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib
```

### 2. Database Setup

```bash
# Create a PostgreSQL database
sudo -u postgres psql
CREATE DATABASE lessons_learned;
CREATE USER lessonsuser WITH PASSWORD 'secure_password';
ALTER ROLE lessonsuser SET client_encoding TO 'utf8';
ALTER ROLE lessonsuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE lessonsuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE lessons_learned TO lessonsuser;
\q
```

### 3. Application Setup

Follow steps 1-5 from the Development Environment Setup above, with these changes:

- Use PostgreSQL settings in your `.env` file
- Set `DJANGO_DEBUG=False`
- Update `DJANGO_ALLOWED_HOSTS` to include your domain
- Configure a production email backend

### 4. Collect Static Files

```bash
python manage.py collectstatic
```

### 5. Set Up Gunicorn

Install Gunicorn:

```bash
pip install gunicorn
```

Create a systemd service file (e.g., `/etc/systemd/system/lessons_learned.service`):

```ini
[Unit]
Description=Lessons Learned System Gunicorn Daemon
After=network.target

[Service]
User=your_user
Group=your_group
WorkingDirectory=/path/to/lessons-learned-system
ExecStart=/path/to/lessons-learned-system/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/path/to/lessons-learned-system/lessons_learned.sock \
          lessons_learned.wsgi:application

[Install]
WantedBy=multi-user.target
```

Start and enable the service:

```bash
sudo systemctl start lessons_learned
sudo systemctl enable lessons_learned
```

### 6. Configure Nginx

Create an Nginx configuration file (e.g., `/etc/nginx/sites-available/lessons_learned`):

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/lessons-learned-system;
    }

    location /media/ {
        root /path/to/lessons-learned-system;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/lessons-learned-system/lessons_learned.sock;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/lessons_learned /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

### 7. SSL/TLS Configuration (Recommended)

Install Certbot:

```bash
sudo apt install certbot python3-certbot-nginx
```

Obtain and configure an SSL certificate:

```bash
sudo certbot --nginx -d yourdomain.com
```

## Troubleshooting

### Missing Profile Images

If profile images are not displaying correctly:

```bash
python manage.py create_missing_profiles
```

### Database Migration Issues

If you encounter migration errors:

```bash
# Reset migrations (development only)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
python manage.py makemigrations
python manage.py migrate
```

### Permission Issues with Media Files

```bash
# Set correct permissions
sudo chown -R www-data:www-data /path/to/lessons-learned-system/media
```

## Updates and Maintenance

To update the application:

```bash
# Pull latest changes
git pull

# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Collect static files (if needed)
python manage.py collectstatic --no-input

# Restart services
sudo systemctl restart lessons_learned
sudo systemctl restart nginx
```

## Backup and Recovery

### Database Backup

```bash
# SQLite
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d)

# PostgreSQL
pg_dump -U lessonsuser -d lessons_learned -F c -f backup.$(date +%Y%m%d).dump
```

### Media Backup

```bash
tar -czf media_backup.$(date +%Y%m%d).tar.gz media/
```

### Restore from Backup

```bash
# SQLite
cp db.sqlite3.backup.YYYYMMDD db.sqlite3

# PostgreSQL
pg_restore -U lessonsuser -d lessons_learned -c backup.YYYYMMDD.dump

# Media files
tar -xzf media_backup.YYYYMMDD.tar.gz
```
