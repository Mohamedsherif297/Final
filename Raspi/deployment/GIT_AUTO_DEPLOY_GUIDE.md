# Git Auto-Deploy Guide for Raspberry Pi

Automatically deploy code changes to your Raspberry Pi by simply pushing to Git!

## 📋 Overview

This system provides three ways to automatically deploy code to your Raspberry Pi:

1. **Periodic Auto-Pull** - Checks for updates every 5 minutes
2. **Webhook Listener** - Deploys immediately when you push to GitHub/GitLab
3. **Manual Trigger** - Deploy on-demand via command or API

## 🚀 Quick Setup

### Step 1: Copy Files to Raspberry Pi

```bash
# From your computer
scp -r Final/Raspi pi@raspberrypi.local:~/surveillance-car
```

### Step 2: SSH into Raspberry Pi

```bash
ssh pi@raspberrypi.local
cd ~/surveillance-car
```

### Step 3: Run Setup Script

```bash
chmod +x deployment/setup_git_deploy.sh
./deployment/setup_git_deploy.sh
```

The script will guide you through:
- Initializing Git repository (if needed)
- Installing dependencies
- Choosing deployment method
- Configuring services

### Step 4: Push Changes

```bash
# On your development computer
git add .
git commit -m "Update code"
git push origin main
```

Your Raspberry Pi will automatically pull and deploy the changes! 🎉

---

## 📖 Detailed Setup

### Method 1: Periodic Auto-Pull (Recommended for Beginners)

Automatically checks for updates every 5 minutes.

#### Setup

```bash
cd ~/surveillance-car

# Install as systemd service
sudo cp deployment/git-deploy.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable git-deploy.service
sudo systemctl start git-deploy.service
```

#### Verify

```bash
# Check service status
sudo systemctl status git-deploy

# View logs
journalctl -u git-deploy -f
```

#### Configuration

Edit `/etc/systemd/system/git-deploy.service` to change check interval:

```ini
# Change --interval 300 (5 minutes) to your preferred seconds
ExecStart=/usr/bin/python3 /home/pi/surveillance-car/deployment/git_auto_deploy.py --watch --interval 300
```

Then restart:
```bash
sudo systemctl restart git-deploy
```

---

### Method 2: Webhook Listener (Recommended for Instant Deployment)

Deploys immediately when you push to GitHub or GitLab.

#### Setup on Raspberry Pi

```bash
cd ~/surveillance-car

# Install Flask
pip3 install flask --user

# Set your webhook secret
export WEBHOOK_SECRET="your-super-secret-key"

# Update service file
sudo nano /etc/systemd/system/webhook-listener.service
# Change: Environment="WEBHOOK_SECRET=your-super-secret-key"

# Install service
sudo cp deployment/webhook-listener.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable webhook-listener.service
sudo systemctl start webhook-listener.service
```

#### Get Your Raspberry Pi IP

```bash
hostname -I
# Example output: 192.168.1.100
```

#### Configure GitHub Webhook

1. Go to your GitHub repository
2. Settings → Webhooks → Add webhook
3. Configure:
   - **Payload URL**: `http://YOUR_PI_IP:8080/webhook/github`
   - **Content type**: `application/json`
   - **Secret**: Your webhook secret
   - **Events**: Just the push event
4. Click "Add webhook"

#### Configure GitLab Webhook

1. Go to your GitLab repository
2. Settings → Webhooks
3. Configure:
   - **URL**: `http://YOUR_PI_IP:8080/webhook/gitlab`
   - **Secret token**: Your webhook secret
   - **Trigger**: Push events
4. Click "Add webhook"

#### Port Forwarding (If Raspberry Pi is Behind Router)

If your Pi is behind a router and you want webhooks from the internet:

1. Log into your router
2. Forward port 8080 to your Raspberry Pi's local IP
3. Use your public IP in webhook URL: `http://YOUR_PUBLIC_IP:8080/webhook/github`

**Security Note**: Use a strong webhook secret and consider using a VPN or Cloudflare Tunnel for better security.

#### Verify

```bash
# Check service status
sudo systemctl status webhook-listener

# View logs
journalctl -u webhook-listener -f

# Test manually (from Pi)
curl -X POST http://localhost:8080/webhook/manual
```

---

### Method 3: Cron Job (Alternative)

Use cron for scheduled checks without systemd.

```bash
# Edit crontab
crontab -e

# Add this line (checks every 5 minutes)
*/5 * * * * cd /home/pi/surveillance-car && python3 deployment/git_auto_deploy.py >> logs/git_deploy.log 2>&1

# Or check every hour
0 * * * * cd /home/pi/surveillance-car && python3 deployment/git_auto_deploy.py >> logs/git_deploy.log 2>&1
```

View logs:
```bash
tail -f ~/surveillance-car/logs/git_deploy.log
```

---

## 🎮 Usage

### Manual Deployment

```bash
# Run deployment manually
cd ~/surveillance-car
python3 deployment/git_auto_deploy.py

# Or with custom branch
python3 deployment/git_auto_deploy.py --branch develop
```

### Check Status

```bash
# View service status
sudo systemctl status git-deploy
sudo systemctl status webhook-listener

# View logs
tail -f ~/surveillance-car/logs/git_deploy.log
tail -f ~/surveillance-car/logs/webhook.log

# View systemd logs
journalctl -u git-deploy -f
journalctl -u webhook-listener -f
```

### Restart Services

```bash
# Restart auto-pull service
sudo systemctl restart git-deploy

# Restart webhook listener
sudo systemctl restart webhook-listener
```

### Stop Services

```bash
# Stop auto-pull
sudo systemctl stop git-deploy

# Stop webhook listener
sudo systemctl stop webhook-listener
```

---

## ⚙️ Configuration

### Change Git Branch

Edit the service file or run manually:

```bash
python3 deployment/git_auto_deploy.py --branch your-branch-name
```

### Change Check Interval

Edit `/etc/systemd/system/git-deploy.service`:

```ini
# Change --interval value (in seconds)
ExecStart=/usr/bin/python3 /home/pi/surveillance-car/deployment/git_auto_deploy.py --watch --interval 600
```

Restart service:
```bash
sudo systemctl daemon-reload
sudo systemctl restart git-deploy
```

### Custom Post-Deployment Actions

Edit `deployment/post_deploy.sh`:

```bash
#!/bin/bash
# Add your custom commands here

# Example: Restart MQTT broker
sudo systemctl restart mosquitto

# Example: Clear cache
rm -rf __pycache__

# Example: Run tests
python3 -m pytest tests/
```

Make it executable:
```bash
chmod +x deployment/post_deploy.sh
```

---

## 🔧 How It Works

### Deployment Process

1. **Fetch** - Fetch latest changes from Git remote
2. **Check** - Compare local and remote commits
3. **Pull** - Pull changes if updates available
4. **Dependencies** - Install/update Python packages from requirements.txt
5. **Post-Deploy** - Run custom post-deployment script
6. **Restart** - Restart surveillance car service (if configured)

### What Gets Deployed

- All code changes from your Git repository
- Updated Python dependencies
- Configuration file changes
- New or modified scripts

### What Doesn't Get Deployed

- Local configuration overrides (use `.gitignore`)
- Logs and temporary files
- Virtual environments
- Compiled Python files (`__pycache__`)

---

## 🛡️ Security Best Practices

### 1. Use Strong Webhook Secrets

```bash
# Generate a strong secret
openssl rand -hex 32
```

### 2. Restrict Webhook Access

Only allow webhooks from GitHub/GitLab IPs. Edit webhook listener to add IP filtering.

### 3. Use SSH Keys for Git

```bash
# Generate SSH key on Raspberry Pi
ssh-keygen -t ed25519 -C "pi@raspberrypi"

# Add to GitHub/GitLab
cat ~/.ssh/id_ed25519.pub
```

### 4. Don't Commit Secrets

Add to `.gitignore`:
```
*.env
secrets/
config/local_*.yaml
```

### 5. Use HTTPS or VPN

For webhook listener, consider:
- Cloudflare Tunnel
- Tailscale VPN
- WireGuard VPN

---

## 🐛 Troubleshooting

### Deployment Not Running

```bash
# Check service status
sudo systemctl status git-deploy
sudo systemctl status webhook-listener

# View logs
journalctl -u git-deploy -n 50
journalctl -u webhook-listener -n 50

# Restart services
sudo systemctl restart git-deploy
sudo systemctl restart webhook-listener
```

### Git Pull Fails

```bash
# Check Git status
cd ~/surveillance-car
git status
git remote -v

# Reset to remote state (WARNING: loses local changes)
git fetch origin
git reset --hard origin/main

# Or stash local changes
git stash
git pull origin main
```

### Permission Denied

```bash
# Fix ownership
sudo chown -R pi:pi ~/surveillance-car

# Fix permissions
chmod +x ~/surveillance-car/deployment/*.py
chmod +x ~/surveillance-car/deployment/*.sh
```

### Webhook Not Receiving Events

```bash
# Check if service is running
sudo systemctl status webhook-listener

# Check if port is open
sudo netstat -tulpn | grep 8080

# Test locally
curl -X POST http://localhost:8080/webhook/manual

# Check firewall
sudo ufw status
sudo ufw allow 8080
```

### Dependencies Not Installing

```bash
# Install pip
sudo apt-get install python3-pip

# Upgrade pip
pip3 install --upgrade pip

# Install requirements manually
cd ~/surveillance-car
pip3 install -r requirements.txt --user
```

---

## 📊 Monitoring

### View Deployment History

```bash
# View Git log
cd ~/surveillance-car
git log --oneline -10

# View deployment logs
tail -f logs/git_deploy.log
```

### Check Last Deployment

```bash
# View last commit
git log -1

# View last deployment log
tail -20 logs/git_deploy.log
```

### Monitor in Real-Time

```bash
# Watch deployment logs
watch -n 5 'tail -20 ~/surveillance-car/logs/git_deploy.log'

# Or use journalctl
journalctl -u git-deploy -f
```

---

## 🚀 Advanced Usage

### Deploy Specific Branch

```bash
python3 deployment/git_auto_deploy.py --branch feature/new-feature
```

### Deploy Without Restart

Edit `git_auto_deploy.py` and comment out the restart section.

### Deploy to Multiple Raspberry Pis

Use the same webhook for multiple Pis - each will deploy independently.

### Rollback to Previous Version

```bash
cd ~/surveillance-car

# View commit history
git log --oneline

# Rollback to specific commit
git reset --hard COMMIT_HASH

# Restart service
sudo systemctl restart surveillance-car
```

### Blue-Green Deployment

Create two directories and switch between them:

```bash
# Setup
mkdir ~/surveillance-car-blue
mkdir ~/surveillance-car-green

# Deploy to green while blue is running
cd ~/surveillance-car-green
git pull origin main

# Switch symlink
ln -sfn ~/surveillance-car-green ~/surveillance-car-active

# Restart service pointing to active
sudo systemctl restart surveillance-car
```

---

## 📝 Example Workflow

### Development Workflow

```bash
# On your computer
cd surveillance-car

# Make changes
nano Drivers/hardware/motor/motor_controller.py

# Test locally
python3 -m pytest tests/

# Commit and push
git add .
git commit -m "Improve motor control"
git push origin main

# Raspberry Pi automatically deploys!
```

### Check Deployment on Pi

```bash
# SSH into Pi
ssh pi@raspberrypi.local

# Check logs
tail -f ~/surveillance-car/logs/git_deploy.log

# Verify changes
cd ~/surveillance-car
git log -1
```

---

## 🎯 Tips & Tricks

### 1. Test Before Deploying

Use a separate branch for testing:

```bash
# Create test branch
git checkout -b test
git push origin test

# Configure Pi to track test branch
python3 deployment/git_auto_deploy.py --branch test
```

### 2. Notification on Deployment

Add to `post_deploy.sh`:

```bash
# Send notification via MQTT
mosquitto_pub -h localhost -t system/notifications -m "Code deployed successfully"
```

### 3. Automatic Backup Before Deploy

Add to `git_auto_deploy.py` before pull:

```python
# Backup current version
subprocess.run(["cp", "-r", ".", "../surveillance-car-backup"])
```

### 4. Deploy Only During Off-Hours

Use cron instead of continuous monitoring:

```bash
# Deploy only at 2 AM
0 2 * * * cd /home/pi/surveillance-car && python3 deployment/git_auto_deploy.py
```

---

## 📚 Additional Resources

### Files Created

- `git_auto_deploy.py` - Main deployment script
- `webhook_listener.py` - Webhook server
- `git-deploy.service` - Systemd service for auto-pull
- `webhook-listener.service` - Systemd service for webhooks
- `post_deploy.sh` - Custom post-deployment actions
- `setup_git_deploy.sh` - Automated setup script

### Logs Location

- Deployment logs: `~/surveillance-car/logs/git_deploy.log`
- Webhook logs: `~/surveillance-car/logs/webhook.log`
- Systemd logs: `journalctl -u git-deploy` or `journalctl -u webhook-listener`

### Useful Commands

```bash
# Manual deploy
python3 deployment/git_auto_deploy.py

# Watch mode (continuous checking)
python3 deployment/git_auto_deploy.py --watch --interval 60

# Check service status
sudo systemctl status git-deploy

# View logs
tail -f logs/git_deploy.log

# Restart services
sudo systemctl restart git-deploy
```

---

## ✅ Checklist

- [ ] Git repository initialized on Raspberry Pi
- [ ] SSH keys configured for Git access
- [ ] Deployment method chosen and configured
- [ ] Services enabled and running
- [ ] Webhook configured (if using webhooks)
- [ ] Test deployment successful
- [ ] Logs accessible and monitored
- [ ] Post-deployment script customized
- [ ] Backup strategy in place

---

## 🎉 You're All Set!

Your Raspberry Pi will now automatically deploy code changes when you push to Git!

**Happy coding! 🚗💨**
