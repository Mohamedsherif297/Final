# Surveillance Car — Active Task Tracker

**Last Updated:** May 2026  
**Current Phase:** Phase 1 Testing + Phase 2 Planning

---

## 🔴 Immediate (Do This Next)

### 1. Test Phase 1 End-to-End ⭐⭐⭐

All backend + frontend is built. Now validate it works on real hardware.

```bash
# Step 1: Start Raspberry Pi
cd /home/pi/Final/Raspi
python3 main.py

# Step 2: Open Web Dashboard
# → Open Final/Dashboard/index.html in browser
# → Enter Pi IP → Click Connect

# Step 3: Verify each component
# ✓ Video stream appears
# ✓ Arrow keys move motors
# ✓ Servo sliders move camera
# ✓ LED buttons respond
# ✓ Emergency stop works
# ✓ Sensor gauge updates

# Step 4: Test Desktop GUI
cd Final/Laptop
python3 mqtt_gui_controller.py

# Step 5: Verify MQTT + WebSocket don't interfere
# Send motor command from GUI → Car moves → Dashboard updates
```

**Testing checklist:**
- [ ] `python3 main.py` starts without errors on Pi
- [ ] WebSocket server starts on port 8765
- [ ] Dashboard connects and shows video
- [ ] Motor D-pad works (arrows + WASD)
- [ ] Servo sliders update crosshair position
- [ ] LED presets change LED color
- [ ] Emergency stop halts motors
- [ ] Sensor gauge shows live distance
- [ ] Desktop GUI connects via MQTT
- [ ] Both GUI + Dashboard work simultaneously
- [ ] Graceful shutdown with Ctrl+C

### 2. Fix Laptop GUI Config Path ⭐⭐

**File:** `Laptop/mqtt_gui_controller.py` line 31  
**Problem:** Path `../surveillance-car/mqtt-config/client_config.json` doesn't exist.  
**Fix:** Change to `../Raspi/Network/MQTT/config/client_config.json`

---

## 🟠 Phase 2 — AI Vision Integration

### Overview

The Mizo AI module (`zLast_development/Mizo/IOT-Surveillance-Car-merged-ai-computer-vision/`) is standalone and needs merging into `Final/Raspi/AI/`.

### Hardware Decision Required First

| | Final Project | Mizo Module |
|---|---|---|
| Servo Driver | GPIO PWM (pin 17/18) | PCA9685 I2C (Adafruit ServoKit) |
| **Decision** | Pick one before integrating | |

### Integration Tasks

- [ ] Decide: GPIO PWM vs PCA9685 I2C for servos
- [ ] Copy relevant detection modules to `Raspi/AI/`
  - `blazeface_detector.py` (primary — fastest on Pi4)
  - `pid_controller.py` (for smooth servo tracking)
  - `temporal_smoothing.py` (reduce servo jitter)
  - `face_recognition_module.py` (optional — heavier)
- [ ] Create `Raspi/AI/vision_controller.py`:
  ```python
  class VisionController:
      def __init__(self, hardware_manager, frame_skip=3):
          # Gets frames from hardware_manager.camera.get_ai_frame()
          # Controls servos via hardware_manager.servo.set_angle(pan, tilt)
          # Triggers emergency via hardware_manager.trigger_emergency()
  ```
- [ ] Add AI initialization to `main.py`
- [ ] Configure AI to use 3 CPU cores (leave 1 for OS):
  ```bash
  OMP_NUM_THREADS=3 python3 main.py
  ```
- [ ] Implement frame skipping (process every 3rd frame)
- [ ] Add MQTT topics for AI output:
  - `vision/faces` — detected face events
  - `vision/objects` — object detection events
  - `vision/tracking` — current tracking status
  - `vision/alerts` — unknown face / alert events
- [ ] Stream AI-annotated frames via WebSocket
- [ ] Test face detection on Pi (verify FPS is acceptable)
- [ ] Test servo tracking coordination
- [ ] Add AI detection overlay to Dashboard

---

## 🟡 Phase 2 — Advanced Hardware (Optional)

- [ ] Buzzer support (audio alerts)
- [ ] Battery voltage monitoring → publish to `sensors/battery`
- [ ] IMU sensor (tilt detection, collision detection)
- [ ] Temperature monitoring (system overheat alerts)

---

## 🟢 Future Phases (Low Priority)

### Mobile App
- [ ] React Native or Flutter interface
- [ ] WebSocket video streaming
- [ ] Touch controls
- [ ] Push notifications for AI alerts

### Cloud Integration
- [ ] Video recording to cloud storage
- [ ] Event log / analytics dashboard
- [ ] Remote access via dynamic DNS + reverse proxy

### Autonomous Navigation
- [ ] Obstacle avoidance path planning
- [ ] Waypoint navigation
- [ ] Auto-patrol mode
- [ ] Return-to-home feature

---

## 📊 Progress Summary

| Component | Status | % |
|---|---|---|
| Hardware Layer | ✅ Complete | 100% |
| MQTT Communication | ✅ Complete | 100% |
| WebSocket Streaming | ✅ Complete | 100% |
| Desktop GUI | ✅ Complete | 100% |
| Web Dashboard | ✅ Complete | 100% |
| Phase 1 Testing | ⚠️ Pending | 0% |
| AI Vision Integration | 🔴 Not Started | 10%* |
| Mobile App | 📝 Future | 0% |
| Cloud Integration | 📝 Future | 5% |

*AI module exists standalone (Mizo), not yet merged into Final.

**Overall Project: ~90%**
