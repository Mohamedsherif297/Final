# Git Auto-Deploy Quick Reference

## 🚀 Quick Setup

```bash
cd ~/surveillance-car
chmod +x deployment/setup_git_deploy.sh
./deployment/setup_git_deploy.sh
```

## 📋 Common Commands

### Manual Deployment
```bash
cd ~/surveillance-car
python3 deployment/git_auto_deploy.py
```

### Service Management
```bash
# Status
sudo systemctl status git-deploy
sudo systemctl status webhook-listener

# Start
sudo systemctl start git-deploy
sudo systemctl start webhook-listener

# Stop
sudo systemctl stop git-deploy
sudo systemctl stop webhook-listener

# Restart
sudo systemctl restart git-deploy
sudo systemctl restart webhook-listener

# Enable on boot
sudo systemctl enable git-deploy
sudo systemctl enable webhook-listener

# Disable on boot
sudo systemctl disable git-deploy
sudo systemctl disable webhook-listener
```

### View Logs
```bash
# Deployment logs
tail -f ~/surveillance-car/logs/git_deploy.log

# Webhook logs
tail -f ~/surveillance-car/logs/webhook.log

# Systemd logs
journalctl -u git-deploy -f
journalctl -u webhook-listener -f

# Last 50 lines
journalctl -u git-deploy -n 50
```

### Git Operations
```bash
cd ~/surveillance-car

# Check status
git status

# View recent commits
git log --oneline -10

# Pull manually
git pull origin main

# Reset to remote (WARNING: loses local changes)
git fetch origin
git reset --hard origin/main

# Stash local changes
git stash
git pull origin main
```

## 🔧 Configuration Files

### Service Files
- `/etc/systemd/system/git-deploy.service`
- `/etc/systemd/system/webhook-listener.service`

### Scripts
- `~/surveillance-car/deployment/git_auto_deploy.py`
- `~/surveillance-car/deployment/webhook_listener.py`
- `~/surveillance-car/deployment/post_deploy.sh`

### Logs
- `~/surveillance-car/logs/git_deploy.log`
- `~/surveillance-car/logs/webhook.log`

## 🌐 Webhook URLs

### GitHub
```
http://YOUR_PI_IP:8080/webhook/github
```

### GitLab
```
http://YOUR_PI_IP:8080/webhook/gitlab
```

### Manual Trigger (localhost only)
```bash
curl -X POST http://localhost:8080/webhook/manual
```

### Health Check
```bash
curl http://localhost:8080/health
```

## 🐛 Troubleshooting

### Service Won't Start
```bash
# Check logs
journalctl -u git-deploy -n 50
journalctl -u webhook-listener -n 50

# Reload systemd
sudo systemctl daemon-reload

# Restart service
sudo systemctl restart git-deploy
```

### Git Pull Fails
```bash
cd ~/surveillance-car

# Check remote
git remote -v

# Fetch updates
git fetch origin

# Reset to remote
git reset --hard origin/main
```

### Permission Issues
```bash
# Fix ownership
sudo chown -R pi:pi ~/surveillance-car

# Fix permissions
chmod +x ~/surveillance-car/deployment/*.py
chmod +x ~/surveillance-car/deployment/*.sh
```

### Port Already in Use
```bash
# Check what's using port 8080
sudo netstat -tulpn | grep 8080

# Kill process
sudo kill -9 PID
```

## 📊 Monitoring

### Check Last Deployment
```bash
# View last commit
cd ~/surveillance-car
git log -1

# View last deployment log
tail -20 logs/git_deploy.log
```

### Real-time Monitoring
```bash
# Watch logs
watch -n 5 'tail -20 ~/surveillance-car/logs/git_deploy.log'

# Or use journalctl
journalctl -u git-deploy -f
```

## 🔐 Security

### Generate Webhook Secret
```bash
openssl rand -hex 32
```

### Update Webhook Secret
```bash
# Edit service file
sudo nano /etc/systemd/system/webhook-listener.service

# Change this line:
Environment="WEBHOOK_SECRET=your-new-secret"

# Restart service
sudo systemctl daemon-reload
sudo systemctl restart webhook-listener
```

### Setup SSH Keys
```bash
# Generate key
ssh-keygen -t ed25519 -C "pi@raspberrypi"

# Display public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub/GitLab
```

## 🎯 Workflow

### Development
```bash
# On your computer
git add .
git commit -m "Your changes"
git push origin main

# Raspberry Pi deploys automatically!
```

### Verify Deployment
```bash
# SSH into Pi
ssh pi@raspberrypi.local

# Check logs
tail -f ~/surveillance-car/logs/git_deploy.log

# Verify changes
cd ~/surveillance-car
git log -1
```

## 📞 Get Help

### Check Service Status
```bash
sudo systemctl status git-deploy --no-pager
sudo systemctl status webhook-listener --no-pager
```

### View Full Logs
```bash
journalctl -u git-deploy --no-pager | less
journalctl -u webhook-listener --no-pager | less
```

### Test Deployment
```bash
cd ~/surveillance-car
python3 deployment/git_auto_deploy.py
```

---

**For detailed documentation, see `GIT_AUTO_DEPLOY_GUIDE.md`**
