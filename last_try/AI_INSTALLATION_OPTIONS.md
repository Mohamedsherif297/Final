# AI Installation Options

## ⚠️ Problem: face_recognition Takes Too Long

Installing `face_recognition` on Raspberry Pi requires compiling `dlib` from source, which takes **30-60 minutes** and the Pi appears stuck during compilation.

## ✅ Solution: Two Options

### Option 1: AI Lite (RECOMMENDED) ⚡
**Fast installation, follows any person**

#### What You Get:
- ✅ Face detection (detects any face)
- ✅ Body tracking
- ✅ Autonomous following
- ❌ No face recognition (doesn't know WHO it's following)

#### Installation (5 minutes):
```bash
cd ~/surveillance-car/last_try

# Install only MediaPipe (fast!)
pip3 install mediapipe --break-system-packages

# Run lite system
sudo ./start_ai_lite.sh
```

#### Use Case:
- You want AI following NOW
- You don't need to recognize specific people
- You want faster, lighter system
- **Perfect for testing and demos!**

---

### Option 2: AI Full (With Recognition) 🎯
**Slow installation, recognizes specific people**

#### What You Get:
- ✅ Face detection
- ✅ Face recognition (knows WHO it's following)
- ✅ Body tracking
- ✅ Follows only known people

#### Installation (30-60 minutes):
```bash
cd ~/surveillance-car/last_try

# Install MediaPipe (fast)
pip3 install mediapipe --break-system-packages

# Install face_recognition (SLOW - 30-60 minutes)
# The Pi will appear stuck - this is NORMAL!
pip3 install face_recognition --break-system-packages

# Run full system
sudo ./start_ai_system.sh
```

#### Use Case:
- You need to recognize specific people
- You have time to wait for installation
- You want full AI capabilities
- **Best for production use**

---

## 📊 Comparison

| Feature | AI Lite | AI Full |
|---------|---------|---------|
| Installation Time | 5 minutes | 30-60 minutes |
| Dependencies | MediaPipe only | MediaPipe + face_recognition |
| Face Detection | ✅ Yes | ✅ Yes |
| Face Recognition | ❌ No | ✅ Yes |
| Body Tracking | ✅ Yes | ✅ Yes |
| Follows | Any person | Known people only |
| CPU Usage | Lower | Higher |
| Dashboard Shows | "Person" | Actual name |

---

## 🚀 Quick Start (AI Lite - Recommended)

### 1. Pull Code
```bash
cd ~/surveillance-car
git pull origin main
```

### 2. Install MediaPipe
```bash
cd last_try
pip3 install mediapipe --break-system-packages
```

### 3. Run System
```bash
sudo ./start_ai_lite.sh
```

### 4. Test
- Open dashboard
- Click "AI Follow"
- Stand in front of camera
- Car follows you!

---

## 🎯 When to Use Each

### Use AI Lite When:
- ✅ You want to test AI quickly
- ✅ You don't care WHO it follows
- ✅ You want faster performance
- ✅ You're doing a demo
- ✅ Installation time matters

### Use AI Full When:
- ✅ You need to recognize specific people
- ✅ You want to follow only known faces
- ✅ You have time for installation
- ✅ You need production features
- ✅ Security/identification matters

---

## 🔄 Can I Switch Later?

**Yes!** Both systems use the same hardware and dashboard.

### Switch to Lite:
```bash
sudo ./start_ai_lite.sh
```

### Switch to Full:
```bash
sudo ./start_ai_system.sh
```

---

## 💡 Recommendation

**Start with AI Lite:**
1. Test the system quickly (5 minutes)
2. Verify everything works
3. If you need recognition, install full version later
4. Let it compile overnight if needed

**The lite version is 100% functional for following people!**

---

## 🐛 Troubleshooting

### AI Lite Not Working
```bash
# Check MediaPipe
python3 -c "import mediapipe; print('OK')"

# If failed, install
pip3 install mediapipe --break-system-packages
```

### face_recognition Installation Stuck
**This is NORMAL!** The Pi is compiling dlib:
- Takes 30-60 minutes
- CPU will be at 100%
- Temperature will rise (60-75°C)
- Screen shows "Building wheel for dlib"
- **DO NOT CANCEL** - let it finish!

To monitor progress:
```bash
# In another terminal
htop  # Watch CPU usage
vcgencmd measure_temp  # Watch temperature
```

### Installation Failed
```bash
# Install system dependencies first
sudo apt-get update
sudo apt-get install -y cmake libopenblas-dev liblapack-dev

# Try again
pip3 install face_recognition --break-system-packages
```

---

## 📁 Files

### AI Lite System:
- `run_all_integrated_lite.py` - Lite version (detection only)
- `ai_controller_lite.py` - Lite AI controller
- `start_ai_lite.sh` - Lite startup script

### AI Full System:
- `run_all_integrated.py` - Full version (with recognition)
- `ai_controller.py` - Full AI controller
- `start_ai_system.sh` - Full startup script

### Shared:
- `system_state.py` - State manager (both use this)
- `hardware/*` - Hardware drivers (both use these)
- `Dashboard/*` - Web dashboard (both use this)

---

## ✅ Summary

**For Quick Testing:** Use AI Lite
- Install: `pip3 install mediapipe --break-system-packages`
- Run: `sudo ./start_ai_lite.sh`
- Time: 5 minutes

**For Production:** Use AI Full
- Install: `pip3 install mediapipe face_recognition --break-system-packages`
- Run: `sudo ./start_ai_system.sh`
- Time: 30-60 minutes (be patient!)

**Both work great - choose based on your needs!** 🚀
