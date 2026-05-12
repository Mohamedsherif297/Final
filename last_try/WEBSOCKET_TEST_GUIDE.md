# WebSocket Video Streaming - Test Guide

## Overview
You have two options for running the system:
1. **run_all.py** - Combined MQTT + WebSocket (RECOMMENDED)
2. **websocket_stream.py** - WebSocket only (for testing video stream alone)

## Prerequisites

### 1. Install Dependencies
```bash
cd ~/surveillance-car/last_try
sudo pip3 install --break-system-packages websockets opencv-python
```

Or install all requirements:
```bash
sudo pip3 install --break-system-packages -r requirements.txt
```

### 2. Pull Latest Code
```bash
cd ~/surveillance-car/last_try
git pull
```

## Testing Options

### Option A: Full System (MQTT + WebSocket) - RECOMMENDED
This runs everything: MQTT control + video streaming

```bash
cd ~/surveillance-car/last_try
sudo python3 run_all.py
```

**Expected Output:**
```
============================================================
Surveillance Car - Full System
============================================================
MQTT: 78ed3eab06c348d0948ef7681cf4a377.s1.eu.hivemq.cloud:8883
WebSocket: ws://0.0.0.0:8765
============================================================

[Hardware] Initializing...
[Motor] Initialized
[Servo] Pan: 90°
[Servo] Tilt: 90°
[Servo] Centered
[Servo] Initialized with PCA9685
[LED] Initialized
[Ultrasonic] Initialized
[Hardware] ✓ Initialized

[MQTT] Connecting...
[MQTT] ✅ Connected to HiveMQ Cloud
[Camera] Opening camera...
[Camera] Streaming 640x480 @ 20fps

[WebSocket] Starting server on ws://0.0.0.0:8765

[System] ✓ All systems running
============================================================
```

### Option B: WebSocket Only (Testing)
Test video streaming without MQTT

```bash
cd ~/surveillance-car/last_try
python3 websocket_stream.py
```

## Dashboard Configuration

### 1. Update Dashboard IP
In your dashboard, enter the Raspberry Pi IP address:
- **Local Network**: `192.168.1.100` (or your Pi's actual IP)
- **Port**: WebSocket runs on port `8765`

### 2. Connect
1. Open dashboard in browser
2. Enter Pi IP: `192.168.1.100`
3. Click "Connect"

### 3. What Should Happen
✅ **Connection Status**: Should show "Connected" (green)
✅ **Video Feed**: Should display live camera feed
✅ **FPS Counter**: Should show ~20 FPS
✅ **Motor Control**: WASD keys should work (if using run_all.py)
✅ **Servo Control**: Arrow keys should work (if using run_all.py)
✅ **LED Control**: Color buttons should work (if using run_all.py)

## Troubleshooting

### Camera Not Opening
```bash
# Check if camera is detected
ls -l /dev/video*

# Test camera manually
python3 -c "import cv2; cam = cv2.VideoCapture(0); print('Camera OK' if cam.isOpened() else 'Camera FAILED')"
```

### WebSocket Connection Failed
1. **Check Pi IP address**: `hostname -I`
2. **Check firewall**: `sudo ufw status` (should be inactive or allow port 8765)
3. **Check if port is in use**: `sudo netstat -tulpn | grep 8765`

### No Video in Dashboard
1. Check browser console (F12) for errors
2. Verify WebSocket connection is established
3. Check Pi terminal for "[WebSocket] Client connected" message
4. Try refreshing dashboard (Ctrl+F5)

### MQTT Not Working
1. Check internet connection on Pi: `ping 8.8.8.8`
2. Verify HiveMQ Cloud credentials
3. Check if MQTT connected: Look for "[MQTT] ✅ Connected" message

## System Architecture

```
┌─────────────────┐
│   Dashboard     │
│  (Web Browser)  │
└────────┬────────┘
         │
         ├─── MQTT (HiveMQ Cloud) ──→ Commands (motor, servo, LED)
         │         Port 8883
         │
         └─── WebSocket (Direct) ───→ Video Stream
                  Port 8765
                     │
              ┌──────┴──────┐
              │ Raspberry Pi │
              │  run_all.py  │
              └──────────────┘
```

## Performance Tips

### Reduce Latency
Edit `run_all.py` and adjust:
```python
VIDEO_FPS = 30        # Increase FPS (default: 20)
JPEG_QUALITY = 50     # Lower quality = less bandwidth (default: 65)
```

### Reduce Bandwidth
```python
VIDEO_WIDTH = 320     # Lower resolution (default: 640)
VIDEO_HEIGHT = 240    # (default: 480)
JPEG_QUALITY = 40     # Lower quality
```

## Stopping the System

Press **Ctrl+C** to stop the system gracefully:
```
^C
[System] Shutting down...
[Motor] Cleanup done
[Servo] Cleanup done
[LED] Cleanup done
[System] Shutdown complete
```

## Next Steps

Once WebSocket streaming is working:
1. ✅ Test video quality and FPS
2. ✅ Verify MQTT commands work simultaneously
3. ✅ Test from different devices (phone, tablet)
4. ✅ Consider adding authentication for security
5. ✅ Set up auto-start on boot (systemd service)
