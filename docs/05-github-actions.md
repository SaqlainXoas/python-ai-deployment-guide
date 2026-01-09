# GitHub Actions CI/CD Pipeline

> **Automate deployments on every git push**

---

## What is CI/CD?

**CI/CD = Continuous Integration / Continuous Deployment**

```mermaid
graph LR
    Dev[Developer] -->|git push| GH[GitHub]
    GH -->|trigger| Action[GitHub Actions]
    Action -->|SSH| VM[VM Server]
    VM -->|git pull| Code[Update Code]
    Code -->|pip install| Deps[Install Dependencies]
    Deps -->|systemctl restart| Services[Restart Services]
    Services -->|running| Live[Live Application]

    style GH fill:#2196F3
    style Action fill:#FF9800
    style Live fill:#4CAF50
```

---

## How It Works

### Manual Deployment (Before)
```bash
# Every time you change code:
ssh user@server
cd /python-hosting/my-api
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart fastapi-api
sudo systemctl restart celery-worker
```

### Automated Deployment (With GitHub Actions)
```bash
# You only do:
git add .
git commit -m "update feature"
git push

# GitHub Actions automatically does the rest!
```

---

## What GitHub Actions Does

✅ **Does:**
- SSH into your server
- Pull latest code (`git pull`)
- Install new dependencies (`pip install -r requirements.txt`)
- Restart services (`systemctl restart`)

❌ **Does NOT:**
- Install Python (done once in initial setup)
- Create venv (done once in initial setup)
- Install Redis/Nginx (done once in initial setup)

---

## Step 1: Generate SSH Key for GitHub Actions

On your **local machine**:

```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions_key

# This creates:
# - github_actions_key (private key) - for GitHub Secrets
# - github_actions_key.pub (public key) - for server
```

---

## Step 2: Add Public Key to Server

Copy the **public key** to your server:

```bash
# View public key
cat ~/.ssh/github_actions_key.pub

# Copy the output, then SSH to server:
ssh user@your-server

# Add to authorized_keys
echo "paste-public-key-here" >> ~/.ssh/authorized_keys

# Set correct permissions
chmod 600 ~/.ssh/authorized_keys
```

---

## Step 3: Add Secrets to GitHub

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `SSH_HOST` | Your server IP or domain | `203.0.113.42` |
| `SSH_USER` | Your server username | `ubuntu` |
| `SSH_KEY` | Private key content | Copy from `~/.ssh/github_actions_key` |

### Getting the Private Key:

```bash
# On your local machine
cat ~/.ssh/github_actions_key

# Copy ENTIRE output including:
# -----BEGIN OPENSSH PRIVATE KEY-----
# ... (multiple lines)
# -----END OPENSSH PRIVATE KEY-----
```

Paste the **entire content** into `SSH_KEY` secret.

---

## Step 4: Create GitHub Actions Workflow

In your repository, create:
```
.github/
└── workflows/
    └── deploy.yml
```

**Template:** See [examples/github-actions/deploy.yml](../examples/github-actions/deploy.yml)

### Basic Workflow:

```yaml
name: Deploy to VPS

on:
  push:
    branches:
      - main  # Trigger on push to main branch

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Deploy to Server
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /python-hosting/my-api
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            sudo systemctl restart fastapi-api
            sudo systemctl restart celery-worker
```

---

## Understanding the Workflow

### Trigger:
```yaml
on:
  push:
    branches:
      - main
```
**Meaning:** Run this workflow when code is pushed to `main` branch.

---

### SSH Action:
```yaml
uses: appleboy/ssh-action@v1.0.0
with:
  host: ${{ secrets.SSH_HOST }}
  username: ${{ secrets.SSH_USER }}
  key: ${{ secrets.SSH_KEY }}
```
**Meaning:** Connect to your server using SSH with credentials from GitHub Secrets.

---

### Deployment Script:
```bash
cd /python-hosting/my-api                    # Go to project directory
git pull origin main               # Get latest code
source venv/bin/activate           # Activate virtual environment
pip install -r requirements.txt    # Install/update dependencies
sudo systemctl restart fastapi-api # Restart FastAPI
sudo systemctl restart celery-worker # Restart Celery
```

---

## Important: venv Usage in Workflow

### ✅ Correct (activate venv, then install):

```yaml
script: |
  cd /python-hosting/my-api
  source venv/bin/activate
  pip install -r requirements.txt
```

### ❌ Wrong (Don't create venv!):

```yaml
script: |
  cd /python-hosting/my-api
  python3 -m venv venv  # ❌ NO! venv already exists from initial setup
```

**Remember:**
- venv is created **ONCE** during initial setup
- GitHub Actions only **activates** it to install packages

---

## Step 5: Enable Passwordless sudo for Service Restart

GitHub Actions needs to restart services without password prompt:

```bash
# On your server
sudo visudo

# Add this line at the end (replace 'ubuntu' with your user):
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl restart fastapi-api
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl restart celery-worker
```

**Security note:** This only allows restarting these specific services without password.

---

## Step 6: Test Your Pipeline

```bash
# On your local machine
echo "# Test deployment" >> README.md
git add .
git commit -m "test: CI/CD pipeline"
git push origin main
```

### Watch the deployment:
1. Go to your GitHub repository
2. Click **Actions** tab
3. See your workflow running
4. Check logs for any errors

---

## Monitoring Deployments

### GitHub Actions Interface:

```mermaid
graph TB
    Push[git push] --> Trigger[Workflow Triggered]
    Trigger --> Run[Job: deploy]
    Run --> Step1[Connect via SSH]
    Step1 --> Step2[git pull]
    Step2 --> Step3[pip install]
    Step3 --> Step4[restart services]
    Step4 --> Success[✅ Deployment Complete]

    style Success fill:#4CAF50
    style Push fill:#2196F3
```

### In GitHub UI:
- ✅ Green checkmark = deployment successful
- ❌ Red X = deployment failed (check logs)
- 🟡 Yellow dot = deployment in progress

---

## Advanced: Deployment with Tests

```yaml
name: Deploy to VPS

on:
  push:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest tests/

  deploy:
    needs: test  # Only deploy if tests pass
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Server
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /python-hosting/my-api
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            sudo systemctl restart fastapi-api
            sudo systemctl restart celery-worker
```

---

## Troubleshooting

### Deployment fails: "Permission denied (publickey)"

**Fix:**
```bash
# Make sure public key is on server
cat ~/.ssh/authorized_keys

# Check SSH_KEY secret contains private key
# (entire content including BEGIN/END lines)
```

---

### Deployment fails: "sudo: a password is required"

**Fix:**
```bash
# Add NOPASSWD to sudoers (see Step 5)
sudo visudo
```

---

### Code updated but changes not visible

**Fix:**
```bash
# Check if services actually restarted
ssh user@server
sudo systemctl status fastapi-api

# Check logs for errors
sudo journalctl -u fastapi-api -f
```

---

### Git pull fails: "uncommitted changes"

**Fix:**
```bash
# On server, you might have local changes
cd /python-hosting/my-api
git status

# If you see uncommitted changes, stash them:
git stash

# Or reset to remote:
git reset --hard origin/main
```

---

## Deployment Best Practices

### 1. Use environment-specific branches
```yaml
on:
  push:
    branches:
      - main        # Production
      - staging     # Staging environment
```

### 2. Add deployment notifications
```yaml
- name: Notify deployment
  if: success()
  run: |
    curl -X POST your-slack-webhook \
      -d '{"text":"Deployment successful!"}'
```

### 3. Add health check
```yaml
script: |
  cd /python-hosting/my-api
  git pull origin main
  source venv/bin/activate
  pip install -r requirements.txt
  sudo systemctl restart fastapi-api
  sudo systemctl restart celery-worker

  # Wait for service to start
  sleep 5

  # Health check
  curl -f http://localhost:5000/python/ || exit 1
```

---

## What's Next?

Your CI/CD is set up! Now:
1. [Monitoring & Logs](06-monitoring.md) - Track your application

---

## Quick Reference

### GitHub Secrets Required
```
SSH_HOST = your-server-ip
SSH_USER = your-username
SSH_KEY = private-key-content
```

### Workflow File Location
```
.github/workflows/deploy.yml
```

### Test Deployment
```bash
git push origin main
# Then check: github.com/your-repo/actions
```

### Essential Commands (on server)
```bash
# View deployment logs
sudo journalctl -u fastapi-api -f

# Check service status
sudo systemctl status fastapi-api

# Manual deployment
cd /python-hosting/my-api && git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart fastapi-api celery-worker
```
