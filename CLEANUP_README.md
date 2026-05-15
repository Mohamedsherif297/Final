# 🧹 Raspberry Pi Space Cleanup Guide

## Problem
Your repository is too large for the Raspberry Pi. It contains files that are only needed on your laptop (documentation, ESP32 files, laptop controller, etc.).

## Solution
Clean up the repository on the Pi to keep only essential files.

---

## 📊 What Gets Removed

### ❌ Will be REMOVED from Pi:
- **Documentation** (ALL_FIXES_SUMMARY.md, etc.) - ~5 MB
- **Docs/** folder - ~2 MB
- **Laptop/** controller - ~10 MB
- **Dashboard/** web interface - ~5 MB
- **ESP32/** files - ~5 MB
- **Raspi/** folder (using last_try instead) - ~70 MB
- **Backup files** (*.zip, *.tar.gz) - ~100 MB
- **Test files** - ~5 MB
- **System files** (.DS_Store, __pycache__) - ~2 MB

**Total saved: ~200 MB**

### ✅ Will be KEPT on Pi:
- **last_try/** - Main application (hardware drivers, AI, MQTT, WebSocket)
- **.git/** - For git pull updates
- **.gitignore** - Git rules

**Final size: ~30-50 MB** (without AI models)

---

## 🚀 How to Clean Up

### Option 1: Automated Cleanup (Recommended)

**On Raspberry Pi:**
```bash
cd ~/surveillance-car
./cleanup_for_pi.sh
```

This will:
1. Show you what will be removed
2. Ask for confirmation
3. Remove unnecessary files
4. Show space saved

### Option 2: Manual Cleanup

**On Raspberry Pi:**
```bash
cd ~/surveillance-car

# Remove documentation
rm -rf Docs/ ESP32/ Laptop/ last_try/
rm -f *.md *.html *.zip

# Remove system files
find . -name ".DS_Store" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Remove tests
rm -rf Raspi/tests/

# Clean logs
rm -f Raspi/logs/*.log
```

---

## 📁 Final Structure on Pi

After cleanup, your Pi will have:

```
surveillance-car/
├── .git/                    # Git repository (for updates)
├── .gitignore              # Git ignore rules
└── last_try/               # Main application
    ├── run_all_integrated.py      # Main entry point
    ├── run_all_integrated_lite.py # Lite version (no AI)
    ├── system_state.py            # Shared state
    ├── ai_controller.py           # AI controller
    ├── mqtt_control.py            # MQTT handler
    ├── websocket_stream.py        # WebSocket camera stream
    ├── requirements.txt           # Dependencies
    ├── hardware/                  # Hardware drivers
    │   ├── motor.py
    │   ├── servo.py
    │   ├── led.py
    │   ├── camera.py
    │   └── ultrasonic.py
    └── pi_minimal/                # AI system
        ├── main.py
        ├── requirements.txt
        └── known_faces/           # Face images
```

**Total size: ~30-50 MB** (plus AI models if needed)

---

## 🔄 Updating Code After Cleanup

The cleanup keeps `.git/` so you can still update:

```bash
cd ~/surveillance-car
git pull origin main
```

Git will only download the files you need (Raspi/ and Dashboard/).

---

## 📦 Installing Dependencies

After cleanup, install only what you need:

### Minimal Installation (No AI)
```bash
cd ~/surveillance-car/last_try
pip3 install -r requirements.txt --break-system-packages
# Or run without AI:
sudo python3 run_all_integrated_lite.py
```

### Full Installation (With AI)
```bash
cd ~/surveillance-car/last_try
pip3 install -r requirements.txt --break-system-packages
cd pi_minimal
pip3 install -r requirements.txt --break-system-packages
# Run with AI:
cd ..
sudo python3 run_all_integrated.py
```

---

## 🎯 What About AI Models?

AI models are large (~5-50 MB each). Options:

### Option 1: Download on Pi
```bash
cd ~/surveillance-car/last_try/pi_minimal
# Create models directory if needed
mkdir -p models
# Download models as needed
wget [model-url] -O models/mobilefacenet.tflite
```

### Option 2: Skip AI (Camera only)
If you don't need AI face tracking, use the lite version:
```bash
cd ~/surveillance-car/last_try
sudo python3 run_all_integrated_lite.py
```

---

## 💾 Space Comparison

### Before Cleanup:
```
Total: ~250 MB
├── Raspi/: 70 MB
├── last_try/: 50 MB
├── Laptop/: 10 MB
├── Dashboard/: 5 MB
├── ESP32/: 5 MB
├── Docs/: 2 MB
├── Backups (*.zip): 100 MB
└── Other: 8 MB
```

### After Cleanup:
```
Total: ~50 MB
├── last_try/: 30 MB
├── .git/: 15 MB
└── Other: 5 MB
```

**Space saved: ~200 MB (80% reduction)**

---

## ⚠️ Important Notes

1. **Run cleanup ONLY on Raspberry Pi**, not on your laptop!
2. **Keep full repo on laptop** for development
3. **Git will still work** after cleanup
4. **You can re-clone** if you need files back

---

## 🔧 Troubleshooting

### "I accidentally ran cleanup on my laptop!"
```bash
# Restore from Git
git reset --hard HEAD
git clean -fd
```

### "I need a file that was removed"
```bash
# Get it from Git
git checkout origin/main -- path/to/file
```

### "Git pull fails after cleanup"
```bash
# This is normal if files were removed
# Just force pull:
git fetch origin
git reset --hard origin/main
```

---

## ✅ Checklist

Before cleanup:
- [ ] You're on the Raspberry Pi (not laptop!)
- [ ] You have Git access for updates
- [ ] You've backed up any custom changes

After cleanup:
- [ ] Check space: `du -sh ~/surveillance-car`
- [ ] Test Git: `git pull origin main`
- [ ] Test app: `cd last_try && sudo python3 run_all_integrated.py`

---

## 🎉 Result

After cleanup:
- ✅ 200 MB space saved (80% reduction)
- ✅ Only essential files remain (last_try/ + .git/)
- ✅ Git updates still work
- ✅ System runs normally
- ✅ Faster deployments
- ✅ Dashboard runs from laptop browser

---

**Ready to clean up? Run `./cleanup_for_pi.sh` on your Raspberry Pi!**
