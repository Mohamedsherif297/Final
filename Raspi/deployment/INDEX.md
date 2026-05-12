# Git Auto-Deploy Documentation Index

## 📚 Documentation Overview

This directory contains a complete Git-based auto-deployment system for your Raspberry Pi.

## 🎯 Start Here

### New Users
1. **[QUICK_START_CARD.md](QUICK_START_CARD.md)** - One-page quick start (print this!)
2. **[README.md](README.md)** - Overview and introduction
3. **[GIT_AUTO_DEPLOY_GUIDE.md](GIT_AUTO_DEPLOY_GUIDE.md)** - Complete setup guide

### Experienced Users
1. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Command reference
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
3. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Problem solving

## 📁 File Guide

### Documentation Files

| File | Purpose | When to Read |
|------|---------|--------------|
| **README.md** | Overview and quick start | First time setup |
| **GIT_AUTO_DEPLOY_GUIDE.md** | Complete documentation | Detailed setup and configuration |
| **QUICK_REFERENCE.md** | Command cheat sheet | Daily use, quick lookup |
| **QUICK_START_CARD.md** | One-page reference | Print and keep handy |
| **ARCHITECTURE.md** | System design and flow | Understanding how it works |
| **TROUBLESHOOTING.md** | Problem solving guide | When things go wrong |
| **INDEX.md** | This file | Finding documentation |

### Executable Files

| File | Purpose | Usage |
|------|---------|-------|
| **git_auto_deploy.py** | Main deployment script | `python3 git_auto_deploy.py` |
| **webhook_listener.py** | Webhook server | `python3 webhook_listener.py` |
| **setup_git_deploy.sh** | Automated setup | `./setup_git_deploy.sh` |
| **test_deployment.sh** | Test installation | `./test_deployment.sh` |
| **post_deploy.sh** | Custom post-deploy actions | Runs automatically |

### Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| **git-deploy.service** | Systemd service (periodic) | `/etc/systemd/system/` |
| **webhook-listener.service** | Systemd service (webhook) | `/etc/systemd/system/` |
| **requirements.txt** | Python dependencies | Current directory |

## 🚀 Quick Navigation

### I want to...

**Set up for the first time**
→ [README.md](README.md) → Run `setup_git_deploy.sh`

**Deploy manually**
→ `python3 deployment/git_auto_deploy.py`

**Check if it's working**
→ `./deployment/test_deployment.sh`

**See deployment logs**
→ `tail -f logs/git_deploy.log`

**Fix a problem**
→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Understand how it works**
→ [ARCHITECTURE.md](ARCHITECTURE.md)

**Find a command**
→ [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

**Configure webhooks**
→ [GIT_AUTO_DEPLOY_GUIDE.md](GIT_AUTO_DEPLOY_GUIDE.md#method-2-webhook-listener-recommended-for-instant-deployment)

**Change settings**
→ [GIT_AUTO_DEPLOY_GUIDE.md](GIT_AUTO_DEPLOY_GUIDE.md#-configuration)

**Rollback deployment**
→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md#10-emergency-rollback-to-previous-version)

## 📖 Reading Order

### For Beginners

1. **[QUICK_START_CARD.md](QUICK_START_CARD.md)** (5 min)
   - Get a quick overview
   
2. **[README.md](README.md)** (10 min)
   - Understand what the system does
   
3. **Run setup script** (5 min)
   - `./setup_git_deploy.sh`
   
4. **[GIT_AUTO_DEPLOY_GUIDE.md](GIT_AUTO_DEPLOY_GUIDE.md)** (30 min)
   - Learn detailed configuration
   
5. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** (bookmark)
   - Keep for daily use

### For Advanced Users

1. **[ARCHITECTURE.md](ARCHITECTURE.md)** (20 min)
   - Understand system design
   
2. **[GIT_AUTO_DEPLOY_GUIDE.md](GIT_AUTO_DEPLOY_GUIDE.md)** (skim)
   - Review advanced features
   
3. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** (bookmark)
   - Quick command lookup

### For Troubleshooting

1. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**
   - Find your specific issue
   
2. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)**
   - Get diagnostic commands
   
3. **[GIT_AUTO_DEPLOY_GUIDE.md](GIT_AUTO_DEPLOY_GUIDE.md)**
   - Review configuration

## 🎯 Common Tasks

### Setup Tasks

| Task | Documentation | Command |
|------|---------------|---------|
| Initial setup | [README.md](README.md) | `./setup_git_deploy.sh` |
| Test installation | [README.md](README.md) | `./test_deployment.sh` |
| Configure webhook | [GIT_AUTO_DEPLOY_GUIDE.md](GIT_AUTO_DEPLOY_GUIDE.md#configure-github-webhook) | See guide |
| Change branch | [GIT_AUTO_DEPLOY_GUIDE.md](GIT_AUTO_DEPLOY_GUIDE.md#change-git-branch) | `--branch name` |

### Daily Tasks

| Task | Documentation | Command |
|------|---------------|---------|
| Manual deploy | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | `python3 deployment/git_auto_deploy.py` |
| Check status | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | `sudo systemctl status git-deploy` |
| View logs | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | `tail -f logs/git_deploy.log` |
| Restart service | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | `sudo systemctl restart git-deploy` |

### Troubleshooting Tasks

| Task | Documentation | Command |
|------|---------------|---------|
| Service won't start | [TROUBLESHOOTING.md](TROUBLESHOOTING.md#1-service-wont-start) | See guide |
| Git pull fails | [TROUBLESHOOTING.md](TROUBLESHOOTING.md#2-git-pull-fails) | See guide |
| Webhook not working | [TROUBLESHOOTING.md](TROUBLESHOOTING.md#3-webhook-not-receiving-events) | See guide |
| Rollback code | [TROUBLESHOOTING.md](TROUBLESHOOTING.md#10-emergency-rollback-to-previous-version) | `git reset --hard HEAD~1` |

## 📊 Documentation Stats

| Document | Pages | Reading Time | Difficulty |
|----------|-------|--------------|------------|
| QUICK_START_CARD.md | 1 | 5 min | Beginner |
| README.md | 3 | 10 min | Beginner |
| QUICK_REFERENCE.md | 2 | 5 min | Beginner |
| GIT_AUTO_DEPLOY_GUIDE.md | 15 | 30 min | Intermediate |
| ARCHITECTURE.md | 8 | 20 min | Advanced |
| TROUBLESHOOTING.md | 10 | 15 min | Intermediate |

**Total:** ~40 pages, ~85 minutes of reading

## 🔍 Search Guide

### By Topic

**Setup & Installation**
- [README.md](README.md)
- [GIT_AUTO_DEPLOY_GUIDE.md](GIT_AUTO_DEPLOY_GUIDE.md) - Setup sections
- [QUICK_START_CARD.md](QUICK_START_CARD.md)

**Configuration**
- [GIT_AUTO_DEPLOY_GUIDE.md](GIT_AUTO_DEPLOY_GUIDE.md) - Configuration section
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Configuration files

**Usage & Commands**
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- [QUICK_START_CARD.md](QUICK_START_CARD.md)

**Troubleshooting**
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Troubleshooting section

**Architecture & Design**
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [GIT_AUTO_DEPLOY_GUIDE.md](GIT_AUTO_DEPLOY_GUIDE.md) - How It Works section

**Security**
- [GIT_AUTO_DEPLOY_GUIDE.md](GIT_AUTO_DEPLOY_GUIDE.md) - Security section
- [ARCHITECTURE.md](ARCHITECTURE.md) - Security Architecture

### By Skill Level

**Beginner**
- [QUICK_START_CARD.md](QUICK_START_CARD.md)
- [README.md](README.md)
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

**Intermediate**
- [GIT_AUTO_DEPLOY_GUIDE.md](GIT_AUTO_DEPLOY_GUIDE.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Advanced**
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [GIT_AUTO_DEPLOY_GUIDE.md](GIT_AUTO_DEPLOY_GUIDE.md) - Advanced sections

## 🎓 Learning Path

### Path 1: Quick Start (30 minutes)
1. Read [QUICK_START_CARD.md](QUICK_START_CARD.md)
2. Run `./setup_git_deploy.sh`
3. Test with `./test_deployment.sh`
4. Push a change and verify

### Path 2: Complete Setup (1 hour)
1. Read [README.md](README.md)
2. Read [GIT_AUTO_DEPLOY_GUIDE.md](GIT_AUTO_DEPLOY_GUIDE.md)
3. Run `./setup_git_deploy.sh`
4. Configure webhooks
5. Test thoroughly

### Path 3: Deep Understanding (2 hours)
1. Read [ARCHITECTURE.md](ARCHITECTURE.md)
2. Read [GIT_AUTO_DEPLOY_GUIDE.md](GIT_AUTO_DEPLOY_GUIDE.md)
3. Review all scripts
4. Customize for your needs
5. Set up monitoring

## 📞 Support Resources

### Self-Help
1. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues
2. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Command reference
3. **Test script** - `./test_deployment.sh`

### Documentation
1. **[GIT_AUTO_DEPLOY_GUIDE.md](GIT_AUTO_DEPLOY_GUIDE.md)** - Complete guide
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design
3. **[README.md](README.md)** - Overview

### Diagnostic Tools
```bash
# Test installation
./deployment/test_deployment.sh

# Check service status
sudo systemctl status git-deploy

# View logs
tail -f logs/git_deploy.log

# Manual deployment
python3 deployment/git_auto_deploy.py
```

## 🎉 Quick Wins

### 5-Minute Setup
```bash
./deployment/setup_git_deploy.sh
# Choose Option 1 (Periodic)
# Done!
```

### First Deployment
```bash
# On your computer
git push origin main

# On Raspberry Pi (wait 5 minutes or use webhook)
tail -f ~/surveillance-car/logs/git_deploy.log
```

### Verify It Works
```bash
./deployment/test_deployment.sh
```

## 📝 Notes

- All documentation is in Markdown format
- Scripts are executable (chmod +x applied)
- Logs are in `~/surveillance-car/logs/`
- Services are in `/etc/systemd/system/`

## 🔄 Updates

This documentation is version-controlled with your code. When you update the deployment system, the documentation updates automatically!

---

**Need help? Start with [QUICK_START_CARD.md](QUICK_START_CARD.md) or [README.md](README.md)**

**Having issues? Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

**Want to understand it? Read [ARCHITECTURE.md](ARCHITECTURE.md)**

---

**Happy deploying! 🚗💨**
