# Surveillance Car — Complete System Summary

**Overall Completion: ~90%** | Last Updated: May 2026

---

## ✅ Phase 1 — Core System (100% Complete)

### 🤖 Raspberry Pi (`Final/Raspi/`)

#### Hardware Layer — `Drivers/hardware/` (36 modules)
| Subsystem | Key Files | Status |
|---|---|---|
| Motor | `motor_controller.py`, `motor_driver.py`, `motor_safety.py` | ✅ |
| Servo | `servo_controller.py`, `servo_calibration.py`, `servo_limits.py` | ✅ |
| LED | `led_controller.py`, `led_effects.py`, `led_patterns.py` | ✅ |
| Ultrasonic | `ultrasonic_controller.py`, `distance_filter.py`, `obstacle_detection.py` | ✅ |
| Camera | `camera_controller.py`, `frame_buffer.py`, `stream_handler.py` | ✅ |
| Safety | `emergency_stop.py`, `watchdog.py`, `hardware_monitor.py` | ✅ |
| GPIO/PWM | `gpio_manager.py`, `pwm_manager.py` | ✅ |
| Hardware Manager | `hardware_manager.py` (Facade/Singleton coordinator) | ✅ |

**Default GPIO Pin Mapping (BCM):**
- Motors: EN1=12, IN1=23, IN2=24 / EN2=13, IN3=27, IN4=22
- Servos: Pan=17, Tilt=18
- RGB LED: R=16, G=20, B=21
- Ultrasonic: Trig=5, Echo=6

**4-Layer Safety System:**
1. Input Validation (speed 0–100, valid directions, angle ranges)
2. Component Safety (acceleration limits, direction-change delays)
3. System Safety (obstacle threshold 20 cm, watchdog timeouts)
4. Emergency Override (immediate halt, LED red, MQTT alert, blocks commands)

#### Network Layer — `Network/`

**MQTT (`Network/MQTT/`):**

| Topic | Direction | Purpose |
|---|---|---|
| `dev/motor` | Subscribe | Motor commands `{"direction":"forward","speed":80}` |
| `dev/led` | Subscribe | LED commands `{"action":"set_rgb","red":255,...}` |
| `dev/servo` | Subscribe | Servo commands `{"action":"set_angle","pan":45,"tilt":20}` |
| `dev/commands` | Subscribe | General commands `{"command":"emergency_stop"}` |
| `dev/status` | Publish | Status updates |
| `sensors/ultrasonic` | Publish | Distance @ 10 Hz |
| `sensors/obstacle` | Publish | Obstacle alerts |
| `emergency/alert` | Publish | Emergency events |

Supports both local Mosquitto (port 1883) and HiveMQ cloud (port 8883, TLS).

**WebSocket (`Network/WebSockets/`):**

| File | Purpose |
|---|---|
| `websocket_server.py` | Async multi-client server, MQTT bridge, backpressure queues |
| `video_stream_handler.py` | OpenCV capture → JPEG encode → async broadcast |
| `audio_system.py` | PyAudio mic capture → PCM → async broadcast |
| `config.py` | All tunable params via environment variables |

Binary frame protocol: `0x00`=JSON, `0x01`=video JPEG, `0x02`=audio PCM.  
Server listens on `ws://PI_IP:8765`.

#### Configuration — `config/hardware/`
- `gpio_config.yaml` — pin assignments
- `pwm_config.yaml` — PWM frequencies
- `servo_config.yaml` — angle limits and presets
- `safety_config.yaml` — obstacle threshold, watchdog timeout

---

### 💻 Laptop Controller (`Final/Laptop/`)

Tkinter GUI — dark themed. Features:
- D-pad + WASD/arrow keyboard movement
- Speed slider (0–100%), Servo slider (0–180°)
- LED on/off/blink, Beep, Center servo
- Live Pi status display + scrolling log
- Runtime local ↔ cloud MQTT broker switching

---

### 🌐 Web Dashboard (`Final/Dashboard/`)

Browser-based dashboard — open `index.html` directly. No server required.

**Features:**
- Live video feed (640×480, JPEG over WebSocket)
- Movement D-pad + keyboard (arrows/WASD)
- **Dual arrow-key mode**: arrows → Motor OR Servo (toggle with Motor/Servo tabs)
- Servo pan/tilt sliders + crosshair position indicator
- Speed slider (0–100%)
- LED presets (idle/moving/alert/off) + effects (rainbow/blink/pulse) + RGB picker
- Emergency stop button + reset
- Ultrasonic distance gauge (live, color-coded: green→yellow→red)
- System status badges (motor, servo pan/tilt, emergency, obstacle)
- Event log with timestamps
- FPS counter + uptime display
- Responsive — works on desktop, tablet, mobile

**To use:**
```bash
# 1. Start Pi
cd /home/pi/Final/Raspi && python3 main.py

# 2. Open Dashboard/index.html in any browser on local network
# 3. Enter Pi IP → click Connect
```

---

## 🚧 Phase 2 — AI Vision (10% — Next Priority)

The AI Vision module exists separately in `zLast_development/Mizo/IOT-Surveillance-Car-merged-ai-computer-vision/` with:
- BlazeFace (MediaPipe TFLite) — 15–20 FPS on Pi4
- dlib 128-dim face recognition
- PCA9685 I2C servo tracking (PID controlled)
- Multi-core processing (3 cores)
- Full Tkinter GUI with enrollment wizard

**Integration needed:**
- Create `Raspi/AI/vision_controller.py` using `hardware_manager.camera.get_ai_frame()`
- Connect detections → `hardware_manager.servo.set_angle(pan=..., tilt=...)`
- Add MQTT topics: `vision/faces`, `vision/objects`, `vision/tracking`
- Stream AI-annotated frames via WebSocket

**Note — Hardware conflict to resolve:**  
Mizo module uses PCA9685 I2C. Final project uses direct GPIO PWM.  
Choose one approach before integrating.

---

## 📊 Phase Completion

| Phase | Component | Status | % |
|---|---|---|---|
| 1 | Hardware (drivers, safety, motor, servo, LED, ultrasonic, camera) | ✅ Complete | 100% |
| 1 | MQTT (local + cloud) | ✅ Complete | 100% |
| 1 | WebSocket streaming (video + audio) | ✅ Complete | 100% |
| 1 | Desktop GUI (Tkinter) | ✅ Complete | 100% |
| 1 | Web Dashboard | ✅ Complete | 100% |
| 1 | Testing | ⚠️ Pending | 0% |
| 2 | AI Vision integration | 🔴 Not started | 10% |

**Overall: ~90%**

---

## 🏃 Quick Start

```bash
# On Raspberry Pi
cd /home/pi/Final/Raspi
pip3 install -r requirements.txt
python3 main.py

# On Laptop (Desktop GUI)
cd Final/Laptop
pip3 install -r requirements.txt
python3 mqtt_gui_controller.py

# Web Dashboard — just open in browser
open Final/Dashboard/index.html
# Enter Pi IP, click Connect
```

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| GPIO permission denied | `sudo usermod -a -G gpio $USER && sudo reboot` |
| Camera not found | `sudo raspi-config` → Interface → Camera → Enable |
| MQTT connection failed | `sudo systemctl status mosquitto` / `sudo ufw allow 1883` |
| WebSocket port blocked | `sudo ufw allow 8765/tcp` |
| Motors not moving | Check 12V external power + common ground |
| Laptop GUI wrong broker path | Edit `_CONFIG_PATH` in `mqtt_gui_controller.py` line 31 |

---

## 📁 Full Structure

```
Final/
├── Dashboard/               ✅ Web Dashboard
│   ├── index.html
│   ├── dashboard.css
│   ├── dashboard.js
│   └── README.md
├── Raspi/                   ✅ Raspberry Pi System
│   ├── main.py
│   ├── requirements.txt
│   ├── setup.sh
│   ├── Drivers/hardware/    (36 modules)
│   ├── Network/MQTT/        (5 files + config)
│   ├── Network/WebSockets/  (6 files)
│   ├── AI/                  🔴 Placeholder (to be integrated)
│   ├── config/hardware/     (4 YAML files)
│   ├── tests/               (7 test files)
│   └── Docs/                (5 architecture docs)
├── Laptop/                  ✅ Desktop GUI Controller
│   ├── mqtt_gui_controller.py
│   ├── connection_manager.py
│   ├── ui_components.py
│   ├── utils/
│   └── docs/
└── Docs/                    ✅ Project Documentation
    ├── COMPLETE_SUMMARY.md  ← This file
    ├── STRUCTURE.md
    ├── ToDo.md
    ├── TODO_CHECKLIST.md
    └── CONNECTIONS_GUIDE.md
```
