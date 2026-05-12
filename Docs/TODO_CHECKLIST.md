# Surveillance Car — Feature Checklist

Granular tracking of every feature by phase.  
**Last Updated:** May 2026

---

## Phase 1 — Core System ✅ 100% Complete

### Hardware Control
- [x] Motor control (forward, backward, left, right, stop)
- [x] Smooth acceleration / deceleration
- [x] Direction change safety delay
- [x] Servo pan/tilt (angle-based, -90° to +90°)
- [x] Servo calibration and limits enforcement
- [x] RGB LED (solid colors, presets)
- [x] LED animation effects: rainbow, blink, pulse, fade, solid, off
- [x] LED status mapping: idle=blue, moving=green, emergency=red
- [x] Ultrasonic sensor (HC-SR04, 10 Hz)
- [x] Distance median/moving-average filter
- [x] Obstacle detection with callbacks (threshold: 20 cm)
- [x] Camera capture (OpenCV, 30 FPS, dual buffer)
- [x] AI-ready frame getter (`get_ai_frame()`)

### Safety Systems
- [x] Emergency stop (immediate halt)
- [x] 6 emergency triggers (OBSTACLE, COMM_TIMEOUT, WATCHDOG, MANUAL, GPIO_INVALID, HW_ERROR)
- [x] Watchdog monitoring (per-component heartbeats)
- [x] Hardware health monitoring
- [x] 4-layer safety architecture
- [x] Emergency LED + MQTT alert on trigger

### GPIO / Configuration
- [x] GPIO singleton manager (pin conflict detection, simulation mode)
- [x] PWM singleton manager (per-channel access)
- [x] YAML config for GPIO, PWM, servo, safety (no hardcoded values)
- [x] Environment variable overrides for all settings

### MQTT Communication
- [x] Local Mosquitto broker (port 1883)
- [x] HiveMQ cloud broker (port 8883, TLS)
- [x] Runtime broker switching
- [x] Auto-reconnect with exponential backoff
- [x] Subscribe: `dev/motor`, `dev/led`, `dev/servo`, `dev/commands`
- [x] Publish: `dev/status`, `sensors/ultrasonic`, `sensors/obstacle`, `emergency/alert`
- [x] Sensor data publishing at 10 Hz
- [x] Emergency alerts

### WebSocket Streaming
- [x] Async WebSocket server (port 8765)
- [x] Multi-client broadcast with per-client queues
- [x] Backpressure control (drop oldest frame when queue full)
- [x] Binary protocol: `0x00`=JSON, `0x01`=video, `0x02`=audio
- [x] Video: 640×480 JPEG @ 20 FPS
- [x] Audio: 16 kHz mono PCM
- [x] MQTT bridge (WS commands → MQTT, MQTT events → WS)
- [x] WAN-ready (port forwarding / nginx reverse proxy)
- [x] Configurable via environment variables

### Desktop GUI (Laptop)
- [x] Tkinter dark-themed interface
- [x] D-pad movement controls
- [x] Arrow key + WASD keyboard shortcuts
- [x] Speed slider (0–100%)
- [x] Servo slider (0–180°)
- [x] LED on/off/blink buttons
- [x] Beep command
- [x] Live Pi status display
- [x] Scrolling event log
- [x] Local ↔ Cloud broker switching
- [x] Batch command utility
- [x] Connection testing tools
- [x] Network scanner

### Web Dashboard
- [x] Single-page, no install required (open index.html)
- [x] WebSocket connection to Pi (single connection for all data + commands)
- [x] Live video feed (JPEG decode → canvas)
- [x] FPS counter overlay
- [x] D-pad motor control (clickable / touch)
- [x] Arrow key motor control
- [x] WASD servo control
- [x] Motor/Servo mode toggle (swap arrow key behavior)
- [x] Speed slider (0–100%)
- [x] Servo pan slider (-90° to +90°)
- [x] Servo tilt slider (-90° to +90°)
- [x] Crosshair position visualizer (maps pan/tilt to dot on circle)
- [x] Servo center button
- [x] LED presets: idle / moving / alert / off
- [x] LED effects: rainbow / blink / pulse
- [x] RGB color picker with Set button
- [x] LED color preview dot (live)
- [x] Emergency stop button (animated glow when active)
- [x] Emergency reset button
- [x] Ultrasonic distance gauge (arc gauge, color coded)
- [x] System status badges (motor, servo pan/tilt, emergency, obstacle)
- [x] Event log (scrolling, timestamped, color-coded by type)
- [x] Connection status pill (Connected/Disconnected/Error)
- [x] Uptime counter
- [x] IP input + Connect/Disconnect button
- [x] Responsive layout (desktop/tablet/mobile)

### System Orchestration
- [x] `main.py` orchestrates Hardware + MQTT + WebSocket concurrently
- [x] asyncio event loop for WebSocket + video + audio
- [x] MQTT runs in daemon thread
- [x] Signal handling (SIGINT/SIGTERM) → graceful shutdown
- [x] Component lifecycle management (init → run → cleanup)

### Documentation
- [x] `Raspi/Docs/README.md` — full Raspi guide
- [x] `Raspi/Docs/QUICK_START.md`
- [x] `Raspi/Docs/ARCHITECTURE.md` — design patterns, threading model
- [x] `Raspi/Docs/SYSTEM_DIAGRAM.md` — ASCII diagrams
- [x] `Raspi/Docs/DEPLOYMENT_CHECKLIST.md`
- [x] `Dashboard/README.md` — dashboard usage
- [x] `Docs/COMPLETE_SUMMARY.md`
- [x] `Docs/STRUCTURE.md`
- [x] `Docs/ToDo.md`
- [x] `Docs/TODO_CHECKLIST.md` — this file
- [x] `Docs/CONNECTIONS_GUIDE.md` — hardware wiring

### Testing
- [x] `test_hardware.py` — full hardware suite
- [x] `test_hardware_fixed.py`
- [x] `test_hardware_pan_only.py`
- [x] `test_mqtt_system.py`
- [x] `test_integration.py`
- [x] `mqtt_client_tester.py`

---

## Phase 1 — Testing ⚠️ Pending (0%)

- [ ] MQTT local connection test (Pi ↔ Laptop GUI)
- [ ] MQTT WAN connection test (via HiveMQ)
- [ ] WebSocket local connection test
- [ ] WebSocket WAN connection test (port forwarding)
- [ ] Hardware response test (each component)
- [ ] Web Dashboard end-to-end test
- [ ] Desktop GUI + Dashboard simultaneous test
- [ ] Performance test (video FPS under load)
- [ ] Graceful shutdown test
- [ ] Emergency stop test (trigger + reset)
- [ ] Obstacle detection test

---

## Phase 2 — AI Vision Integration 🔴 (10%)

### Prerequisite Decision
- [ ] Choose servo hardware: GPIO PWM (current Final) or PCA9685 I2C (Mizo)

### AI Module Files to Create/Copy
- [ ] `Raspi/AI/__init__.py`
- [ ] `Raspi/AI/vision_controller.py` (main integration point)
- [ ] `Raspi/AI/blazeface_detector.py` (from Mizo)
- [ ] `Raspi/AI/pid_controller.py` (from Mizo)
- [ ] `Raspi/AI/temporal_smoothing.py` (from Mizo)
- [ ] `Raspi/AI/face_recognition_module.py` (optional)
- [ ] `Raspi/AI/known_faces/` (face database directory)
- [ ] `Raspi/AI/models/blaze_face_short_range.tflite` (bundled model)

### Vision Controller Implementation
- [ ] Read frames from `hardware_manager.camera.get_ai_frame()`
- [ ] Frame skipping (process every Nth frame, default N=3)
- [ ] Face detection (BlazeFace primary, Haar Cascade fallback)
- [ ] Face tracking with PID → servo angles
- [ ] Temporal smoothing to reduce jitter
- [ ] Publish detections to `vision/faces` MQTT topic
- [ ] Stream AI-annotated frames via WebSocket
- [ ] Connect AI alerts to `hardware_manager.trigger_emergency()`

### Multi-core Configuration
- [ ] Configure AI to use 3 cores (leave 1 for OS+networking)
- [ ] Test performance on Pi4 with AI + video stream running
- [ ] Benchmark: target > 10 FPS on AI processing

### Main.py Integration
- [ ] Add `ENABLE_AI = True` flag in main.py
- [ ] Initialize `VisionController` in system startup
- [ ] Start AI processing loop alongside existing loops
- [ ] Clean shutdown of AI thread

### Dashboard AI Features
- [ ] AI detection overlay on video canvas
- [ ] Face count / detected names in status panel
- [ ] AI status badge (enabled/disabled, FPS)

---

## Phase 3 — Future (Not Started)

### Advanced Hardware
- [ ] Buzzer driver (`dev/commands` beep)
- [ ] Battery voltage ADC reading → `sensors/battery`
- [ ] Temperature sensor → `sensors/temperature`

### Mobile App
- [ ] WebSocket video client
- [ ] Touch D-pad controls
- [ ] Push notifications (emergency alerts)

### Cloud / Remote Access
- [ ] Dynamic DNS setup
- [ ] nginx + TLS reverse proxy for wss://
- [ ] Video recording to cloud storage
- [ ] Analytics dashboard

### Autonomous Navigation
- [ ] Obstacle map from ultrasonic data
- [ ] Path planning algorithm
- [ ] Patrol waypoints
- [ ] Return-to-home feature
