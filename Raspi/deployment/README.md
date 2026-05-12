# Git Auto-Deploy System

Automatically deploy code changes to your Raspberry Pi by pushing to Git!

## 🎯 What This Does

This system allows you to:
- **Push code** to GitHub/GitLab from your computer
- **Automatically deploy** to your Raspberry Pi
- **No manual SSH** or file copying needed
- **Instant updates** with webhooks or periodic checks

## 🚀 Quick Start

### 1. Run Setup Script

```bash
cd ~/surveillance-car
chmod +x deployment/setup_git_deploy.sh
./deployment/setup_git_deploy.sh
```

### 2. Choose Deployment Method

The setup script will ask you to choose:

- **Option 1**: Periodic auto-pull (checks every 5 minutes)
- **Option 2**: Webhook listener (instant deployment on push)
- **Option 3**: Both (recommended)
- **Option 4**: Manual only

### 3. Push Changes

```bash
# On your development computer
git add .
git commit -m "Update code"
git push origin main
```

Your Raspberry Pi automatically deploys! 🎉

## 📁 Files

| File | Description |
|------|-------------|
| `git_auto_deploy.py` | Main deployment script |
| `webhook_listener.py` | Webhook server for GitHub/GitLab |
| `git-deploy.service` | Systemd service for periodic checks |
| `webhook-listener.service` | Systemd service for webhook listener |
| `post_deploy.sh` | Custom post-deployment actions |
| `setup_git_deploy.sh` | Automated setup script |
| `GIT_AUTO_DEPLOY_GUIDE.md` | Complete documentation |
| `QUICK_REFERENCE.md` | Command reference |

## 📖 Documentation

- **[Complete Guide](GIT_AUTO_DEPLOY_GUIDE.md)** - Full setup and usage documentation
- **[Quick Reference](QUICK_REFERENCE.md)** - Common commands and troubleshooting

## 🎮 Usage

### Manual Deployment

```bash
python3 deployment/git_auto_deploy.py
```

### Check Status

```bash
sudo systemctl status git-deploy
sudo systemctl status webhook-listener
```

### View Logs

```bash
tail -f logs/git_deploy.log
tail -f logs/webhook.log
```

## 🔧 How It Works

### Periodic Auto-Pull

1. Service runs in background
2. Checks Git remote every 5 minutes
3. Pulls changes if available
4. Installs dependencies
5. Restarts services

### Webhook Listener

1. Listens on port 8080
2. Receives push events from GitHub/GitLab
3. Verifies webhook signature
4. Triggers deployment immediately
5. Returns status to Git provider

## 🌐 Deployment Methods Comparison

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Periodic** | Simple, no port forwarding | 5-minute delay | Beginners, local networks |
| **Webhook** | Instant deployment | Requires port forwarding | Production, fast iteration |
| **Cron** | No systemd needed | Less flexible | Minimal setups |
| **Manual** | Full control | Requires SSH | Testing, debugging |

## 🛡️ Security

- Use strong webhook secrets
- Configure firewall rules
- Use SSH keys for Git
- Don't commit secrets
- Consider VPN for webhooks

See [Security Best Practices](GIT_AUTO_DEPLOY_GUIDE.md#-security-best-practices) for details.

## 🐛 Troubleshooting

### Service Not Running

```bash
sudo systemctl status git-deploy
journalctl -u git-deploy -n 50
sudo systemctl restart git-deploy
```

### Git Pull Fails

```bash
cd ~/surveillance-car
git status
git fetch origin
git reset --hard origin/main
```

### Webhook Not Working

```bash
sudo systemctl status webhook-listener
curl -X POST http://localhost:8080/webhook/manual
sudo ufw allow 8080
```

See [Troubleshooting Guide](GIT_AUTO_DEPLOY_GUIDE.md#-troubleshooting) for more.

## 📊 Monitoring

```bash
# View deployment logs
tail -f logs/git_deploy.log

# View webhook logs
tail -f logs/webhook.log

# View systemd logs
journalctl -u git-deploy -f
journalctl -u webhook-listener -f

# Check last deployment
git log -1
```

## 🎯 Example Workflow

```bash
# On your computer
cd surveillance-car
nano Drivers/hardware/motor/motor_controller.py
git add .
git commit -m "Improve motor control"
git push origin main

# Raspberry Pi automatically:
# 1. Receives webhook or detects change
# 2. Pulls latest code
# 3. Installs dependencies
# 4. Runs post-deploy script
# 5. Restarts services
# 6. Logs everything

# Check deployment on Pi
ssh pi@raspberrypi.local
tail -f ~/surveillance-car/logs/git_deploy.log
```

## ⚙️ Configuration

### Change Check Interval

Edit `/etc/systemd/system/git-deploy.service`:

```ini
ExecStart=/usr/bin/python3 /home/pi/surveillance-car/deployment/git_auto_deploy.py --watch --interval 300
```

Change `300` to your desired seconds.

### Change Branch

```bash
python3 deployment/git_auto_deploy.py --branch your-branch
```

### Custom Post-Deploy Actions

Edit `deployment/post_deploy.sh`:

```bash
#!/bin/bash
# Add your commands here
sudo systemctl restart mosquitto
python3 -m pytest tests/
```

## 🚀 Advanced Features

- Deploy specific branches
- Blue-green deployment
- Automatic rollback
- Notification on deployment
- Deploy to multiple Pis
- Scheduled deployments

See [Advanced Usage](GIT_AUTO_DEPLOY_GUIDE.md#-advanced-usage) for details.

## 📞 Support

### Quick Commands

```bash
# Manual deploy
python3 deployment/git_auto_deploy.py

# Check status
sudo systemctl status git-deploy

# View logs
tail -f logs/git_deploy.log

# Restart service
sudo systemctl restart git-deploy
```

### Documentation

- [Complete Guide](GIT_AUTO_DEPLOY_GUIDE.md) - Full documentation
- [Quick Reference](QUICK_REFERENCE.md) - Command cheat sheet

### Common Issues

1. **Service won't start** → Check logs with `journalctl -u git-deploy -n 50`
2. **Git pull fails** → Reset with `git reset --hard origin/main`
3. **Webhook not working** → Check firewall with `sudo ufw status`
4. **Permission denied** → Fix with `sudo chown -R pi:pi ~/surveillance-car`

## ✅ Checklist

- [ ] Setup script completed
- [ ] Deployment method chosen
- [ ] Services running
- [ ] Test deployment successful
- [ ] Webhook configured (if using)
- [ ] Logs accessible
- [ ] Post-deploy script customized

## 🎉 Benefits

✅ **No manual deployment** - Push and forget  
✅ **Fast iteration** - Changes deploy in seconds  
✅ **Consistent** - Same process every time  
✅ **Logged** - Full deployment history  
✅ **Automatic** - Works 24/7  
✅ **Flexible** - Multiple deployment methods  

---

**Ready to deploy? Run the setup script and start pushing!** 🚗💨

```bash
./deployment/setup_git_deploy.sh
```
