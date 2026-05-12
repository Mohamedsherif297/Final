# Surveillance Car - Raspberry Pi System

Complete integrated system for IoT surveillance car with professional hardware control, MQTT communication, and AI vision capabilities.

## 🏗️ Architecture

```
Final/Raspi/
├── main.py                    # Main entry point - system orchestrator
├── Drivers/                   # Hardware abstraction layer
│   └── hardware/
│       ├── gpio/              # GPIO and PWM management
│       ├── motor/             # Motor control with safety
│       ├── servo/             # Servo control (pan/tilt)
│       ├── led/               # LED control with effects
│       ├── ultrasonic/        # Distance sensor
│       ├── camera/            # Camera capture
│       ├── safety/            # Emergency stop & watchdog
│       ├── managers/          # Hardware manager (coordinator)
│       └── utils/             # Utilities
├── Network/                   # Communication layer
│   └── MQTT/
│       ├── mqtt_device_controller_integrated.py  # Main MQTT controller
│       ├── connection_manager.py                 # Connection management
│       └── mqtt_topics.py                        # Topic definitions
├── AI/                        # AI vision (to be integrated)
├── config/                    # Configuration files
│   └── hardware/              # Hardware configs (YAML)
└── tests/                     # Test suites
```

## 🚀 Quick Start

### 1. Installation

```bash
cd Final/Raspi

# Install dependencies
pip3 install -r requirements.txt

# Make main.py executable
chmod +x main.py
```

### 2. Hardware Setup

Connect your hardware according to the GPIO configuration in `config/hardware/gpio_config.yaml`:

**Default Pin Configuration (BCM Mode):**
- **Motors**: EN1=12, IN1=23, IN2=24, EN2=13, IN3=27, IN4=22
- **Servos**: Pan=17, Tilt=18
- **RGB LED**: R=16, G=20, B=21
- **Ultrasonic**: Trig=5, Echo=6

⚠️ **Important**: Use external power for motors and servos!

### 3. MQTT Broker Setup

**Local Broker:**
```bash
# Install Mosquitto
sudo apt-get install mosquitto mosquitto-clients

# Start broker
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
```

**Cloud Broker:**
Edit `Network/MQTT/config/client_config.json` with your HiveMQ credentials.

### 4. Run the System

```bash
# Run with default settings (localhost MQTT)
python3 main.py

# Or run MQTT controller directly
python3 Network/MQTT/mqtt_device_controller_integrated.py
```

## 📡 MQTT Topics

### Command Topics (Subscribe)

| Topic | Description | Example Payload |
|-------|-------------|-----------------|
| `dev/motor` | Motor control | `{"direction": "forward", "speed": 80}` |
| `dev/led` | LED control | `{"action": "set_rgb", "red": 255, "green": 0, "blue": 0}` |
| `dev/servo` | Servo control | `{"action": "set_angle", "pan": 45, "tilt": 20}` |
| `dev/commands` | General commands | `{"command": "status"}` |

### Status Topics (Publish)

| Topic | Description |
|-------|-------------|
| `dev/status` | Device status updates |
| `sensors/ultrasonic` | Distance measurements |
| `sensors/obstacle` | Obstacle detection alerts |
| `emergency/alert` | Emergency stop alerts |

## 🎮 Control Examples

### Motor Control

```bash
# Move forward at 80% speed
mosquitto_pub -h localhost -t dev/motor -m '{"direction": "forward", "speed": 80}'

# Turn left
mosquitto_pub -h localhost -t dev/motor -m '{"direction": "left", "speed": 60}'

# Stop
mosquitto_pub -h localhost -t dev/motor -m '{"direction": "stop"}'
```

### LED Control

```bash
# Set RGB color (red)
mosquitto_pub -h localhost -t dev/led -m '{"action": "set_rgb", "red": 255, "green": 0, "blue": 0}'

# Set status color
mosquitto_pub -h localhost -t dev/led -m '{"action": "set_color", "color": "moving"}'

# Start rainbow effect
mosquitto_pub -h localhost -t dev/led -m '{"action": "start_effect", "effect": "rainbow"}'
```

### Servo Control

```bash
# Set pan/tilt angles
mosquitto_pub -h localhost -t dev/servo -m '{"action": "set_angle", "pan": 45, "tilt": 20}'

# Center servos
mosquitto_pub -h localhost -t dev/servo -m '{"action": "center"}'

# Scan horizontally
mosquitto_pub -h localhost -t dev/servo -m '{"action": "scan"}'
```

### System Commands

```bash
# Get system status
mosquitto_pub -h localhost -t dev/commands -m '{"command": "status"}'

# Emergency stop
mosquitto_pub -h localhost -t dev/commands -m '{"command": "emergency_stop"}'

# Reset emergency
mosquitto_pub -h localhost -t dev/commands -m '{"command": "reset_emergency"}'

# Stop all devices
mosquitto_pub -h localhost -t dev/commands -m '{"command": "stop_all"}'
```

## 🔒 Safety Features

### Emergency Stop System
- **Multiple Triggers**: Obstacle detection, manual button, timeout, hardware error
- **Immediate Response**: Stops all motors instantly
- **LED Indication**: Red LED flashes on emergency
- **MQTT Alert**: Publishes emergency event to `emergency/alert`

### Watchdog Monitoring
- **Component Health**: Monitors all hardware components
- **Heartbeat System**: Requires periodic heartbeats (10s timeout)
- **Auto-Recovery**: Triggers emergency stop on component failure

### Obstacle Detection
- **Ultrasonic Sensor**: Continuous distance monitoring
- **Configurable Threshold**: Default 20cm (configurable in `safety_config.yaml`)
- **Auto-Stop**: Triggers emergency stop when obstacle detected

## ⚙️ Configuration

### Hardware Configuration

Edit `config/hardware/*.yaml` files:

**gpio_config.yaml** - GPIO pin mappings
```yaml
motor:
  left_motor:
    enable: 12
    input1: 23
    input2: 24
```

**pwm_config.yaml** - PWM frequencies
```yaml
motor:
  frequency: 1000  # Hz
```

**servo_config.yaml** - Servo limits and presets
```yaml
pan:
  min_angle: -90
  max_angle: 90
```

**safety_config.yaml** - Safety thresholds
```yaml
obstacle_detection:
  threshold: 20  # cm
```

### MQTT Configuration

Edit `Network/MQTT/config/client_config.json`:
```json
{
  "local_broker": {
    "host": "localhost",
    "port": 1883
  },
  "cloud_broker": {
    "host": "your-cluster.hivemq.cloud",
    "port": 8883
  },
  "credentials": {
    "username": "your-username",
    "password": "your-password"
  }
}
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific component tests
pytest tests/test_mqtt_system.py

# Run with coverage
pytest --cov=Drivers --cov=Network --cov-report=html
```

## 🔧 Troubleshooting

### Permission Denied on GPIO
```bash
sudo usermod -a -G gpio $USER
sudo reboot
```

### Camera Not Found
```bash
# Enable camera
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot
```

### MQTT Connection Failed
```bash
# Check broker status
sudo systemctl status mosquitto

# Check firewall
sudo ufw allow 1883

# Test connection
mosquitto_sub -h localhost -t test
```

### Motors Not Working
- Check external power supply (12V)
- Verify common ground connection
- Check GPIO pin numbers in config
- Test with: `python3 -c "from Drivers import hardware_manager; hardware_manager.initialize()"`

## 📊 System Status

Monitor system status:

```bash
# Subscribe to status updates
mosquitto_sub -h localhost -t dev/status -v

# Subscribe to sensor data
mosquitto_sub -h localhost -t sensors/# -v

# Subscribe to emergency alerts
mosquitto_sub -h localhost -t emergency/# -v
```

## 🔌 Integration Points

### For AI Vision Integration

```python
from Drivers.hardware.managers.hardware_manager import hardware_manager

# Get camera frame for AI processing
frame = hardware_manager.camera.get_ai_frame()

# Process with AI
detections = your_ai_model.detect(frame)

# Control based on detections
if person_detected:
    hardware_manager.servo.set_angle(pan=angle_to_person)
```

### For Web Dashboard Integration

```python
# Get comprehensive system status
status = hardware_manager.get_status()

# Returns:
# {
#   'motor': {'direction': 'forward', 'speed': 80, ...},
#   'servo': {'pan': 45, 'tilt': 20, ...},
#   'led': {'color': [255, 0, 0], ...},
#   'ultrasonic': {'distance': 35.2, ...},
#   'camera': {'fps': 30, ...},
#   'emergency': {'active': False, ...},
#   'watchdog': {'status': 'healthy', ...}
# }
```

## 📝 Development

### Adding New Hardware

1. Create controller in `Drivers/hardware/[component]/`
2. Add configuration to `config/hardware/`
3. Update `hardware_manager.py` to initialize component
4. Add MQTT handlers in `mqtt_device_controller_integrated.py`
5. Add tests in `tests/`

### Code Style

- Use type hints
- Write docstrings
- Follow SOLID principles
- Keep modules independent
- Use thread-safe patterns

## 🎯 Features

### Hardware Control
✅ Professional motor control with smooth acceleration  
✅ Servo control with angle limits  
✅ RGB LED with 6 animation effects  
✅ Ultrasonic distance measurement with filtering  
✅ Camera capture with dual buffers  

### Safety Systems
✅ Emergency stop with multiple triggers  
✅ Watchdog monitoring  
✅ Hardware health checking  
✅ Obstacle detection  

### Network Communication
✅ MQTT local/cloud broker support  
✅ Auto-reconnection with exponential backoff  
✅ Real-time sensor data publishing  
✅ Command/response pattern  

### Architecture
✅ Thread-safe operations  
✅ Configuration-driven design  
✅ Modular and extensible  
✅ Production-ready code quality  

## 📄 License

Educational and development use.

## 🙏 Acknowledgments

- Hardware control system by Kareem Ahmed
- MQTT integration and system orchestration
- Built for IoT Surveillance Car project

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Platform**: Raspberry Pi 3/4
