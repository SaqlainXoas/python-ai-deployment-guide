# Initial Server Setup

> **Run these steps ONCE when you first get SSH access to your VM**

---

## Prerequisites

- Fresh Ubuntu 20.04+ VM with SSH access
- Root or sudo privileges
- Your GitHub repository URL ready

---

## Step 1: SSH into Server

```bash
ssh your-user@your-server-ip
```

---

## Step 2: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

**Why?** Prevents dependency conflicts and security issues.

---

## Step 3: Install Python 3 and pip

```bash
sudo apt install -y python3 python3-venv python3-pip
```

Verify installation:
```bash
python3 --version
# Expected: Python 3.8.10 or higher
```

---

## Step 4: Install Redis

```bash
sudo apt install -y redis-server
```

Start Redis and enable on boot:
```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

Verify Redis is running:
```bash
redis-cli ping
```
**Expected output:** `PONG`

---

## Step 5: Install Nginx

```bash
sudo apt install -y nginx
```

Start Nginx:
```bash
sudo systemctl enable nginx
sudo systemctl start nginx
```

Verify:
```bash
sudo systemctl status nginx
# Should show "active (running)"
```

---

## Step 6: Create Project Directory

```bash
sudo mkdir -p /python-hosting/my-api
sudo chown -R $USER:$USER /python-hosting/my-api
cd /python-hosting/my-api
```

**Path choice:** `/python-hosting/<project-name>`
- Replace `my-api` with your actual project name
- Keeps all Python projects organized under one parent directory
- Matches systemd service paths and CI/CD workflows

**Note:** Common alternatives include `/var/www/app` or `/opt/app` - pick one and stay consistent across your configs.

---

## Step 7: Clone Your Repository

```bash
git clone https://github.com/your-username/your-repo.git .
```

**Note:** The `.` at the end clones into current directory.

---

## Step 8: Create Virtual Environment (IMPORTANT!)

```bash
python3 -m venv venv
```

**Critical:** This is done **ONCE** and **NEVER** in GitHub Actions workflow!

Verify:
```bash
ls venv/
# Should see: bin/ include/ lib/ pyvenv.cfg
```

---

## Step 9: Install Python Dependencies

```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

**Why activate then deactivate?**
- We install packages inside venv
- But systemd will use absolute paths (`venv/bin/python`)
- No need to keep it activated

---

## Verification Checklist

Before proceeding, verify:

- [ ] Python 3 installed: `python3 --version`
- [ ] Redis running: `redis-cli ping` returns `PONG`
- [ ] Nginx running: `sudo systemctl status nginx` shows active
- [ ] Project cloned: `ls /python-hosting/my-api` shows your code
- [ ] venv created: `ls /python-hosting/my-api/venv` exists
- [ ] Dependencies installed: `venv/bin/pip list` shows your packages

---

## What's Next?

Your server is now ready! Next steps:
1. [Setup FastAPI Application](02-fastapi-setup.md)
2. [Create systemd Services](03-systemd-services.md)
3. [Configure Nginx](04-nginx-config.md)

---

## Common Issues

### Redis not starting?
```bash
sudo journalctl -u redis-server -f
```

### Permission denied on project directory?
```bash
sudo chown -R $USER:$USER /python-hosting/my-api
```

### Python not found?
```bash
which python3
# Should show: /usr/bin/python3
```
