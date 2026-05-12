# Complete Connections Guide - Surveillance Car

Comprehensive guide covering all hardware, network, and software connections.

---

## 📑 Table of Contents

1. [Hardware Connections](#hardware-connections)
2. [Network Connections](#network-connections)
3. [Software Connections](#software-connections)
4. [MQTT Topics & Messages](#mqtt-topics--messages)
5. [Data Flow](#data-flow)
6. [Troubleshooting](#troubleshooting)

---

## 🔌 Hardware Connections

### Power Connections

#### Raspberry Pi Power
- **Input**: 5V 3A USB-C power supply or power bank
- **Important**: Do NOT power motors from Raspberry Pi!

#### Motor Driver (L298N) Power
- **12V Input**: External 12V power supply (2A minimum)
- **5V Output**: Can power servos (if < 500mA total)
- **Ground**: **CRITICAL** - Connect common ground between Pi and L298N

```
Power Supply (12V) ──→ L298N VCC
                       L298N GND ──→ Common Ground ←── Raspberry Pi GND
```

### GPIO Connections (BCM Mode)

#### Motor Connections (L298N Driver)

**Left Motor**:
```
Raspberry Pi          L298N Motor Driver
GPIO 12 (PWM)    ──→  ENA (Enable A)
GPIO 23          ──→  IN1 (Input 1)
GPIO 24          ──→  IN2 (Input 2)
                      OUT1 ──→ Left Motor +
                      OUT2 ──→ Left Motor -
```

**Right Motor**:
```
Raspberry Pi          L298N Motor Driver
GPIO 13 (PWM)    ──→  ENB (Enable B)
GPIO 27          ──→  IN3 (Input 3)
GPIO 22          ──→  IN4 (Input 4)
                      OUT3 ──→ Right Motor +
                      OUT4 ──→ Right Motor -
```

**Pin Summary**:
| Component | BCM Pin | Function |
|-----------|---------|----------|
| Left Motor Enable | 12 | PWM speed control |
| Left Motor IN1 | 23 | Direction control |
| Left Motor IN2 | 24 | Direction control |
| Right Motor Enable | 13 | PWM speed control |
| Right Motor IN3 | 27 | Direction control |
| Right Motor IN4 | 22 | Direction control |

#### Servo Connections

**Pan Servo (Horizontal)**:
```
Raspberry Pi          Servo
GPIO 17 (PWM)    ──→  Signal (Yellow/White)
5V               ──→  VCC (Red)
GND              ──→  GND (Brown/Black)
```

**Tilt Servo (Vertical)**:
```
Raspberry Pi          Servo
GPIO 18 (PWM)    ──→  Signal (Yellow/White)
5V               ──→  VCC (Red)
GND              ──→  GND (Brown/Black)
```

**Pin Summary**:
| Servo | BCM Pin | Angle Range |
|-------|---------|-------------|
| Pan | 17 | -90° to +90° |
| Tilt | 18 | -90° to +90° |

**Note**: If servos draw > 500mA total, use external 5V power supply.

#### LED Connections (RGB Common Cathode)

```
Raspberry Pi          RGB LED
GPIO 16          ──→  Red Anode (via 220Ω resistor)
GPIO 20          ──→  Green Anode (via 220Ω resistor)
GPIO 21          ──→  Blue Anode (via 220Ω resistor)
GND              ──→  Common Cathode
```

**Pin Summary**:
| Color | BCM Pin | Resistor |
|-------|---------|----------|
| Red | 16 | 220Ω |
| Green | 20 | 220Ω |
| Blue | 21 | 220Ω |

#### Ultrasonic Sensor (HC-SR04)

```
Raspberry Pi          HC-SR04
GPIO 5           ──→  Trigger
GPIO 6           ──→  Echo
5V               ──→  VCC
GND              ──→  GND
```

**Pin Summary**:
| Function | BCM Pin |
|----------|---------|
| Trigger | 5 |
| Echo | 6 |

**Range**: 2cm - 400cm  
**Update Rate**: 10 Hz (configurable)

#### Camera Connection

**CSI Camera**:
```
Raspberry Pi CSI Port ──→ Camera Ribbon Cable
```

**USB Camera**:
```
USB Port ──→ USB Camera
```

**Settings**:
- Resolution: 640x480 (configurable)
- FPS: 30 (configurable)
- Dual buffers: Main + AI

### Complete Wiring Diagram

```
                    ┌─────────────────────────────────┐
                    │     Raspberry Pi 4/3            │
                    │                                 │
                    │  GPIO 12 ──→ L298N ENA         │
                    │  GPIO 23 ──→ L298N IN1         │
                    │  GPIO 24 ──→ L298N IN2         │
                    │  GPIO 13 ──→ L298N ENB         │
                    │  GPIO 27 ──→ L298N IN3         │
                    │  GPIO 22 ──→ L298N IN4         │
                    │                                 │
                    │  GPIO 17 ──→ Pan Servo         │
                    │  GPIO 18 ──→ Tilt Servo        │
                    │                                 │
                    │  GPIO 16 ──→ LED Red (220Ω)    │
                    │  GPIO 20 ──→ LED Green (220Ω)  │
                    │  GPIO 21 ──→ LED Blue (220Ω)   │
                    │                                 │
                    │  GPIO 5  ──→ Ultrasonic Trig   │
                    │  GPIO 6  ──→ Ultrasonic Echo   │
                    │                                 │
                    │  GND ──→ Common Ground ←── All │
                    └─────────────────────────────────┘
                              │
                              │ WiFi/Ethernet
                              ↓
                         MQTT Broker
                              ↓
                         Laptop GUI
```

---

## 🌐 Network Connections

### MQTT Broker Connections

#### Local Network Mode

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│ Raspberry Pi │ ←─────→ │   Mosquitto  │ ←─────→ │    Laptop    │
│  (Device)    │  WiFi   │    Broker    │  WiFi   │     GUI      │
│              │         │  (localhost) │         │              │
└──────────────┘         └──────────────┘         └──────────────┘
     Port: 1883               Port: 1883               Port: 1883
```

**Configuration**:
- **Broker**: localhost (on Raspberry Pi)
- **Port**: 1883 (standard MQTT)
- **Protocol**: MQTT v3.1.1
- **QoS**: 1 (at least once delivery)
- **Clean Session**: True

**Setup**:
```bash
# On Raspberry Pi
sudo apt-get install mosquitto mosquitto-clients
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
```

**Connection String**:
```python
BROKER_HOST = "localhost"  # or Pi's IP: "192.168.1.100"
BROKER_PORT = 1883
```

#### Cloud Network Mode (HiveMQ)

```
┌──────────────┐                                    ┌──────────────┐
│ Raspberry Pi │ ←────────────────────────────────→ │    Laptop    │
│  (Device)    │         Internet (TLS)             │     GUI      │
│              │              ↕                      │              │
└──────────────┘      ┌──────────────┐              └──────────────┘
                      │   HiveMQ     │
                      │    Cloud     │
                      └──────────────┘
```

**Configuration**:
- **Broker**: 78ed3eab06c348d0948ef7681cf4a377.s1.eu.hivemq.cloud
- **Port**: 8883 (MQTT over TLS)
- **Protocol**: MQTT v3.1.1 with TLS
- **Username**: mohamed
- **Password**: P@ssw0rd
- **QoS**: 1
- **Clean Session**: True

**Connection String**:
```python
BROKER_HOST = "78ed3eab06c348d0948ef7681cf4a377.s1.eu.hivemq.cloud"
BROKER_PORT = 8883
USERNAME = "mohamed"
PASSWORD = "P@ssw0rd"
# TLS enabled automatically for port 8883
```

### Network Topology

```
                    Internet
                        │
                        │ (Cloud Mode)
                        ↓
                  ┌──────────┐
                  │  HiveMQ  │
                  │  Cloud   │
                  └──────────┘
                        ↕
        ┌───────────────┼───────────────┐
        │               │               │
        ↓               ↓               ↓
┌──────────────┐  ┌──────────┐  ┌──────────┐
│ Raspberry Pi │  │  Laptop  │  │  Mobile  │
│   (Device)   │  │   GUI    │  │   App    │
└──────────────┘  └──────────┘  └──────────┘
        ↕               ↕
        └───────────────┘
         Local Network
        (Local Mode)
```

### WiFi Configuration

**Raspberry Pi WiFi**:
```bash
# Edit wpa_supplicant
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf

# Add network
network={
    ssid="YourNetworkName"
    psk="YourPassword"
}
```

**Static IP (Optional)**:
```bash
# Edit dhcpcd.conf
sudo nano /etc/dhcpcd.conf

# Add static IP
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8
```

---

## 💻 Software Connections

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACES                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Laptop GUI   │  │ MQTT Client  │  │  Web Browser │      │
│  │  (Tkinter)   │  │ (mosquitto)  │  │  (Future)    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │  MQTT Broker    │
                    │  (Mosquitto/    │
                    │   HiveMQ)       │
                    └────────┬────────┘
                             │
┌────────────────────────────┼────────────────────────────────┐
│              RASPBERRY PI SYSTEM                             │
│                    ┌────────▼────────┐                       │
│                    │ MQTT Controller │                       │
│                    │  (Integrated)   │                       │
│                    └────────┬────────┘                       │
│                             │                                │
│                    ┌────────▼────────┐                       │
│                    │ Hardware Manager│                       │
│                    └────────┬────────┘                       │
│                             │                                │
│        ┌────────────────────┼────────────────────┐          │
│        │                    │                    │          │
│   ┌────▼────┐         ┌────▼────┐         ┌────▼────┐     │
│   │  Motor  │         │  Servo  │         │   LED   │     │
│   │Controller│        │Controller│        │Controller│     │
│   └────┬────┘         └────┬────┘         └────┬────┘     │
│        │                    │                    │          │
│   ┌────▼────┐         ┌────▼────┐         ┌────▼────┐     │
│   │Ultrasonic│        │ Camera  │         │ Safety  │     │
│   │Controller│        │Controller│        │ Systems │     │
│   └────┬────┘         └────┬────┘         └────┬────┘     │
│        │                    │                    │          │
│        └────────────────────┼────────────────────┘          │
│                             │                                │
│                    ┌────────▼────────┐                       │
│                    │  GPIO/PWM       │                       │
│                    │  Managers       │                       │
│                    └────────┬────────┘                       │
└─────────────────────────────┼──────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │ Physical Hardware │
                    └───────────────────┘
```

### Component Connections

#### Hardware Manager → Controllers

```python
# Hardware Manager initializes and coordinates all controllers
hardware_manager.initialize()
    ├── motor_controller.initialize()
    ├── servo_controller.initialize()
    ├── led_controller.initialize()
    ├── ultrasonic_controller.initialize()
    ├── camera_controller.initialize()
    └── safety_systems.initialize()
```

#### MQTT Controller → Hardware Manager

```python
# MQTT receives command
mqtt_controller.on_message(topic, payload)
    ↓
# Routes to handler
handle_motor_command(data)
    ↓
# Calls hardware manager
hardware_manager.motor.move_forward(speed)
    ↓
# Hardware manager delegates
motor_controller.move_forward(speed)
    ↓
# Controller uses GPIO
gpio_manager.set_pin(pin, state)
```

### Thread Connections

```
Main Thread
    ├── System initialization
    ├── Signal handling
    └── Graceful shutdown
         │
         ├─→ MQTT Loop Thread
         │       ├── Message receiving
         │       ├── Callback execution
         │       └── Keep-alive
         │
         ├─→ Camera Capture Thread
         │       ├── Frame capture (30 FPS)
         │       └── Buffer management
         │
         ├─→ Ultrasonic Monitor Thread
         │       ├── Distance measurement (10 Hz)
         │       └── Obstacle detection
         │
         ├─→ Watchdog Thread
         │       ├── Heartbeat monitoring (1 Hz)
         │       └── Timeout detection
         │
         ├─→ Sensor Publishing Thread
         │       ├── Data collection
         │       └── MQTT publishing (10 Hz)
         │
         └─→ LED Effect Thread (when active)
                 └── Animation execution
```

**Thread Safety**:
- All hardware access protected by `threading.RLock`
- Camera frames use `queue.Queue` (thread-safe)
- Emergency stop uses atomic operations

---

## 📡 MQTT Topics & Messages

### Topic Structure

```
dev/
├── motor          (Motor commands)
├── led            (LED commands)
├── servo          (Servo commands)
├── commands       (General commands)
└── status         (Status updates)

sensors/
├── ultrasonic     (Distance data)
└── obstacle       (Obstacle alerts)

emergency/
└── alert          (Emergency events)

vision/           (Future - AI)
├── faces
├── objects
└── tracking
```

### Command Topics (Subscribe)

#### dev/motor
**Direction**: Raspberry Pi subscribes, Laptop publishes

**Message Format**:
```json
{
  "direction": "forward|backward|left|right|stop",
  "speed": 0-100
}
```

**Examples**:
```json
{"direction": "forward", "speed": 80}
{"direction": "left", "speed": 60}
{"direction": "stop", "speed": 0}
```

#### dev/led
**Direction**: Raspberry Pi subscribes, Laptop publishes

**Message Format**:
```json
{
  "action": "set_rgb|set_color|start_effect|stop_effect|off",
  "red": 0-255,
  "green": 0-255,
  "blue": 0-255,
  "color": "idle|moving|emergency|...",
  "effect": "blink|fade|rainbow|police|pulse|..."
}
```

**Examples**:
```json
{"action": "set_rgb", "red": 255, "green": 0, "blue": 0}
{"action": "set_color", "color": "moving"}
{"action": "start_effect", "effect": "rainbow"}
{"action": "off"}
```

#### dev/servo
**Direction**: Raspberry Pi subscribes, Laptop publishes

**Message Format**:
```json
{
  "action": "set_angle|center|preset|scan",
  "pan": -90 to 90,
  "tilt": -90 to 90,
  "preset": "center|left|right|up|down"
}
```

**Examples**:
```json
{"action": "set_angle", "pan": 45, "tilt": 20}
{"action": "center"}
{"action": "preset", "preset": "left"}
{"action": "scan"}
```

#### dev/commands
**Direction**: Raspberry Pi subscribes, Laptop publishes

**Message Format**:
```json
{
  "command": "status|stop_all|emergency_stop|reset_emergency|get_hardware_status"
}
```

**Examples**:
```json
{"command": "status"}
{"command": "emergency_stop"}
{"command": "reset_emergency"}
```

### Status Topics (Publish)

#### dev/status
**Direction**: Raspberry Pi publishes, Laptop subscribes

**Message Format**:
```json
{
  "type": "motor_moved|led_controlled|servo_moved|error|...",
  "message": "string or object",
  "timestamp": 1234567890.123
}
```

**Examples**:
```json
{
  "type": "motor_moved",
  "message": {"direction": "forward", "speed": 80},
  "timestamp": 1234567890.123
}
```

#### sensors/ultrasonic
**Direction**: Raspberry Pi publishes, Laptop subscribes

**Message Format**:
```json
{
  "distance": 0.0-400.0,
  "timestamp": 1234567890.123
}
```

**Update Rate**: 10 Hz

#### sensors/obstacle
**Direction**: Raspberry Pi publishes, Laptop subscribes

**Message Format**:
```json
{
  "distance": 0.0-20.0,
  "timestamp": 1234567890.123
}
```

**Triggered**: When distance < threshold (default 20cm)

#### emergency/alert
**Direction**: Raspberry Pi publishes, Laptop subscribes

**Message Format**:
```json
{
  "trigger": "OBSTACLE_DETECTED|WATCHDOG_TIMEOUT|MANUAL_BUTTON|...",
  "message": "description",
  "timestamp": 1234567890.123
}
```

---

## 🔄 Data Flow

### Command Flow (Laptop → Raspberry Pi)

```
1. User Action (Laptop GUI)
   ↓
2. GUI generates command
   {"direction": "forward", "speed": 80}
   ↓
3. Publish to MQTT
   Topic: dev/motor
   ↓
4. MQTT Broker
   (Mosquitto or HiveMQ)
   ↓
5. Raspberry Pi MQTT Controller
   on_message() receives
   ↓
6. Route to handler
   handle_motor_command(data)
   ↓
7. Call Hardware Manager
   hardware_manager.motor.move_forward(80)
   ↓
8. Motor Controller
   - Validate speed
   - Check emergency stop
   - Smooth acceleration
   ↓
9. GPIO Manager
   - Set direction pins
   - Set PWM speed
   ↓
10. Physical Motors
    Motors spin forward at 80% speed
    ↓
11. Confirmation
    Publish to dev/status
    {"type": "motor_moved", ...}
    ↓
12. Laptop GUI
    Display status update
```

### Sensor Flow (Raspberry Pi → Laptop)

```
1. Ultrasonic Sensor
   Trigger pulse, measure echo
   ↓
2. Ultrasonic Controller
   - Read distance
   - Apply filtering (moving average)
   - Check threshold
   ↓
3. Distance Filter
   - Median filter
   - Noise rejection
   ↓
4. Sensor Publishing Thread
   Every 100ms (10 Hz)
   ↓
5. Publish to MQTT
   Topic: sensors/ultrasonic
   {"distance": 35.2, "timestamp": ...}
   ↓
6. MQTT Broker
   ↓
7. Laptop GUI
   - Receive message
   - Update display
   - Show distance value
```

### Emergency Flow

```
1. Trigger Source
   - Obstacle detected (< 20cm)
   - Watchdog timeout (> 10s)
   - Manual button
   - Hardware error
   ↓
2. Emergency Stop System
   emergency_stop.trigger_emergency(trigger, message)
   ↓
3. Execute Callbacks
   ├→ hardware_manager._emergency_handler()
   │   ├→ motor.emergency_stop()
   │   │   └→ Motors stop immediately
   │   └→ led.set_status_color('emergency')
   │       └→ LED turns red
   └→ mqtt_controller._on_emergency()
       └→ Publish to emergency/alert
   ↓
4. Block New Commands
   All controllers check emergency_active
   ↓
5. MQTT Alert
   Topic: emergency/alert
   {"trigger": "OBSTACLE_DETECTED", ...}
   ↓
6. Laptop GUI
   - Display emergency alert
   - Show red indicator
   - Log event
```

---

## 🔧 Troubleshooting

### Hardware Connection Issues

**Motors not moving**:
```
Check:
1. External 12V power connected to L298N
2. Common ground between Pi and L298N
3. GPIO pins match config (BCM mode)
4. Motor driver enabled (ENA/ENB high)
5. No emergency stop active

Test:
python3 -c "from Drivers import hardware_manager; hardware_manager.initialize(); hardware_manager.motor.move_forward(50)"
```

**Servos not responding**:
```
Check:
1. 5V power connected
2. Signal wire on correct GPIO (17, 18)
3. Servo angle within limits (-90 to 90)
4. PWM frequency correct (50 Hz)

Test:
python3 -c "from Drivers import hardware_manager; hardware_manager.initialize(); hardware_manager.servo.center()"
```

**LED not lighting**:
```
Check:
1. 220Ω resistors in place
2. Common cathode to GND
3. GPIO pins correct (16, 20, 21)
4. LED polarity correct

Test:
python3 -c "from Drivers import hardware_manager; hardware_manager.initialize(); hardware_manager.led.set_color(255, 0, 0)"
```

**Ultrasonic sensor not reading**:
```
Check:
1. 5V power connected
2. Trigger on GPIO 5, Echo on GPIO 6
3. Sensor facing forward
4. No obstacles blocking sensor

Test:
python3 -c "from Drivers import hardware_manager; hardware_manager.initialize(); print(hardware_manager.ultrasonic.get_distance())"
```

### Network Connection Issues

**Cannot connect to local broker**:
```bash
# Check Mosquitto running
sudo systemctl status mosquitto

# Restart broker
sudo systemctl restart mosquitto

# Check firewall
sudo ufw allow 1883

# Test connection
mosquitto_sub -h localhost -t test -v
```

**Cannot connect to HiveMQ cloud**:
```bash
# Test connection
mosquitto_pub -h 78ed3eab06c348d0948ef7681cf4a377.s1.eu.hivemq.cloud \
  -p 8883 \
  -u mohamed \
  -P 'P@ssw0rd' \
  --capath /etc/ssl/certs/ \
  -t test \
  -m "hello"

# Check internet connection
ping 8.8.8.8

# Verify credentials in config
cat Final/Raspi/Network/MQTT/config/client_config.json
```

**Laptop GUI won't connect**:
```
Check:
1. Raspberry Pi running main.py
2. Broker mode selected (Local/Cloud)
3. Correct broker IP/hostname
4. Firewall not blocking port

Test:
cd Final/Laptop
python utils/connection_test.py
```

### Software Connection Issues

**GPIO permission denied**:
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Reboot
sudo reboot
```

**Camera not found**:
```bash
# Check camera
vcgencmd get_camera

# Enable camera
sudo raspi-config
# Interface Options → Camera → Enable

# Reboot
sudo reboot
```

**Import errors**:
```bash
# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Reinstall dependencies
pip3 install -r requirements.txt
```

---

## 📞 Quick Reference

### Connection Checklist

**Hardware**:
- [ ] 12V power to L298N
- [ ] Common ground connected
- [ ] All GPIO pins connected correctly
- [ ] Servos powered (5V)
- [ ] LED resistors in place (220Ω)
- [ ] Camera connected

**Network**:
- [ ] WiFi configured
- [ ] MQTT broker running
- [ ] Firewall ports open (1883/8883)
- [ ] Broker credentials correct

**Software**:
- [ ] Dependencies installed
- [ ] GPIO permissions set
- [ ] Camera enabled
- [ ] Config files present

### Test Commands

```bash
# Test hardware
cd Final/Raspi
python3 -c "from Drivers import hardware_manager; hardware_manager.initialize(); print('OK')"

# Test MQTT local
mosquitto_pub -h localhost -t test -m "hello"
mosquitto_sub -h localhost -t test -v

# Test MQTT cloud
mosquitto_pub -h 78ed3eab06c348d0948ef7681cf4a377.s1.eu.hivemq.cloud -p 8883 -u mohamed -P 'P@ssw0rd' --capath /etc/ssl/certs/ -t test -m "hello"

# Test motor
mosquitto_pub -h localhost -t dev/motor -m '{"direction": "forward", "speed": 50}'

# Monitor all topics
mosquitto_sub -h localhost -t '#' -v
```

---

**Document Version**: 1.0  
**Last Updated**: System Integration Complete  
**Status**: Production Ready
