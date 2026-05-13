# Surveillance Car - AI Integrated System

## Quick Start

### 1. Install AI Dependencies (First Time Only)
```bash
# Install MediaPipe
pip3 install mediapipe --break-system-packages

# Install face_recognition (takes 30-60 minutes)
pip3 install face_recognition --break-system-packages
```

### 2. Add Known Faces
```bash
# Create folders for each person
mkdir -p pi_minimal/known_faces/Mohamed
mkdir -p pi_minimal/known_faces/Ahmed

# Add 2-3 clear face photos per person
# Copy photos to: pi_minimal/known_faces/PersonName/photo1.jpg
```

### 3. Run System
```bash
sudo ./start_ai_system.sh
```

### 4. Open Dashboard
- Open `Dashboard/index.html` in browser
- Enter Raspberry Pi IP address
- Click "Connect"

## Control Modes

### Manual Mode (Default)
- Control car with WASD keys or dashboard buttons
- Servo control with arrow keys
- LED control
- Standard MQTT commands

### AI Follow Mode
- Click "AI Follow" button in dashboard
- Car will autonomously follow recognized faces
- Tracks person using face + body detection
- Stops when person is close or lost

## Features

### Multicore Processing
- **Core 0**: MQTT, WebSocket, Camera, Motor control
- **Cores 1-3**: AI face detection, recognition, body tracking

### Mode Switching
- Switch between Manual and AI modes anytime
- Emergency stop works in both modes
- MQTT always has control priority

### AI Status Display
Dashboard shows:
- Current mode (MANUAL / AI FOLLOW)
- Person being tracked
- Recognition confidence
- Current AI action
- Face/body detection indicators

### Video Streaming
- Real-time video in both modes
- ~20 FPS over local network
- Works with Cloudflare Tunnel for WAN access

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Raspberry Pi                        │
│                                                      │
│  ┌──────────────┐         ┌──────────────┐         │
│  │   Core 0     │         │  Cores 1-3   │         │
│  │              │         │              │         │
│  │ • MQTT       │◄────────┤ • AI Face    │         │
│  │ • WebSocket  │  Queue  │   Detection  │         │
│  │ • Camera     │         │ • Recognition│         │
│  │ • Motor Ctrl │         │ • Tracking   │         │
│  └──────────────┘         └──────────────┘         │
│         │                                           │
│         ▼                                           │
│  ┌──────────────────────────────────┐              │
│  │      Hardware Drivers            │              │
│  │  Motor | Servo | LED | Ultrasonic│              │
│  └──────────────────────────────────┘              │
└─────────────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
    HiveMQ Cloud         Dashboard
    (MQTT WAN)          (WebSocket)
```

## Command Reference

### Mode Switching (MQTT)
```bash
# Manual mode
mosquitto_pub -h 78ed3eab06c348d0948ef7681cf4a377.s1.eu.hivemq.cloud \
  -p 8883 --capath /etc/ssl/certs/ \
  -u mohamed -P 'P@ssw0rd' \
  -t dev/mode -m '{"mode":"manual"}'

# AI follow mode
mosquitto_pub -h 78ed3eab06c348d0948ef7681cf4a377.s1.eu.hivemq.cloud \
  -p 8883 --capath /etc/ssl/certs/ \
  -u mohamed -P 'P@ssw0rd' \
  -t dev/mode -m '{"mode":"ai_follow"}'
```

### Emergency Stop
```bash
mosquitto_pub -h 78ed3eab06c348d0948ef7681cf4a377.s1.eu.hivemq.cloud \
  -p 8883 --capath /etc/ssl/certs/ \
  -u mohamed -P 'P@ssw0rd' \
  -t dev/commands -m '{"command":"emergency_stop"}'
```

## Files

### Main System
- `run_all_integrated.py` - Main integrated system (use this)
- `run_all.py` - Old system without AI (deprecated)
- `system_state.py` - Shared state manager
- `ai_controller.py` - AI wrapper

### Hardware Drivers
- `hardware/motor.py` - DC motor control (L298N)
- `hardware/servo.py` - Servo control (PCA9685)
- `hardware/led.py` - RGB LED control
- `hardware/ultrasonic.py` - Distance sensor

### AI System
- `pi_minimal/main.py` - Standalone AI code
- `pi_minimal/known_faces/` - Known people photos

### Dashboard
- `Dashboard/index.html` - Web dashboard
- `Dashboard/dashboard.js` - Dashboard logic
- `Dashboard/dashboard.css` - Dashboard styles

## Troubleshooting

### AI not working
1. Check dependencies: `python3 -c "import mediapipe, face_recognition"`
2. Check known faces: `ls -la pi_minimal/known_faces/`
3. Check logs for "[AI]" messages
4. Verify you're in AI Follow mode

### Mode not switching
1. Check MQTT connection in logs
2. Verify dashboard is connected
3. Check mode badge in dashboard
4. Try emergency stop to reset

### Poor AI performance
1. Reduce camera resolution in `ai_controller.py`
2. Use fewer known faces (2-3 people max)
3. Ensure good lighting
4. Check CPU temperature: `vcgencmd measure_temp`

### Video lag
1. Reduce JPEG quality in `run_all_integrated.py`
2. Lower camera FPS
3. Use local network instead of tunnel
4. Check network bandwidth

## Performance Tips

1. **Optimize known faces**: Use 2-3 clear photos per person
2. **Good lighting**: AI works best in well-lit environments
3. **Cooling**: Ensure Pi has adequate cooling for AI processing
4. **Network**: Use 5GHz WiFi for better video streaming
5. **Power**: Use quality 5V 3A power supply

## Safety

- Emergency stop works in **all modes**
- MQTT always has control priority
- Motor commands are queued and processed safely
- System shuts down cleanly on Ctrl+C

## Next Steps

1. ✅ Install dependencies
2. ✅ Add known face photos
3. ✅ Test system: `sudo ./start_ai_system.sh`
4. ✅ Open dashboard and connect
5. ✅ Test manual mode
6. ✅ Switch to AI mode
7. ✅ Test face tracking

## Documentation

- `AI_SETUP_GUIDE.md` - Detailed AI setup instructions
- `NGROK_SETUP.md` - Ngrok tunnel setup (deprecated)
- `CLOUDFLARE_TUNNEL_SETUP.md` - Cloudflare tunnel setup

## Support

Check logs for error messages:
- `[MQTT]` - MQTT connection issues
- `[WebSocket]` - Video streaming issues
- `[AI]` - AI processing issues
- `[Motor]` - Motor control issues
- `[Camera]` - Camera issues

For hardware issues, test components individually using test scripts in `hardware/` directory.
