# systemd Service Files

These service files run FastAPI and Celery as system services.

## Installation

### 1. Copy service files

```bash
sudo cp fastapi-api.service /etc/systemd/system/
sudo cp celery-worker.service /etc/systemd/system/
```

### 2. Customize service files

Edit the files and replace:
- `your-user` → your actual username (e.g., `ubuntu`)
- `/python-hosting/my-api` → your actual project path

```bash
sudo nano /etc/systemd/system/fastapi-api.service
sudo nano /etc/systemd/system/celery-worker.service
```

### 3. Reload systemd

```bash
sudo systemctl daemon-reload
```

### 4. Enable services (auto-start on boot)

```bash
sudo systemctl enable fastapi-api
sudo systemctl enable celery-worker
```

### 5. Start services

```bash
sudo systemctl start fastapi-api
sudo systemctl start celery-worker
```

### 6. Check status

```bash
sudo systemctl status fastapi-api
sudo systemctl status celery-worker
```

## Important Configuration Notes

### Absolute Paths Required

systemd does **NOT** use your shell environment. You must specify full paths:

```ini
# ✅ CORRECT
ExecStart=/python-hosting/my-api/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000

# ❌ WRONG (won't work)
ExecStart=uvicorn main:app --host 127.0.0.1 --port 8000
```

### WorkingDirectory

Must point to your project directory containing `main.py`:

```ini
WorkingDirectory=/python-hosting/my-api
```

### Environment PATH

Include venv bin directory:

```ini
Environment="PATH=/python-hosting/my-api/venv/bin"
```

### User and Group

Replace with your actual username:

```bash
# Find your username
whoami

# Use in service file
User=ubuntu
Group=ubuntu
```

## Common Commands

```bash
# Start services
sudo systemctl start fastapi-api celery-worker

# Stop services
sudo systemctl stop fastapi-api celery-worker

# Restart services (after code changes)
sudo systemctl restart fastapi-api celery-worker

# Check status
sudo systemctl status fastapi-api
sudo systemctl status celery-worker

# View logs
sudo journalctl -u fastapi-api -f
sudo journalctl -u celery-worker -f

# Enable auto-start on boot
sudo systemctl enable fastapi-api celery-worker

# Disable auto-start
sudo systemctl disable fastapi-api celery-worker
```

## After Code Changes

```bash
# Restart services to load new code
sudo systemctl restart fastapi-api celery-worker

# Watch logs for errors
sudo journalctl -u fastapi-api -f
```

## Troubleshooting

### Service fails to start

```bash
# Check logs for errors
sudo journalctl -u fastapi-api -n 50 --no-pager

# Common issues:
# - Wrong path to venv
# - Wrong working directory
# - Missing dependencies
# - Port already in use
```

### Permission denied

```bash
# Fix ownership
sudo chown -R your-user:your-user /python-hosting/my-api
```

### Service keeps restarting

```bash
# View logs
sudo journalctl -u fastapi-api -f

# Usually means:
# - Import error in Python code
# - Port conflict
# - Missing Redis connection (for Celery)
```

## Advanced Options

### Add Environment Variables

```ini
[Service]
Environment="PATH=/python-hosting/my-api/venv/bin"
Environment="DATABASE_URL=postgresql://..."
Environment="REDIS_URL=redis://localhost:6379/0"
Environment="SECRET_KEY=your-secret-key"
```

### Change Log Level

For Celery:
```ini
ExecStart=/python-hosting/my-api/venv/bin/celery -A tasks worker --loglevel=debug
```

For FastAPI (add logging config in code):
```python
# main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Options

The service files include basic security settings:

```ini
NoNewPrivileges=true    # Prevent privilege escalation
PrivateTmp=true         # Use private /tmp directory
```

For more security hardening, consider:
```ini
ProtectSystem=full
ProtectHome=true
ReadOnlyPaths=/
ReadWritePaths=/python-hosting/my-api
```
