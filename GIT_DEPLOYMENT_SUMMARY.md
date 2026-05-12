# Git Auto-Deployment System - Summary

## 🎯 What Was Created

A complete Git-based deployment system for your Raspberry Pi that automatically pulls and deploys code changes when you push to your repository.

## 📁 Files Created

All files are in `/Raspi/deployment/`:

1. **`git_auto_deploy.py`** - Main deployment script
   - Fetches updates from Git
   - Pulls changes
   - Installs dependencies
   - Runs post-deploy scripts
   - Restarts services

2. **`webhook_listener.py`** - Webhook server
   - Listens for GitHub/GitLab push events
   - Verifies webhook signatures
   - Triggers deployment on push

3. **`git-deploy.service`** - Systemd service for periodic checks
   - Runs in background
   - Checks for updates every 5 minutes
   - Auto-starts on boot

4. **`webhook-listener.service`** - Systemd service for webhooks
   - Runs webhook server
   - Listens on port 8080
   - Auto-starts on boot

5. **`post_deploy.sh`** - Custom post-deployment actions
   - Runs after code is pulled
   - Customize with your own commands

6. **`setup_git_deploy.sh`** - Automated setup script
   - Interactive setup wizard
   - Installs dependencies
   - Configures services

7. **`test_deployment.sh`** - Test script
   - Verifies installation
   - Checks all components

8. **`GIT_AUTO_DEPLOY_GUIDE.md`** - Complete documentation
   - Detailed setup instructions
   - Configuration options
   - Troubleshooting guide

9. **`QUICK_REFERENCE.md`** - Command cheat sheet
   - Common commands
   - Quick troubleshooting

10. **`README.md`** - Overview and quick start

## 🚀 How to Use

### Step 1: Copy to Raspberry Pi

```bash
# From your computer
scp -r "IOT /Final/Raspi" pi@raspberrypi.local:~/surveillance-car
```

### Step 2: Run Setup on Raspberry Pi

```bash
# SSH into Pi
ssh pi@raspberrypi.local

# Navigate to project
cd ~/surveillance-car

# Run setup
chmod +x deployment/setup_git_deploy.sh
./deployment/setup_git_deploy.sh
```

### Step 3: Choose Deployment Method

The setup script will ask you to choose:

**Option 1: Periodic Auto-Pull** (Recommended for beginners)
- Checks for updates every 5 minutes
- No port forwarding needed
- Simple and reliable

**Option 2: Webhook Listener** (Recommended for instant deployment)
- Deploys immediately when you push
- Requires port forwarding or local network
- Fastest deployment

**Option 3: Both** (Recommended)
- Best of both worlds
- Webhook for instant deployment
- Periodic check as backup

**Option 4: Manual Only**
- No automation
- Deploy manually when needed

### Step 4: Push Changes

```bash
# On your development computer
cd "IOT /Final"
git add .
git commit -m "Your changes"
git push origin main
```

**Your Raspberry Pi automatically deploys!** 🎉

## 🎮 Deployment Methods Explained

### Method 1: Periodic Auto-Pull

```
┌─────────────┐
│ Raspberry Pi│
│             │
│  ┌───────┐  │     Every 5 minutes
│  │Service│──┼────► Check Git remote
│  └───────┘  │     Pull if changes
│             │     Deploy automatically
└─────────────┘
```

**Pros:**
- Simple setup
- No port forwarding
- Works on any network

**Cons:**
- 5-minute delay
- Periodic network checks

### Method 2: Webhook Listener

```
┌──────────┐         ┌─────────────┐
│ GitHub/  │  Push   │ Raspberry Pi│
│ GitLab   │────────►│             │
│          │ Webhook │  ┌───────┐  │
│          │         │  │Webhook│  │
└──────────┘         │  │Server │  │
                     │  └───┬───┘  │
                     │      │      │
                     │  ┌───▼───┐  │
                     │  │Deploy │  │
                     │  └───────┘  │
                     └─────────────┘
```

**Pros:**
- Instant deployment
- No polling
- Efficient

**Cons:**
- Requires port forwarding (if not on same network)
- Slightly more complex setup

## 🔧 What Happens During Deployment

```
1. Fetch Updates
   ↓
2. Check for Changes
   ↓
3. Pull Code (if changes exist)
   ↓
4. Install Dependencies (from requirements.txt)
   ↓
5. Run Post-Deploy Script (custom actions)
   ↓
6. Restart Services (if configured)
   ↓
7. Log Everything
```

## 📊 Common Commands

### Manual Deployment
```bash
cd ~/surveillance-car
python3 deployment/git_auto_deploy.py
```

### Check Status
```bash
sudo systemctl status git-deploy
sudo systemctl status webhook-listener
```

### View Logs
```bash
tail -f ~/surveillance-car/logs/git_deploy.log
tail -f ~/surveillance-car/logs/webhook.log
```

### Restart Services
```bash
sudo systemctl restart git-deploy
sudo systemctl restart webhook-listener
```

### Test Installation
```bash
cd ~/surveillance-car
chmod +x deployment/test_deployment.sh
./deployment/test_deployment.sh
```

## 🌐 Webhook Setup (Optional)

If you chose webhook listener, configure your Git provider:

### GitHub

1. Go to repository → Settings → Webhooks → Add webhook
2. **Payload URL**: `http://YOUR_PI_IP:8080/webhook/github`
3. **Content type**: `application/json`
4. **Secret**: Your webhook secret (from setup)
5. **Events**: Just the push event
6. Click "Add webhook"

### GitLab

1. Go to repository → Settings → Webhooks
2. **URL**: `http://YOUR_PI_IP:8080/webhook/gitlab`
3. **Secret token**: Your webhook secret (from setup)
4. **Trigger**: Push events
5. Click "Add webhook"

### Get Your Pi's IP
```bash
hostname -I
```

## 🛡️ Security Notes

1. **Use strong webhook secrets**
   ```bash
   openssl rand -hex 32
   ```

2. **Use SSH keys for Git**
   ```bash
   ssh-keygen -t ed25519 -C "pi@raspberrypi"
   cat ~/.ssh/id_ed25519.pub  # Add to GitHub/GitLab
   ```

3. **Don't commit secrets**
   - Add `.env` files to `.gitignore`
   - Keep sensitive configs local

4. **Consider VPN for webhooks**
   - Tailscale
   - WireGuard
   - Cloudflare Tunnel

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
# Check service
sudo systemctl status webhook-listener

# Test locally
curl -X POST http://localhost:8080/webhook/manual

# Check firewall
sudo ufw allow 8080
```

### Permission Issues
```bash
sudo chown -R pi:pi ~/surveillance-car
chmod +x ~/surveillance-car/deployment/*.py
chmod +x ~/surveillance-car/deployment/*.sh
```

## 📚 Documentation

- **Complete Guide**: `Raspi/deployment/GIT_AUTO_DEPLOY_GUIDE.md`
- **Quick Reference**: `Raspi/deployment/QUICK_REFERENCE.md`
- **Deployment README**: `Raspi/deployment/README.md`

## ✅ Benefits

✅ **No manual SSH** - Push and forget  
✅ **Automatic deployment** - Works 24/7  
✅ **Fast iteration** - Changes deploy in seconds/minutes  
✅ **Consistent** - Same process every time  
✅ **Logged** - Full deployment history  
✅ **Flexible** - Multiple deployment methods  
✅ **Safe** - Stashes local changes before pulling  
✅ **Smart** - Only deploys when changes exist  

## 🎯 Example Workflow

### On Your Computer
```bash
cd "IOT /Final"

# Make changes
nano Raspi/Drivers/hardware/motor/motor_controller.py

# Commit and push
git add .
git commit -m "Improve motor control"
git push origin main
```

### On Raspberry Pi (Automatic)
```
[2024-05-12 10:30:15] Fetching updates from remote...
[2024-05-12 10:30:16] Updates available: abc1234 -> def5678
[2024-05-12 10:30:16] Pulling changes from origin/main...
[2024-05-12 10:30:17] Successfully pulled changes
[2024-05-12 10:30:17] Installing/updating dependencies...
[2024-05-12 10:30:20] Dependencies updated successfully
[2024-05-12 10:30:20] Running post-deployment script...
[2024-05-12 10:30:21] Post-deployment script completed
[2024-05-12 10:30:21] Deployment completed successfully!
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

## 🎉 You're All Set!

Your Raspberry Pi now automatically deploys code changes when you push to Git!

### Next Steps

1. ✅ Test the deployment system
2. ✅ Push a small change to verify it works
3. ✅ Monitor logs to see deployment in action
4. ✅ Customize `post_deploy.sh` for your needs
5. ✅ Set up webhooks for instant deployment (optional)

### Need Help?

- Read the complete guide: `Raspi/deployment/GIT_AUTO_DEPLOY_GUIDE.md`
- Check quick reference: `Raspi/deployment/QUICK_REFERENCE.md`
- Run test script: `./deployment/test_deployment.sh`

---

**Happy deploying! 🚗💨**
