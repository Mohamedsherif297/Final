# Git Auto-Deploy Troubleshooting Guide

## Quick Diagnostics

Run this command to check system status:

```bash
cd ~/surveillance-car
./deployment/test_deployment.sh
```

## Common Issues & Solutions

### 1. Service Won't Start

**Symptoms:**
- `sudo systemctl status git-deploy` shows "failed" or "inactive"
- No deployment happening

**Diagnosis:**
```bash
# Check service status
sudo systemctl status git-deploy

# View detailed logs
journalctl -u git-deploy -n 50

# Check for errors
journalctl -u git-deploy | grep -i error
```

**Solutions:**

**A. Service file not found**
```bash
# Copy service file
sudo cp ~/surveillance-car/deployment/git-deploy.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable git-deploy
sudo systemctl start git-deploy
```

**B. Permission issues**
```bash
# Fix ownership
sudo chown -R pi:pi ~/surveillance-car

# Fix permissions
chmod +x ~/surveillance-car/deployment/*.py
chmod +x ~/surveillance-car/deployment/*.sh
```

**C. Python not found**
```bash
# Check Python path
which python3

# Update service file if needed
sudo nano /etc/systemd/system/git-deploy.service
# Change ExecStart path to match your Python location
```

---

### 2. Git Pull Fails

**Symptoms:**
- Logs show "Failed to pull changes"
- "Permission denied" errors
- "Merge conflict" errors

**Diagnosis:**
```bash
cd ~/surveillance-car

# Check Git status
git status

# Check remote
git remote -v

# Try manual pull
git pull origin main
```

**Solutions:**

**A. Authentication issues**
```bash
# Setup SSH keys
ssh-keygen -t ed25519 -C "pi@raspberrypi"
cat ~/.ssh/id_ed25519.pub
# Add this key to GitHub/GitLab

# Test SSH connection
ssh -T git@github.com
# or
ssh -T git@gitlab.com
```

**B. Local changes conflict**
```bash
# Stash local changes
git stash

# Pull changes
git pull origin main

# Apply stashed changes (optional)
git stash pop
```

**C. Detached HEAD state**
```bash
# Checkout main branch
git checkout main

# Pull changes
git pull origin main
```

**D. Reset to remote (WARNING: loses local changes)**
```bash
# Fetch latest
git fetch origin

# Reset to remote
git reset --hard origin/main
```

---

### 3. Webhook Not Receiving Events

**Symptoms:**
- Push to Git but no deployment
- Webhook shows error in GitHub/GitLab
- Can't access webhook URL

**Diagnosis:**
```bash
# Check if service is running
sudo systemctl status webhook-listener

# Check if port is open
sudo netstat -tulpn | grep 8080

# Test locally
curl -X POST http://localhost:8080/webhook/manual

# Check logs
tail -f ~/surveillance-car/logs/webhook.log
```

**Solutions:**

**A. Service not running**
```bash
# Start service
sudo systemctl start webhook-listener

# Enable on boot
sudo systemctl enable webhook-listener

# Check status
sudo systemctl status webhook-listener
```

**B. Port blocked by firewall**
```bash
# Check firewall status
sudo ufw status

# Allow port 8080
sudo ufw allow 8080

# Reload firewall
sudo ufw reload
```

**C. Port forwarding not configured**
```bash
# Get Pi's local IP
hostname -I

# Configure router to forward port 8080 to Pi's IP
# (This is done in your router's admin panel)

# Test from outside network
curl -X POST http://YOUR_PUBLIC_IP:8080/health
```

**D. Wrong webhook URL**
```bash
# Get Pi's IP
hostname -I

# Webhook URL should be:
# http://YOUR_PI_IP:8080/webhook/github (for GitHub)
# http://YOUR_PI_IP:8080/webhook/gitlab (for GitLab)

# Update in GitHub/GitLab webhook settings
```

**E. Invalid webhook secret**
```bash
# Check service file
sudo cat /etc/systemd/system/webhook-listener.service | grep WEBHOOK_SECRET

# Update secret in GitHub/GitLab to match
# Or update service file:
sudo nano /etc/systemd/system/webhook-listener.service
# Change: Environment="WEBHOOK_SECRET=your-secret"

# Restart service
sudo systemctl daemon-reload
sudo systemctl restart webhook-listener
```

---

### 4. Dependencies Not Installing

**Symptoms:**
- Logs show "Failed to install dependencies"
- Import errors when running code
- "No module named..." errors

**Diagnosis:**
```bash
# Check if requirements.txt exists
ls -la ~/surveillance-car/requirements.txt

# Try manual install
cd ~/surveillance-car
pip3 install -r requirements.txt
```

**Solutions:**

**A. pip not installed**
```bash
# Install pip
sudo apt-get update
sudo apt-get install python3-pip

# Upgrade pip
pip3 install --upgrade pip
```

**B. Permission issues**
```bash
# Install as user (not system-wide)
pip3 install -r requirements.txt --user

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**C. Network issues**
```bash
# Check internet connection
ping -c 3 google.com

# Try with timeout
pip3 install -r requirements.txt --timeout 60
```

**D. Specific package fails**
```bash
# Install packages one by one
cat requirements.txt | xargs -n 1 pip3 install

# Skip failing packages
pip3 install -r requirements.txt --ignore-installed
```

---

### 5. Deployment Runs But Code Doesn't Update

**Symptoms:**
- Logs show "Deployment completed successfully"
- But code changes not visible
- Old code still running

**Diagnosis:**
```bash
cd ~/surveillance-car

# Check current commit
git log -1

# Check if files changed
git diff HEAD~1

# Check if service restarted
sudo systemctl status surveillance-car
```

**Solutions:**

**A. Service not restarted**
```bash
# Manually restart service
sudo systemctl restart surveillance-car

# Or restart main script
pkill -f main.py
python3 ~/surveillance-car/main.py
```

**B. Python cache not cleared**
```bash
# Clear Python cache
find ~/surveillance-car -type d -name __pycache__ -exec rm -rf {} +
find ~/surveillance-car -type f -name "*.pyc" -delete

# Restart service
sudo systemctl restart surveillance-car
```

**C. Wrong branch**
```bash
# Check current branch
git branch

# Switch to correct branch
git checkout main

# Pull changes
git pull origin main
```

---

### 6. Logs Not Showing

**Symptoms:**
- Log files empty or not created
- Can't see deployment activity

**Diagnosis:**
```bash
# Check if logs directory exists
ls -la ~/surveillance-car/logs/

# Check log file permissions
ls -la ~/surveillance-car/logs/*.log

# Try to write to log
echo "test" >> ~/surveillance-car/logs/git_deploy.log
```

**Solutions:**

**A. Logs directory doesn't exist**
```bash
# Create logs directory
mkdir -p ~/surveillance-car/logs

# Set permissions
chmod 755 ~/surveillance-car/logs
```

**B. Permission issues**
```bash
# Fix ownership
sudo chown -R pi:pi ~/surveillance-car/logs

# Fix permissions
chmod 644 ~/surveillance-car/logs/*.log
```

**C. View systemd logs instead**
```bash
# View service logs
journalctl -u git-deploy -f
journalctl -u webhook-listener -f

# View last 50 lines
journalctl -u git-deploy -n 50
```

---

### 7. Deployment Too Slow

**Symptoms:**
- Deployment takes several minutes
- System becomes unresponsive during deployment

**Diagnosis:**
```bash
# Check deployment time in logs
tail -50 ~/surveillance-car/logs/git_deploy.log

# Check system resources
top
free -h
df -h
```

**Solutions:**

**A. Large repository**
```bash
# Use shallow clone
git fetch --depth=1

# Clean up old commits
git gc --aggressive
```

**B. Many dependencies**
```bash
# Use binary packages instead of building
sudo apt-get install python3-numpy python3-opencv

# Or use pip cache
pip3 install -r requirements.txt --cache-dir ~/.cache/pip
```

**C. Slow network**
```bash
# Increase Git timeout
git config --global http.postBuffer 524288000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999
```

---

### 8. Multiple Deployments Running

**Symptoms:**
- Logs show overlapping deployments
- "Already up to date" but still deploying
- Resource usage high

**Diagnosis:**
```bash
# Check running processes
ps aux | grep git_auto_deploy

# Check service status
sudo systemctl status git-deploy
sudo systemctl status webhook-listener
```

**Solutions:**

**A. Kill duplicate processes**
```bash
# Kill all deployment processes
pkill -f git_auto_deploy.py

# Restart service cleanly
sudo systemctl restart git-deploy
```

**B. Adjust check interval**
```bash
# Edit service file
sudo nano /etc/systemd/system/git-deploy.service

# Increase interval (e.g., 600 seconds = 10 minutes)
# Change: --interval 300 to --interval 600

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart git-deploy
```

---

### 9. Post-Deploy Script Fails

**Symptoms:**
- Logs show "Post-deployment script failed"
- Custom actions not executing

**Diagnosis:**
```bash
# Check if script exists
ls -la ~/surveillance-car/deployment/post_deploy.sh

# Check if executable
ls -la ~/surveillance-car/deployment/post_deploy.sh | grep x

# Try running manually
bash ~/surveillance-car/deployment/post_deploy.sh
```

**Solutions:**

**A. Script not executable**
```bash
# Make executable
chmod +x ~/surveillance-car/deployment/post_deploy.sh
```

**B. Script has errors**
```bash
# Check for syntax errors
bash -n ~/surveillance-car/deployment/post_deploy.sh

# Run with debug output
bash -x ~/surveillance-car/deployment/post_deploy.sh
```

**C. Missing dependencies**
```bash
# Check what commands script uses
cat ~/surveillance-car/deployment/post_deploy.sh

# Install missing commands
# Example: sudo apt-get install mosquitto-clients
```

---

### 10. Emergency: Rollback to Previous Version

**Symptoms:**
- New deployment broke something
- Need to revert quickly

**Solution:**

```bash
cd ~/surveillance-car

# View recent commits
git log --oneline -10

# Rollback to previous commit
git reset --hard HEAD~1

# Or rollback to specific commit
git reset --hard COMMIT_HASH

# Force update remote (if needed)
git push origin main --force

# Restart service
sudo systemctl restart surveillance-car

# Or restart main script
pkill -f main.py
python3 ~/surveillance-car/main.py
```

---

## Diagnostic Commands

### System Health Check

```bash
#!/bin/bash
echo "=== Git Auto-Deploy Diagnostics ==="
echo ""

echo "1. Service Status:"
sudo systemctl status git-deploy --no-pager | head -10
sudo systemctl status webhook-listener --no-pager | head -10
echo ""

echo "2. Git Status:"
cd ~/surveillance-car
git status
git remote -v
echo ""

echo "3. Recent Deployments:"
tail -20 ~/surveillance-car/logs/git_deploy.log
echo ""

echo "4. Network:"
hostname -I
sudo netstat -tulpn | grep 8080
echo ""

echo "5. Disk Space:"
df -h | grep -E "Filesystem|/$"
echo ""

echo "6. Python:"
python3 --version
pip3 --version
echo ""

echo "=== End Diagnostics ==="
```

Save this as `diagnose.sh` and run:
```bash
chmod +x diagnose.sh
./diagnose.sh
```

---

## Getting Help

### Collect Information

Before asking for help, collect this information:

```bash
# 1. Service status
sudo systemctl status git-deploy > ~/debug_info.txt
sudo systemctl status webhook-listener >> ~/debug_info.txt

# 2. Recent logs
tail -100 ~/surveillance-car/logs/git_deploy.log >> ~/debug_info.txt
tail -100 ~/surveillance-car/logs/webhook.log >> ~/debug_info.txt

# 3. Git status
cd ~/surveillance-car
git status >> ~/debug_info.txt
git log -5 --oneline >> ~/debug_info.txt

# 4. System info
uname -a >> ~/debug_info.txt
python3 --version >> ~/debug_info.txt

# View collected info
cat ~/debug_info.txt
```

### Reset Everything

If all else fails, reset the deployment system:

```bash
# Stop services
sudo systemctl stop git-deploy
sudo systemctl stop webhook-listener

# Remove services
sudo systemctl disable git-deploy
sudo systemctl disable webhook-listener
sudo rm /etc/systemd/system/git-deploy.service
sudo rm /etc/systemd/system/webhook-listener.service
sudo systemctl daemon-reload

# Reset Git repository
cd ~/surveillance-car
git fetch origin
git reset --hard origin/main
git clean -fd

# Re-run setup
./deployment/setup_git_deploy.sh
```

---

## Prevention Tips

### 1. Test Before Deploying

```bash
# Create a test branch
git checkout -b test
git push origin test

# Configure Pi to use test branch
python3 deployment/git_auto_deploy.py --branch test

# Test changes, then merge to main
```

### 2. Monitor Logs Regularly

```bash
# Add to crontab for daily log summary
0 9 * * * tail -50 ~/surveillance-car/logs/git_deploy.log | mail -s "Daily Deployment Log" your@email.com
```

### 3. Backup Before Major Changes

```bash
# Backup current version
cp -r ~/surveillance-car ~/surveillance-car-backup-$(date +%Y%m%d)

# Or use Git tags
git tag -a v1.0 -m "Stable version"
git push origin v1.0
```

### 4. Use Health Checks

```bash
# Add to post_deploy.sh
#!/bin/bash

# Test if main script runs
timeout 5 python3 ~/surveillance-car/main.py --test

if [ $? -ne 0 ]; then
    echo "Health check failed! Rolling back..."
    git reset --hard HEAD~1
    exit 1
fi
```

---

**Still having issues? Check the complete guide: `GIT_AUTO_DEPLOY_GUIDE.md`**
