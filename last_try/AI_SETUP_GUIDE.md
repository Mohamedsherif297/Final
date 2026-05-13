# AI Face Tracking Setup Guide

## Overview
This guide will help you install and configure the AI face recognition and tracking system on your Raspberry Pi.

## Prerequisites
- Raspberry Pi 4 (recommended for AI processing)
- Python 3.7+
- Camera connected and working
- Existing system running (MQTT + WebSocket)

## Installation Steps

### 1. Install System Dependencies
```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install required system packages
sudo apt-get install -y \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libatlas-base-dev \
    gfortran
```

### 2. Install Python Dependencies
```bash
cd /home/iot/IOT\ /Final/last_try

# Install MediaPipe (lightweight, optimized for Pi)
pip3 install mediapipe --break-system-packages

# Install face_recognition (CPU-intensive, may take time)
pip3 install face_recognition --break-system-packages

# If face_recognition fails, try installing dependencies first:
pip3 install dlib --break-system-packages
pip3 install face_recognition --break-system-packages
```

**Note:** Installing `face_recognition` on Raspberry Pi can take 30-60 minutes as it compiles dlib from source.

### 3. Prepare Known Faces Directory
```bash
# Create directory structure
mkdir -p pi_minimal/known_faces

# Add known people (example)
mkdir -p pi_minimal/known_faces/Mohamed
mkdir -p pi_minimal/known_faces/Ahmed
mkdir -p pi_minimal/known_faces/Sara

# Add photos (3-5 photos per person recommended)
# Copy photos to respective folders:
# pi_minimal/known_faces/Mohamed/photo1.jpg
# pi_minimal/known_faces/Mohamed/photo2.jpg
# etc.
```

**Photo Requirements:**
- Clear, well-lit face photos
- Face should be clearly visible
- Multiple angles recommended
- JPG, JPEG, or PNG format
- Resolution: 640x480 or higher

### 4. Test AI System (Standalone)
```bash
# Test the original AI code
cd pi_minimal
python3 main.py --dry-run --display

# If working, test with GPIO
sudo python3 main.py --display
```

### 5. Run Integrated System
```bash
cd /home/iot/IOT\ /Final/last_try

# Run integrated system with AI
sudo python3 run_all_integrated.py
```

## System Architecture

### CPU Core Allocation
- **Core 0**: MQTT, WebSocket, Camera capture, Motor control
- **Cores 1-3**: AI processing (face detection, recognition, body tracking)

### Control Modes

#### Manual Mode (Default)
- MQTT commands control the car
- Dashboard controls work normally
- AI is idle but ready

#### AI Follow Mode
- AI autonomously follows recognized faces
- Tracks person using face + body detection
- Motor commands come from AI
- MQTT can still switch modes or emergency stop

### Mode Switching

**From Dashboard:**
- Click "Manual Control" button → Manual mode
- Click "AI Follow" button → AI mode

**From MQTT:**
```bash
# Switch to manual
mosquitto_pub -h 78ed3eab06c348d0948ef7681cf4a377.s1.eu.hivemq.cloud \
  -p 8883 --capath /etc/ssl/certs/ \
  -u mohamed -P 'P@ssw0rd' \
  -t dev/mode \
  -m '{"mode":"manual"}'

# Switch to AI follow
mosquitto_pub -h 78ed3eab06c348d0948ef7681cf4a377.s1.eu.hivemq.cloud \
  -p 8883 --capath /etc/ssl/certs/ \
  -u mohamed -P 'P@ssw0rd' \
  -t dev/mode \
  -m '{"mode":"ai_follow"}'
```

### Emergency Stop
Emergency stop works in **both modes** and has highest priority:
```bash
mosquitto_pub -h 78ed3eab06c348d0948ef7681cf4a377.s1.eu.hivemq.cloud \
  -p 8883 --capath /etc/ssl/certs/ \
  -u mohamed -P 'P@ssw0rd' \
  -t dev/commands \
  -m '{"command":"emergency_stop"}'
```

## Dashboard Features

### AI Status Display
- **Mode Badge**: Shows current mode (MANUAL / AI FOLLOW)
- **Tracking**: Shows name of person being tracked
- **Confidence**: Recognition confidence percentage
- **Action**: Current AI action (forward, left, right, stop)
- **Detection Indicators**: 
  - 👤 Face detected
  - 🚶 Body detected

### Video Streaming
- Works in both modes
- In AI mode, you can see what the AI sees
- Frame rate: ~20 FPS

## Performance Tips

### Optimize AI Performance
1. **Reduce known faces**: Fewer faces = faster recognition
2. **Lower camera resolution**: Edit `ai_controller.py`:
   ```python
   FRAME_WIDTH = 320  # Instead of 640
   FRAME_HEIGHT = 240  # Instead of 480
   ```
3. **Adjust detection confidence**: Lower = faster but less accurate
4. **Use fewer photos per person**: 2-3 photos is enough

### Monitor Performance
```bash
# Check CPU usage
htop

# Check temperature
vcgencmd measure_temp

# Check AI processing in logs
# Look for "[AI]" messages in terminal
```

## Troubleshooting

### AI Not Starting
```bash
# Check if MediaPipe is installed
python3 -c "import mediapipe; print('OK')"

# Check if face_recognition is installed
python3 -c "import face_recognition; print('OK')"

# Check known faces directory
ls -la pi_minimal/known_faces/
```

### Slow Performance
- Reduce camera resolution
- Reduce number of known faces
- Ensure Pi has adequate cooling
- Check CPU temperature: `vcgencmd measure_temp`

### AI Not Tracking
- Ensure you're in AI Follow mode
- Check that known faces are loaded (see startup logs)
- Verify face photos are clear and well-lit
- Try standing closer to camera
- Check lighting conditions

### Mode Not Switching
- Check MQTT connection
- Verify dashboard is connected
- Check terminal logs for mode change messages
- Try emergency stop to reset

## File Structure
```
last_try/
├── run_all_integrated.py      # Main integrated system
├── system_state.py             # Shared state manager
├── ai_controller.py            # AI wrapper
├── hardware/                   # Hardware drivers
│   ├── motor.py
│   ├── servo.py
│   ├── led.py
│   └── ultrasonic.py
└── pi_minimal/                 # AI system
    ├── main.py                 # Original AI code
    ├── requirements.txt
    └── known_faces/            # Known people photos
        ├── Person1/
        │   ├── photo1.jpg
        │   └── photo2.jpg
        └── Person2/
            └── photo1.jpg
```

## Next Steps
1. Install dependencies
2. Add known face photos
3. Test standalone AI system
4. Run integrated system
5. Test mode switching from dashboard
6. Test AI tracking with known person

## Support
If you encounter issues:
1. Check terminal logs for error messages
2. Verify all dependencies are installed
3. Test hardware individually
4. Check MQTT connection
5. Verify camera is working
