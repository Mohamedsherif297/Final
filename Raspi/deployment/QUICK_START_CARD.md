# 🚀 Git Auto-Deploy Quick Start Card

## ⚡ 3-Step Setup

```bash
# 1. Copy to Raspberry Pi
scp -r Raspi pi@raspberrypi.local:~/surveillance-car

# 2. SSH and run setup
ssh pi@raspberrypi.local
cd ~/surveillance-car
./deployment/setup_git_deploy.sh

# 3. Push changes
git push origin main
# ✅ Automatic deployment!
```

---

## 📋 Essential Commands

| Task | Command |
|------|---------|
| **Manual deploy** | `python3 deployment/git_auto_deploy.py` |
| **Check status** | `sudo systemctl status git-deploy` |
| **View logs** | `tail -f logs/git_deploy.log` |
| **Restart service** | `sudo systemctl restart git-deploy` |
| **Test setup** | `./deployment/test_deployment.sh` |

---

## 🔧 Deployment Methods

### Option 1: Periodic (Simple)
✅ Checks every 5 minutes  
✅ No port forwarding  
⏱️ 0-5 minute delay  

### Option 2: Webhook (Fast)
✅ Instant deployment  
✅ Efficient  
⚙️ Requires port forwarding  

### Option 3: Both (Best)
✅ Instant + backup  
✅ Most reliable  

---

## 🌐 Webhook Setup

### GitHub
1. Settings → Webhooks → Add webhook
2. URL: `http://YOUR_PI_IP:8080/webhook/github`
3. Secret: (from setup)
4. Events: Push

### GitLab
1. Settings → Webhooks
2. URL: `http://YOUR_PI_IP:8080/webhook/gitlab`
3. Secret: (from setup)
4. Trigger: Push events

**Get Pi IP:** `hostname -I`

---

## 🐛 Quick Fixes

### Service won't start
```bash
sudo systemctl restart git-deploy
journalctl -u git-deploy -n 50
```

### Git pull fails
```bash
cd ~/surveillance-car
git reset --hard origin/main
```

### Webhook not working
```bash
sudo systemctl restart webhook-listener
sudo ufw allow 8080
```

### Permission issues
```bash
sudo chown -R pi:pi ~/surveillance-car
chmod +x deployment/*.py deployment/*.sh
```

---

## 📊 What Happens on Deploy

```
Push → Fetch → Check → Pull → Install Deps → Post-Deploy → Restart → Done!
```

**Time:** 5-30 seconds

---

## 📚 Full Documentation

- **Complete Guide:** `GIT_AUTO_DEPLOY_GUIDE.md`
- **Commands:** `QUICK_REFERENCE.md`
- **Troubleshooting:** `TROUBLESHOOTING.md`
- **Architecture:** `ARCHITECTURE.md`

---

## ✅ Checklist

- [ ] Setup script completed
- [ ] Service running: `sudo systemctl status git-deploy`
- [ ] Test deployment: `./deployment/test_deployment.sh`
- [ ] Push test change
- [ ] Verify in logs: `tail -f logs/git_deploy.log`
- [ ] Webhook configured (optional)

---

## 🎯 Example Workflow

```bash
# On your computer
git add .
git commit -m "Update motor control"
git push origin main

# Raspberry Pi deploys automatically!
# Check with:
ssh pi@raspberrypi.local
tail -f ~/surveillance-car/logs/git_deploy.log
```

---

## 🆘 Need Help?

**Test:** `./deployment/test_deployment.sh`  
**Logs:** `tail -f logs/git_deploy.log`  
**Status:** `sudo systemctl status git-deploy`  
**Docs:** `GIT_AUTO_DEPLOY_GUIDE.md`

---

**🎉 Push code → Automatic deployment → Done!**

Print this card and keep it handy! 📄
