# Surveillance Car — Test Suite

All tests run directly on the Raspberry Pi terminal.

## Install

```bash
cd /home/pi/Final/Raspi
pip3 install pytest pytest-timeout paho-mqtt websockets opencv-python
```

---

## Test Layers

| Layer | Folder | Needs |
|---|---|---|
| Unit / Hardware | `tests/unit/` | Components wired, NO main.py |
| MQTT Network | `tests/network/test_mqtt.py` | `mosquitto` running, main.py running |
| WebSocket | `tests/network/test_websocket.py` | `main.py` running |
| Combined | `tests/combined/` | `main.py` running + hardware |

---

## Running Tests

### Run everything
```bash
cd /home/pi/Final/Raspi
pytest tests/ -v
```

### Run by layer
```bash
# Unit tests only (GPIO, motor, servo, LED, ultrasonic, camera)
pytest tests/unit/ -v

# Network tests only
pytest tests/network/ -v

# Combined tests only
pytest tests/combined/ -v
```

### Run by marker
```bash
# Only hardware tests (motors actually move)
pytest tests/ -v -m hardware

# Skip slow effects tests
pytest tests/unit/ -v -m "not slow"

# Only MQTT-related
pytest tests/ -v -m mqtt

# Skip hardware (safe for software-only checks)
pytest tests/ -v -m "not hardware and not camera"
```

### Run a single test file
```bash
pytest tests/unit/test_motor.py -v
pytest tests/unit/test_servo.py -v
pytest tests/network/test_mqtt.py -v
pytest tests/network/test_websocket.py -v
```

---

## WAN (HiveMQ) Test Setup

Export credentials before running:
```bash
export HIVEMQ_HOST="your-broker.s1.eu.hivemq.cloud"
export HIVEMQ_PORT=8883
export HIVEMQ_USER="your-username"
export HIVEMQ_PASS="your-password"

pytest tests/network/test_mqtt.py -v -k "wan"
```

## Custom Pi IP (for WebSocket/combined tests)

```bash
export PI_IP=192.168.1.100
pytest tests/network/test_websocket.py -v
```

---

## Test Suite Overview

### `tests/unit/test_gpio.py`
- GPIO manager initialization
- Pin registration (output/input)
- Correct error on wrong mode
- All motor + servo pins configurable

### `tests/unit/test_motor.py`
- Motor init and initial state
- Forward / backward / left / right (hardware)
- Speed clamping (0–100)
- Emergency stop + recovery cycle

### `tests/unit/test_servo.py`
- Servo init and center position
- Full angle range: -90° → +90° (hardware)
- Limit clamping (beyond min/max)
- Pan/tilt nudge operations

### `tests/unit/test_led_ultrasonic_camera.py`
- LED colors: red, green, blue, white, off (hardware)
- LED status presets: idle, moving, emergency (hardware)
- LED effects: blink, rainbow, pulse (slow, hardware)
- Ultrasonic single reading + filtered reading (hardware)
- Ultrasonic 5-reading monitoring loop (hardware)
- Camera frame capture + JPEG save

### `tests/network/test_mqtt.py`
- Local broker reachable
- Pub/sub round-trip on test/ping
- All 4 command topics: dev/motor, dev/led, dev/servo, dev/commands
- sensors/ultrasonic topic
- Reconnect after disconnect
- HiveMQ WAN connection (TLS)
- HiveMQ WAN pub/sub round-trip
- HiveMQ WAN motor command

### `tests/network/test_websocket.py`
- Server reachable + welcome JSON
- Multiple simultaneous clients
- Video frames received (5+)
- Video frame JPEG validation (magic bytes)
- FPS measurement (≥5 FPS)
- Video resolution check (640×480)
- Audio chunks received (3+)
- Audio chunk size validation
- Motor command via WS bridge
- LED command via WS bridge
- Emergency stop via WS bridge
- MQTT relay messages received

### `tests/combined/test_full_pipeline.py`
- MQTT motor command → dev/status ack
- MQTT LED command → hardware (LED changes color)
- MQTT servo center → hardware
- MQTT emergency stop → emergency/alert
- Ultrasonic sensor data published by Pi
- WS motor command → bridges to MQTT → hardware
- Simultaneous video + control commands (no interference)
- MQTT + WebSocket both accessible at same time
- Pi publishes status on startup

---

## What to Look For Physically

| Test | What You See |
|---|---|
| `test_move_forward` | Both motors spin forward |
| `test_move_backward` | Both motors spin backward |
| `test_turn_left` | Right motor faster than left |
| `test_turn_right` | Left motor faster than right |
| `test_pan_full_left` | Camera pans left |
| `test_pan_full_right` | Camera pans right |
| `test_set_red` | LED glows red |
| `test_set_green` | LED glows green |
| `test_blink_effect` | LED blinks |
| `test_rainbow_effect` | LED cycles colors |
| `test_single_measurement` | Distance printed in terminal |
| `test_get_frame` | `test_frame.jpg` saved — open to verify |
