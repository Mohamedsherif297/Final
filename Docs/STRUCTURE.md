# Surveillance Car — Project Structure

```
Final/
│
├── Dashboard/                        ✅ Web Dashboard (Phase 1 — Complete)
│   ├── index.html                    ⭐ Open this in browser to control car
│   ├── dashboard.css                 Dark glassmorphism styles
│   ├── dashboard.js                  WebSocket engine + controls logic
│   └── README.md                     Dashboard usage guide
│
├── Raspi/                            ✅ Raspberry Pi System (Phase 1 — Complete)
│   ├── main.py                       ⭐ System entry point (Hardware + MQTT + WebSocket)
│   ├── requirements.txt              Python dependencies
│   ├── setup.sh                      One-time setup script
│   │
│   ├── Drivers/                      ✅ Hardware Abstraction Layer
│   │   └── hardware/
│   │       ├── gpio/                 GPIO & PWM singleton managers
│   │       ├── motor/                L298N motor control + safety
│   │       ├── servo/                Pan/tilt servo, calibration, limits
│   │       ├── led/                  RGB LED + 6 animation effects
│   │       ├── ultrasonic/           HC-SR04 sensor, median filter, obstacle detect
│   │       ├── camera/               OpenCV capture, dual buffer, 30 FPS
│   │       ├── safety/               Emergency stop, watchdog, health monitor
│   │       ├── managers/             Hardware Manager (Facade/Singleton)
│   │       └── utils/                Logging and shared utilities
│   │
│   ├── Network/                      ✅ Communication Layer
│   │   ├── MQTT/                     MQTT command/control + sensor publishing
│   │   │   ├── mqtt_device_controller_integrated.py  ⭐ Main controller
│   │   │   ├── connection_manager.py                 Local/cloud broker switching
│   │   │   ├── mqtt_topics.py                        Topic constants
│   │   │   └── config/                               MQTT config files
│   │   │
│   │   └── WebSockets/               Real-time video/audio streaming
│   │       ├── websocket_server.py   ⭐ Async multi-client server
│   │       ├── video_stream_handler.py  JPEG encode + broadcast @ 20 FPS
│   │       ├── audio_system.py       PCM capture + broadcast @ 16 kHz
│   │       ├── config.py             All tunable params (env var overrides)
│   │       └── README.md             WebSocket technical docs
│   │
│   ├── AI/                           🔴 To Be Integrated (Phase 2)
│   │   └── DEPLOYMENT_FILES.md       Placeholder — AI not yet wired in
│   │
│   ├── config/                       ✅ Configuration (YAML — no hardcoded values)
│   │   └── hardware/
│   │       ├── gpio_config.yaml      GPIO pin assignments
│   │       ├── pwm_config.yaml       PWM frequencies
│   │       ├── servo_config.yaml     Angle limits and presets
│   │       └── safety_config.yaml    Obstacle threshold, watchdog timeout
│   │
│   ├── tests/                        ✅ Test Suite
│   │   ├── test_hardware.py          Full hardware component test
│   │   ├── test_hardware_fixed.py    Fixed variant
│   │   ├── test_hardware_pan_only.py Servo-only test
│   │   ├── test_mqtt_system.py       MQTT integration tests
│   │   ├── test_integration.py       End-to-end integration
│   │   ├── mqtt_client_tester.py     CLI MQTT tester
│   │   └── HARDWARE_TEST_GUIDE.md    Physical test instructions
│   │
│   └── Docs/                         ✅ Raspi-level Documentation
│       ├── README.md                 Full Raspi system guide
│       ├── QUICK_START.md            Getting started
│       ├── ARCHITECTURE.md           Layered architecture + design patterns
│       ├── SYSTEM_DIAGRAM.md         ASCII system diagrams
│       └── DEPLOYMENT_CHECKLIST.md   Pre-deployment checklist
│
├── Laptop/                           ✅ Desktop GUI Controller
│   ├── mqtt_gui_controller.py        ⭐ Tkinter GUI (dark themed)
│   ├── connection_manager.py         Local/cloud MQTT switching
│   ├── ui_components.py              UI widget helpers
│   ├── requirements.txt              Laptop dependencies
│   ├── README.md                     Laptop setup guide
│   ├── utils/
│   │   ├── batch_commands.py         Automated command sequences
│   │   ├── connection_test.py        Connection testing
│   │   ├── message_validator.py      JSON message validation
│   │   └── network_scanner.py        LAN network scanner
│   └── docs/
│       ├── client_setup_guide.md
│       ├── mqtt_api_reference.md
│       └── troubleshooting_mqtt.md
│
└── Docs/                             ✅ Project-level Documentation
    ├── COMPLETE_SUMMARY.md           Full project summary (this version)
    ├── STRUCTURE.md                  This file
    ├── ToDo.md                       Active task tracker
    ├── TODO_CHECKLIST.md             Detailed feature checklist
    └── CONNECTIONS_GUIDE.md          Hardware wiring guide
```

---

## 📊 Component Status

| Component | Files | Status | % |
|---|---|---|---|
| `Dashboard/` | 4 | ✅ Complete | 100% |
| `Raspi/Drivers/hardware/` | 36 | ✅ Complete | 100% |
| `Raspi/Network/MQTT/` | 5 + config | ✅ Complete | 100% |
| `Raspi/Network/WebSockets/` | 6 | ✅ Complete | 100% |
| `Raspi/config/hardware/` | 4 YAML | ✅ Complete | 100% |
| `Raspi/tests/` | 7 | ✅ Complete | 100% |
| `Raspi/AI/` | Placeholder | 🔴 Phase 2 | 10% |
| `Laptop/` | 8 + utils | ✅ Complete | 100% |

**Overall: ~90%**

---

## 🔌 Network Ports Used

| Port | Protocol | Purpose |
|---|---|---|
| 1883 | MQTT TCP | Local Mosquitto broker |
| 8883 | MQTT TLS | HiveMQ cloud broker |
| 8765 | WebSocket | Video/Audio/Commands |
