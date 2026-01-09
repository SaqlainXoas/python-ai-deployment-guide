# GitHub Actions Deployment Workflow

This workflow automatically deploys your FastAPI application when you push to the `main` branch.

## Setup Instructions

### 1. Copy workflow file to your repository

```bash
# In your project root
mkdir -p .github/workflows
cp deploy.yml .github/workflows/
```

### 2. Generate SSH key pair

On your **local machine**:

```bash
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions_key
```

This creates two files:
- `github_actions_key` - Private key (for GitHub Secrets)
- `github_actions_key.pub` - Public key (for server)

### 3. Add public key to server

```bash
# View public key
cat ~/.ssh/github_actions_key.pub

# Copy the output, then SSH to your server:
ssh your-user@your-server

# Add public key to authorized_keys
echo "paste-public-key-here" >> ~/.ssh/authorized_keys

# Set correct permissions
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### 4. Add GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these three secrets:

#### SSH_HOST
Your server IP address or domain name
```
Example: 203.0.113.42
Or: example.com
```

#### SSH_USER
Your server username
```
Example: ubuntu
Or: your-username
```

#### SSH_KEY
Your private key (entire content)
```bash
# On your local machine, copy the private key:
cat ~/.ssh/github_actions_key

# Copy ENTIRE output including:
# -----BEGIN OPENSSH PRIVATE KEY-----
# ... multiple lines ...
# -----END OPENSSH PRIVATE KEY-----
```

Paste the entire content into the `SSH_KEY` secret.

### 5. Enable passwordless sudo for service restart

On your **server**, allow restarting services without password:

```bash
sudo visudo
```

Add these lines at the end (replace `ubuntu` with your username):

```
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl restart fastapi-api
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl restart celery-worker
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl is-active fastapi-api
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl is-active celery-worker
```

Save and exit (`Ctrl+X`, `Y`, `Enter`).

### 6. Test the workflow

```bash
# Make a small change
echo "# Test deployment" >> README.md

# Commit and push
git add .
git commit -m "test: GitHub Actions deployment"
git push origin main
```

### 7. Monitor deployment

1. Go to your repository on GitHub
2. Click **Actions** tab
3. See your workflow running
4. Click on the workflow to view logs

## What This Workflow Does

1. **Triggers** when code is pushed to `main` branch
2. **Connects** to your server via SSH using GitHub Secrets
3. **Pulls** latest code: `git pull origin main`
4. **Activates** venv: `source venv/bin/activate`
5. **Installs** dependencies: `pip install -r requirements.txt`
6. **Restarts** services: `sudo systemctl restart fastapi-api celery-worker`
7. **Verifies** services are running

## Important Notes

### venv is NOT created in workflow

The virtual environment is created **once** during initial setup.

The workflow only:
- ✅ Activates existing venv
- ✅ Installs/updates packages inside it

It does **NOT**:
- ❌ Create venv (`python3 -m venv venv`)
- ❌ Delete and recreate venv

### Project path must match

The workflow uses `/python-hosting/my-api`. If your project is elsewhere, update:

```yaml
script: |
  cd /path/to/your/project  # Change this
  git pull origin main
  # ... rest stays the same
```

## Workflow Customization

### Deploy to different branch

```yaml
on:
  push:
    branches:
      - production  # Deploy on push to 'production' branch
```

### Add health check

```yaml
script: |
  cd /python-hosting/my-api
  git pull origin main
  source venv/bin/activate
  pip install -r requirements.txt
  sudo systemctl restart fastapi-api celery-worker

  # Wait for services to start
  sleep 5

  # Health check endpoint
  curl -f http://localhost:5000/python/ || exit 1
```

### Run tests before deploying

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: |
          pip install -r requirements.txt
          pytest tests/

  deploy:
    needs: test  # Only deploy if tests pass
    runs-on: ubuntu-latest
    steps:
      # ... deployment steps ...
```

### Add Slack/Discord notification

```yaml
- name: Notify on success
  if: success()
  run: |
    curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
      -H 'Content-Type: application/json' \
      -d '{"text":"Deployment successful! ✅"}'

- name: Notify on failure
  if: failure()
  run: |
    curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
      -H 'Content-Type: application/json' \
      -d '{"text":"Deployment failed! ❌"}'
```

## Troubleshooting

### "Permission denied (publickey)"

**Fix:**
1. Make sure public key is in `~/.ssh/authorized_keys` on server
2. Check SSH_KEY secret contains **private key** (not public)
3. Verify correct username in SSH_USER secret

```bash
# Test SSH connection manually
ssh -i ~/.ssh/github_actions_key your-user@your-server
```

### "sudo: a password is required"

**Fix:** Add NOPASSWD to sudoers (see step 5 above)

### "fatal: not a git repository"

**Fix:** Make sure `/python-hosting/my-api` contains your git repository

```bash
ssh your-user@your-server
cd /python-hosting/my-api
git status  # Should show git repo info
```

### Changes not visible after deployment

**Check:**
1. Services actually restarted: `sudo systemctl status fastapi-api`
2. No errors in logs: `sudo journalctl -u fastapi-api -f`
3. Latest commit pulled: `cd /python-hosting/my-api && git log -1`

### Workflow fails on "git pull"

**Possible causes:**
- Uncommitted changes on server
- Merge conflicts

**Fix:**
```bash
# On server
cd /python-hosting/my-api
git status

# If uncommitted changes:
git stash

# Or reset to remote:
git reset --hard origin/main
```

## Security Best Practices

1. **Use deploy keys** instead of personal SSH keys
2. **Limit sudo permissions** to only required commands
3. **Use environment-specific secrets** (production vs staging)
4. **Enable branch protection** on `main` branch
5. **Review deployment logs** regularly

## Manual Deployment (if workflow fails)

If GitHub Actions fails, you can deploy manually:

```bash
ssh your-user@your-server
cd /python-hosting/my-api
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart fastapi-api celery-worker
```

## Monitoring Deployments

### View deployment history
- GitHub → **Actions** tab → See all workflow runs

### Check deployment logs
- Click on workflow run → See detailed logs

### Check server logs
```bash
ssh your-user@your-server
sudo journalctl -u fastapi-api -f
```

## Advanced: Multiple Environments

Deploy to staging and production:

```yaml
name: Deploy

on:
  push:
    branches:
      - main
      - staging

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Set environment
        id: env
        run: |
          if [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
            echo "server=${{ secrets.PROD_SSH_HOST }}" >> $GITHUB_OUTPUT
          else
            echo "server=${{ secrets.STAGING_SSH_HOST }}" >> $GITHUB_OUTPUT
          fi

      - name: Deploy
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ steps.env.outputs.server }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /python-hosting/my-api
            git pull origin ${{ github.ref_name }}
            source venv/bin/activate
            pip install -r requirements.txt
            sudo systemctl restart fastapi-api celery-worker
```

## Quick Reference

### Required GitHub Secrets
```
SSH_HOST     = your-server-ip
SSH_USER     = your-username
SSH_KEY      = private-key-content
```

### Required sudoers entries
```
your-user ALL=(ALL) NOPASSWD: /bin/systemctl restart fastapi-api
your-user ALL=(ALL) NOPASSWD: /bin/systemctl restart celery-worker
```

### Workflow file location
```
.github/workflows/deploy.yml
```

### Test deployment
```bash
git push origin main
# Check: github.com/your-repo/actions
```
