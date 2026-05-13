# Quick Reference Card

## 🚀 Start System
```bash
cd ~/surveillance-car/last_try
sudo ./start_ai_system.sh
```

## 🌐 Dashboard
1. Open `Dashboard/index.html`
2. Enter Pi IP: `192.168.1.12`
3. Click "Connect"

## 🎮 Controls

### Keyboard (Manual Mode)
- **W** - Forward
- **S** - Backward
- **A** - Left
- **D** - Right
- **↑↓←→** - Servo control
- **Q/E** - Speed down/up

### Dashboard Buttons
- **Manual Control** - Switch to manual mode
- **AI Follow** - Switch to AI autonomous mode
- **Emergency Stop** - Stop everything immediately
- **Center Servo** - Reset camera to center

## 📡 MQTT Topics

### Mode Switching
```bash
# Manual mode
Topic: dev/mode
Payload: {"mode":"manual"}

# AI follow mode
Topic: dev/mode
Payload: {"mode":"ai_follow"}
```

### Motor Control (Manual mode only)
```bash
Topic: dev/motor
Payload: {"direction":"forward","speed":70}
# direction: forward, backward, left, right, stop
# speed: 0-100
```

### Servo Control
```bash
Topic: dev/servo
Payload: {"pan":90,"tilt":90}
# pan: 0-180 (left to right)
# tilt: 0-180 (down to up)
```

### LED Control
```bash
Topic: dev/led
Payload: {"red":255,"green":0,"blue":0}
# red, green, blue: 0-255
```

### Commands
```bash
Topic: dev/commands
Payloads:
  {"command":"emergency_stop"}
  {"command":"reset_emergency"}
  {"command":"center"}
  {"command":"stop_all"}
```

## 🤖 AI Mode

### How It Works
1. Click "AI Follow" in dashboard
2. Stand in front of camera
3. Car recognizes you and follows
4. Stops when close or you're lost

### Known Faces
Located in: `pi_minimal/known_faces/images/`
- karim A (9 photos)
- mezo (9 photos)
- obooda (9 photos)

### Add New Person
```bash
mkdir -p pi_minimal/known_faces/images/YourName
# Add 3-5 clear face photos
# Restart system to load new faces
```

## 📊 Dashboard Status

### Connection Status
- **Green dot** - Connected
- **Red dot** - Disconnected

### Mode Badge
- **MANUAL** - Manual control active
- **AI FOLLOW** - AI autonomous mode

### AI Status
- **Tracking** - Person being followed
- **Confidence** - Recognition accuracy (%)
- **Action** - Current AI action
- **👤** - Face detected
- **🚶** - Body detected

## 🔧 Troubleshooting

### System Won't Start
```bash
# Check dependencies
python3 -c "import mediapipe, face_recognition"

# Check permissions
sudo chmod +x start_ai_system.sh
```

### AI Not Working
```bash
# Check known faces
ls -la pi_minimal/known_faces/images/

# Check logs
# Look for "[AI]" messages in terminal
```

### Dashboard Not Connecting
```bash
# Check Pi IP
hostname -I

# Check if system is running
ps aux | grep python3

# Check WebSocket port
sudo netstat -tulpn | grep 8765
```

### Mode Not Switching
- Check MQTT connection (green dot)
- Check mode badge in dashboard
- Try emergency stop to reset

## 📁 Important Files

### Main System
- `run_all_integrated.py` - Use this (AI integrated)
- `run_all.py` - Old system (no AI)
- `start_ai_system.sh` - Easy startup

### Hardware
- `hardware/motor.py` - Motor control
- `hardware/servo.py` - Servo control
- `hardware/led.py` - LED control
- `hardware/ultrasonic.py` - Distance sensor

### AI
- `ai_controller.py` - AI wrapper
- `system_state.py` - State manager
- `pi_minimal/main.py` - Original AI code

### Dashboard
- `Dashboard/index.html` - Web interface
- `Dashboard/dashboard.js` - Logic
- `Dashboard/dashboard.css` - Styles

## 🔒 Safety

### Emergency Stop
- Works in **all modes**
- Highest priority
- Stops motors immediately
- Clears command queue

### Priority Order
1. Emergency stop (highest)
2. Manual MQTT commands
3. AI commands (lowest)

## 📈 Performance

### Expected
- Video: 15-20 FPS
- AI: 5-10 FPS
- Recognition: 1-2 seconds
- CPU: 60-100% (all cores)
- Temp: 60-75°C

### Optimize
- Reduce camera resolution
- Use fewer known faces
- Ensure good cooling
- Use 5GHz WiFi

## 🌐 Network

### Local (LAN)
- WebSocket: `ws://192.168.1.12:8765`
- Dashboard connects directly

### WAN
- MQTT: HiveMQ Cloud (always works)
- WebSocket: Use Cloudflare Tunnel
  ```bash
  cloudflared tunnel --url tcp://localhost:8765
  ```

## 📚 Documentation

- `AI_SETUP_GUIDE.md` - Detailed setup
- `README_AI_INTEGRATED.md` - Quick start
- `INTEGRATION_COMPLETE.md` - Full overview
- `QUICK_REFERENCE.md` - This file

## 🆘 Support

### Check Logs
Look for these prefixes:
- `[MQTT]` - MQTT issues
- `[WebSocket]` - Video streaming
- `[AI]` - AI processing
- `[Motor]` - Motor control
- `[Camera]` - Camera issues
- `[System]` - General system

### Common Issues

**"Permission denied"**
→ Use `sudo`

**"Module not found"**
→ Install with `pip3 install <module> --break-system-packages`

**"Camera not found"**
→ Check camera connection: `vcgencmd get_camera`

**"MQTT connection failed"**
→ Check internet connection and credentials

**"AI not tracking"**
→ Check lighting, distance, and known faces

## 🎯 Quick Test Sequence

1. ✅ Start system: `sudo ./start_ai_system.sh`
2. ✅ Open dashboard and connect
3. ✅ Test manual mode (WASD keys)
4. ✅ Test servo (arrow keys)
5. ✅ Switch to AI mode
6. ✅ Stand in front of camera
7. ✅ Verify tracking works
8. ✅ Test emergency stop
9. ✅ Switch back to manual

## 📞 Contact

GitHub: https://github.com/Mohamedsherif297/Final
Branch: main

---

**Ready to test!** Pull code on Pi and run `sudo ./start_ai_system.sh` 🚀
