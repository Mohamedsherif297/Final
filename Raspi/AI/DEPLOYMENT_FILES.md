# 📦 Minimal Files Needed for Raspberry Pi Deployment

## 🎯 Overview

This document lists the **minimal essential files** needed to run Mizo's AI face recognition system on Raspberry Pi.

---

## 📁 Required File Structure

```
Raspi/AI/
│
├── main.py                          # ✅ REQUIRED - Main GUI application
├── config.py                        # ✅ REQUIRED - Configuration settings
├── requirements.txt                 # ✅ REQUIRED - Python dependencies
├── setup.py                         # ✅ REQUIRED - Download models & setup
│
├── core/                            # ✅ REQUIRED - Core modules
│   ├── __init__.py
│   ├── camera.py                    # Camera capture (USB/PiCamera)
│   ├── detector.py                  # Face detection (MediaPipe)
│   ├── recognizer.py                # Face recognition (TFLite)
│   ├── tracker.py                   # Kalman tracking
│   ├── pipeline.py                  # Main AI pipeline
│   └── servo.py                     # Servo control (optional)
│
├── dataset/                         # ✅ REQUIRED - Face database
│   ├── faces/                       # Enrolled face images
│   │   ├── Person1/
│   │   │   ├── face_0000.jpg
│   │   │   └── face_0001.jpg
│   │   └── Person2/
│   │       └── face_0000.jpg
│   └── encodings.pkl                # Face embeddings (generated)
│
└── models/                          # ✅ REQUIRED - AI models
    ├── mobilefacenet.tflite         # Face recognition model (~5 MB)
    └── (MediaPipe bundles detection model internally)
```

---

## 📋 File-by-File Breakdown

### 🎯 Core Application Files (4 files)

| File | Size | Purpose | Required? |
|------|------|---------|-----------|
| `main.py` | ~30 KB | GUI application with Tkinter | ✅ YES |
| `config.py` | ~3 KB | All configuration settings | ✅ YES |
| `requirements.txt` | ~1 KB | Python dependencies | ✅ YES |
| `setup.py` | ~5 KB | Download models & setup | ✅ YES |

### 🧠 Core Modules (7 files in `core/`)

| File | Size | Purpose | Required? |
|------|------|---------|-----------|
| `core/__init__.py` | <1 KB | Package marker | ✅ YES |
| `core/camera.py` | ~8 KB | Camera capture (USB/PiCamera2) | ✅ YES |
| `core/detector.py` | ~6 KB | Face detection (MediaPipe) | ✅ YES |
| `core/recognizer.py` | ~15 KB | Face recognition (TFLite) | ✅ YES |
| `core/tracker.py` | ~10 KB | Kalman tracking | ✅ YES |
| `core/pipeline.py` | ~12 KB | Main AI pipeline | ✅ YES |
| `core/servo.py` | ~8 KB | Servo control (PCA9685) | ⚠️ OPTIONAL |

### 📊 Data Files

| File/Folder | Size | Purpose | Required? |
|-------------|------|---------|-----------|
| `dataset/faces/` | Varies | Enrolled face images | ✅ YES (empty OK) |
| `dataset/encodings.pkl` | Varies | Face embeddings | ⚠️ Generated |
| `models/mobilefacenet.tflite` | ~5 MB | Recognition model | ✅ YES |

---

## 📦 Total Size Breakdown

```
Core Python files:     ~100 KB
AI Model (TFLite):     ~5 MB
Face dataset:          ~1-10 MB (depends on enrolled faces)
Python packages:       ~200 MB (installed via pip)
─────────────────────────────────────────
TOTAL:                 ~205-215 MB
```

---

## 🚀 Deployment Steps

### Step 1: Copy Files to Raspberry Pi

```bash
# On your laptop, create a deployment package
cd zLast_development/Mizo/IOT-Surveillance-Car-merged-ai-computer-vision/Raspi

# Copy to Pi (replace with your Pi's IP)
scp -r AI/ pi@192.168.1.10:~/
```

### Step 2: Install Dependencies on Pi

```bash
# SSH into Raspberry Pi
ssh pi@192.168.1.10

# Navigate to AI folder
cd ~/AI

# Install Python packages
pip3 install -r requirements.txt

# Download AI models
python3 setup.py
```

### Step 3: Configure for Raspberry Pi

Edit `config.py`:
```python
USE_PICAMERA2 = True   # If using Pi Camera
# or
CAMERA_INDEX = 0       # If using USB webcam

ENABLE_SERVO = True    # If you have servos connected
FLIP_H = True          # Mirror correction
```

### Step 4: Run

```bash
python3 main.py
```

---

## 📝 Detailed File Descriptions

### 1. **`main.py`** (30 KB)
- **Purpose**: Main GUI application
- **Features**:
  - Dark-themed Tkinter interface
  - Live video feed display
  - Face detection/recognition display
  - Enrollment dialog
  - Settings panel
  - System stats (FPS, CPU, memory)
- **Dependencies**: tkinter, PIL, cv2, numpy
- **Can run without**: Servo control

### 2. **`config.py`** (3 KB)
- **Purpose**: Centralized configuration
- **Settings**:
  - Camera (resolution, FPS, flip)
  - AI (thresholds, frame skipping)
  - Servo (pins, limits, PID)
  - Display (window size, colors)
- **Edit this file** to customize behavior

### 3. **`requirements.txt`** (1 KB)
- **Purpose**: Python package list
- **Key packages**:
  - `opencv-python` - Camera & image processing
  - `mediapipe` - Face detection (TFLite)
  - `numpy` - Array operations
  - `Pillow` - Image display in GUI
  - `psutil` - System stats
  - `insightface` - Fallback recognizer
  - `onnxruntime` - ONNX model runtime

### 4. **`setup.py`** (5 KB)
- **Purpose**: Download AI models
- **Downloads**:
  - MobileFaceNet TFLite model (~5 MB)
  - Creates necessary directories
  - Validates installation
- **Run once** after copying files

### 5. **`core/camera.py`** (8 KB)
- **Purpose**: Camera capture abstraction
- **Supports**:
  - USB webcam (cv2.VideoCapture)
  - Raspberry Pi Camera (picamera2)
- **Features**:
  - Threaded capture for performance
  - FPS tracking
  - Frame flipping
  - Auto-detection of camera type

### 6. **`core/detector.py`** (6 KB)
- **Purpose**: Face detection
- **Method**: MediaPipe BlazeFace (TFLite)
- **Performance**: 15-20 FPS on Pi 4
- **Output**: Bounding boxes [(x1,y1,x2,y2), ...]

### 7. **`core/recognizer.py`** (15 KB)
- **Purpose**: Face recognition
- **Method**: MobileFaceNet (TFLite)
- **Features**:
  - 128-dimensional embeddings
  - Cosine similarity matching
  - Multiple embeddings per person
  - Fallback to InsightFace (ONNX)
- **Performance**: 5-10 FPS on Pi 4

### 8. **`core/tracker.py`** (10 KB)
- **Purpose**: Multi-object tracking
- **Method**: Kalman filter + IoU matching
- **Features**:
  - Smooth tracking across frames
  - Handles occlusions
  - Assigns unique IDs
  - Maintains identity

### 9. **`core/pipeline.py`** (12 KB)
- **Purpose**: Main AI processing pipeline
- **Flow**:
  1. Get frame from camera
  2. Detect faces
  3. Recognize faces (every N frames)
  4. Track faces
  5. Update servos (if enabled)
  6. Send results to GUI
- **Runs in**: Separate thread

### 10. **`core/servo.py`** (8 KB) - OPTIONAL
- **Purpose**: Servo motor control
- **Hardware**: PCA9685 I2C driver
- **Features**:
  - PID controller
  - Smooth movements
  - Speed limiting
  - Deadzone
- **Only needed if**: You have pan/tilt servos

---

## ⚙️ Configuration Options

### Minimal Configuration (No Servos)
```python
# config.py
CAMERA_INDEX = 0
USE_PICAMERA2 = False
ENABLE_SERVO = False
FLIP_H = True
```

### Full Configuration (With Servos)
```python
# config.py
CAMERA_INDEX = 0
USE_PICAMERA2 = True
ENABLE_SERVO = True
PAN_CHANNEL = 0
TILT_CHANNEL = 1
```

### Performance Tuning
```python
# For better FPS on Pi 3
AI_W = 240
AI_H = 180
RECOG_EVERY_N = 10  # Recognize every 10th frame

# For better accuracy on Pi 4
AI_W = 320
AI_H = 240
RECOG_EVERY_N = 5
```

---

## 🔧 Optional Files (Not Required)

These files are in the full project but **NOT needed** for basic operation:

| File | Purpose | Needed? |
|------|---------|---------|
| `gui_tracker.py` | Alternative GUI (root folder) | ❌ NO (use main.py) |
| `enroll_faces.py` | CLI enrollment tool | ❌ NO (GUI has enrollment) |
| `blazeface_detector.py` | Alternative detector | ❌ NO (core/detector.py) |
| `yolo_face_detector.py` | YOLO detector | ❌ NO (slower) |
| `face_recognition_module.py` | dlib recognizer | ❌ NO (slower) |
| `pid_controller.py` | Standalone PID | ❌ NO (in core/servo.py) |
| `video_recorder.py` | Recording feature | ❌ NO (optional) |
| `tiny_llm.py` | AI assistant | ❌ NO (optional) |

---

## 📊 Comparison: Full vs Minimal

| Aspect | Full Project | Minimal Deployment |
|--------|--------------|-------------------|
| Files | ~35 files | ~15 files |
| Size | ~50 MB | ~5 MB (code only) |
| Dependencies | 15+ packages | 6 core packages |
| Features | All features | Core features only |
| Complexity | High | Low |

---

## ✅ Checklist for Deployment

### Before Copying to Pi:
- [ ] Have all files in `Raspi/AI/` folder
- [ ] `requirements.txt` is present
- [ ] `setup.py` is present
- [ ] `core/` folder has all modules
- [ ] `dataset/` folder exists (can be empty)
- [ ] `models/` folder exists (can be empty)

### On Raspberry Pi:
- [ ] Python 3.7+ installed
- [ ] pip3 installed
- [ ] Camera connected (USB or Pi Camera)
- [ ] I2C enabled (if using servos)
- [ ] Dependencies installed (`pip3 install -r requirements.txt`)
- [ ] Models downloaded (`python3 setup.py`)
- [ ] `config.py` edited for your setup

### Testing:
- [ ] Camera detected: `ls /dev/video*`
- [ ] Python imports work: `python3 -c "import cv2, mediapipe"`
- [ ] GUI launches: `python3 main.py`
- [ ] Camera feed visible
- [ ] Face detection working
- [ ] Can enroll a face
- [ ] Face recognition working

---

## 🎯 Quick Deployment Command

```bash
# One-line deployment (from your laptop)
cd zLast_development/Mizo/IOT-Surveillance-Car-merged-ai-computer-vision && \
tar -czf raspi-ai.tar.gz Raspi/AI && \
scp raspi-ai.tar.gz pi@192.168.1.10:~/ && \
ssh pi@192.168.1.10 "tar -xzf raspi-ai.tar.gz && cd Raspi/AI && pip3 install -r requirements.txt && python3 setup.py"
```

---

## 💡 Summary

### Absolute Minimum (Core Functionality):
```
4 Python files (main, config, requirements, setup)
7 Core modules (core/*.py)
1 AI model (mobilefacenet.tflite)
= ~5 MB total
```

### Recommended (With Face Database):
```
Above + enrolled face images
= ~10-20 MB total
```

### Full System (With All Features):
```
Above + servo control + optional features
= ~25 MB total
```

**Bottom Line**: You need **~15 files** and **~5 MB** for a working system!
