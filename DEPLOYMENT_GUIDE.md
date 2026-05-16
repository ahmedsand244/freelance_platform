# 🚀 Freelance Platform Production Deployment Guide

This guide describes how to deploy the Freelance marketplace (Khamsat clone) to a Linux (Ubuntu 22.04+) server in a secure, high-performance configuration.

## System Architecture

The architecture separates core processes to maximize scalability, utilizing asynchronous workers whenever possible.

1.  **Nginx (Reverse Proxy)**: Entry point that routes HTTP traffic to Gunicorn and WebSocket (`/ws/`) traffic to Daphne. Handles static/media files extremely fast.
2.  **Gunicorn (WSGI)**: Handles pure standard synchronous Django web traffic perfectly.
3.  **Daphne (ASGI)**: Standalone asynchronous server dedicated strictly to WebSockets.
4.  **Redis**: Serves primarily as the in-memory Cache backend, the Celery task broker, and the Django Channels layer communication pipeline.
5.  **Celery**: Background queue processing (Emails, heavy compute loads).

---

## 🛠️ 1. Server Environment Setup

```bash
# Update Ubuntu system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3.11-venv python3-pip nginx redis-server supervisor -y

# Start and enable Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

## 📦 2. Clone Project & Install Dependencies

```bash
# Move to web directory
cd /var/www/
git clone <your_repo_url> khamsat
cd khamsat

# Setup Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install strictly generated production dependencies
pip install -r requirements.txt
pip install gunicorn daphne channels channels-redis django-redis celery
```

## 🔒 3. Configure SECRETS (`.env`)
Make sure your `/var/www/khamsat/.env` looks like this before proceeding:
```properties
DEBUG=False
ALLOWED_HOSTS=your_domain.com,www.your_domain.com,127.0.0.1
SECRET_KEY=generate_a_very_secure_random_hash
DATABASE_URL=postgres://user:pass@localhost:5432/khamsat_db
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/2
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/2
```

## 🗄️ 4. Build Static Content & Migrate

```bash
# Process Javascript, CSS, and Image optimisations into the single /staticfiles/ folder
python manage.py collectstatic --noinput

# Establish Database schema mapping
python manage.py migrate
```

## ⚙️ 5. Setting up SystemD Process Managers

For stability, we will bind Gunicorn, Daphne, and Celery into `systemd` daemon services.

### Gunicorn Service
**`sudo nano /etc/systemd/system/gunicorn.service`**
```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/khamsat
Environment="PATH=/var/www/khamsat/venv/bin"
ExecStart=/var/www/khamsat/venv/bin/gunicorn -c gunicorn_config.py khamsat.wsgi:application

[Install]
WantedBy=multi-user.target
```

### Daphne Service (WebSockets)
**`sudo nano /etc/systemd/system/daphne.service`**
```ini
[Unit]
Description=daphne daemon (Channels)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/khamsat
Environment="PATH=/var/www/khamsat/venv/bin"
ExecStart=/var/www/khamsat/venv/bin/daphne -b 127.0.0.1 -p 8001 khamsat.asgi:application

[Install]
WantedBy=multi-user.target
```

### Celery Background Worker Service
**`sudo nano /etc/systemd/system/celery.service`**
```ini
[Unit]
Description=Celery Worker
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/khamsat
Environment="PATH=/var/www/khamsat/venv/bin"
ExecStart=/var/www/khamsat/venv/bin/celery -A khamsat worker -l INFO

[Install]
WantedBy=multi-user.target
```

### Start SystemDaemons
```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn daphne celery
sudo systemctl start gunicorn daphne celery
```

## 🌐 6. Set up NGINX & SSL
We have provided a generated `nginx.conf` file in the repository root.

```bash
# Link the config properly
sudo cp /var/www/khamsat/nginx.conf /etc/nginx/sites-available/khamsat
sudo ln -s /etc/nginx/sites-available/khamsat /etc/nginx/sites-enabled/

# Reload Nginx configuration
sudo nginx -t
sudo systemctl restart nginx
```

> [!TIP]
> **Securing SSL via CertBot**
> `sudo apt install certbot python3-certbot-nginx` 
> `sudo certbot --nginx -d your_domain.com -d www.your_domain.com`

---
All complete. The infrastructure is thoroughly isolated perfectly splitting synchronous CPU blocks from long-lived socket operations. Money limits, Redis caching buffers, and Django cookie parameters guarantee absolute security during payout validations and connections blockages.
