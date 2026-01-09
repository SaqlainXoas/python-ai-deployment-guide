# Nginx Configuration

This Nginx configuration file sets up a reverse proxy for your FastAPI application.

## Installation

### 1. Copy config file

```bash
sudo cp python-app.conf /etc/nginx/sites-available/python-app
```

### 2. Edit configuration

Replace `your-domain.com` with your actual domain or server IP:

```bash
sudo nano /etc/nginx/sites-available/python-app
```

Change:
```nginx
server_name your-domain.com www.your-domain.com;
```

To:
```nginx
# If you have a domain:
server_name example.com www.example.com;

# If using IP only:
server_name 203.0.113.42;  # your server IP

# Or for testing:
server_name _;  # match all
```

### 3. Enable the site

```bash
sudo ln -s /etc/nginx/sites-available/python-app /etc/nginx/sites-enabled/
```

### 4. Test configuration

```bash
sudo nginx -t
```

**Expected output:**
```
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### 5. Reload Nginx

```bash
sudo systemctl reload nginx
```

## Verify It Works

```bash
# Test from server
curl http://localhost/python/

# Test from browser
http://your-domain.com/python/
```

## Important Notes

### Trailing Slash Issue

**CRITICAL:** Do NOT use trailing slashes inconsistently!

```nginx
# ✅ CORRECT (no trailing slashes)
location /python {
    proxy_pass http://localhost:5000;
}

# ❌ WRONG (causes 404 errors)
location /python/ {
    proxy_pass http://localhost:5000/;
}
```

**Rule:** Keep `/python` without trailing slash in both location and proxy_pass.

### Why These Headers?

```nginx
proxy_set_header Host $host;
# Preserves original hostname (your-domain.com)

proxy_set_header X-Real-IP $remote_addr;
# Sends visitor's real IP to FastAPI

proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
# Chain of proxy IPs

proxy_set_header X-Forwarded-Proto $scheme;
# Whether request was HTTP or HTTPS

proxy_set_header X-Forwarded-Host $host;
# Original host header
```

Without these, FastAPI would see all requests as coming from `127.0.0.1`.

## Adding HTTPS (SSL)

### Option 1: Using Let's Encrypt (Free, Recommended)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Follow prompts and choose:
# - Enter email address
# - Agree to terms
# - Choose whether to redirect HTTP → HTTPS (recommended: yes)
```

Certbot will automatically:
- Create SSL certificates
- Update your Nginx config
- Setup auto-renewal

Test auto-renewal:
```bash
sudo certbot renew --dry-run
```

### Option 2: Manual SSL Configuration

Uncomment the SSL server block in `python-app.conf` and configure paths to your certificates.

## Multiple Applications Example

You can serve multiple apps from one server:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # FastAPI app
    location /python {
        proxy_pass http://localhost:5000;
        # ... headers ...
    }

    # Another API (Node.js, Django, etc.)
    location /api {
        proxy_pass http://localhost:3000;
        # ... headers ...
    }

    # Static website
    location / {
        root /var/www/html;
        index index.html;
    }
}
```

## Troubleshooting

### 502 Bad Gateway

**Meaning:** Nginx can't connect to FastAPI

**Fix:**
```bash
# Check if FastAPI is running
sudo systemctl status fastapi-api

# Check if port 5000 is listening
sudo netstat -tulpn | grep 5000

# Check FastAPI logs
sudo journalctl -u fastapi-api -f
```

### 404 Not Found

**Meaning:** Route doesn't exist

**Check:**
1. FastAPI routes have `/python` prefix
2. Nginx `location /python` matches
3. No trailing slash mismatch

### Connection Refused

**Meaning:** Port not accessible

**Fix:**
```bash
# Make sure FastAPI is running on 127.0.0.1:5000
# Check systemd service file
sudo systemctl status fastapi-api

# Check ExecStart line uses:
# --host 127.0.0.1 --port 5000
```

## Testing Configuration

### 1. Nginx syntax test
```bash
sudo nginx -t
```

### 2. Check Nginx is running
```bash
sudo systemctl status nginx
```

### 3. Test from command line
```bash
curl -I http://localhost/python/
# Should return HTTP 200
```

### 4. Test from browser
```
http://your-domain.com/python/
```

### 5. View Nginx logs
```bash
# Error log
sudo tail -f /var/log/nginx/error.log

# Access log
sudo tail -f /var/log/nginx/access.log
```

## Common Commands

```bash
# Test config
sudo nginx -t

# Reload (no downtime)
sudo systemctl reload nginx

# Restart
sudo systemctl restart nginx

# Status
sudo systemctl status nginx

# View error log
sudo tail -f /var/log/nginx/error.log

# View access log
sudo tail -f /var/log/nginx/access.log
```

## Config File Locations

```
Main config:       /etc/nginx/nginx.conf
Sites available:   /etc/nginx/sites-available/
Sites enabled:     /etc/nginx/sites-enabled/
Error log:         /var/log/nginx/error.log
Access log:        /var/log/nginx/access.log
```

## Performance Tuning (Optional)

For high-traffic applications:

```nginx
# Increase worker connections
# Edit /etc/nginx/nginx.conf
worker_processes auto;
worker_connections 2048;

# Enable gzip compression
gzip on;
gzip_types text/plain application/json application/javascript text/css;
gzip_min_length 1000;

# Client body size (for large uploads)
client_max_body_size 10M;
```

## Security Headers (Optional)

Add security headers:

```nginx
location /python {
    proxy_pass http://localhost:5000;
    # ... existing headers ...

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```
