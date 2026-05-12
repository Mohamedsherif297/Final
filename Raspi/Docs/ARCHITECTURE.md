# System Architecture

Complete architecture documentation for the Surveillance Car system.

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interfaces                          │
│  (MQTT Client, Web Dashboard, Mobile App, CLI)              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  Network Layer (MQTT)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  mqtt_device_controller_integrated.py                │  │
│  │  - Command routing                                    │  │
│  │  - Status publishing                                  │  │
│  │  - Sensor data streaming                             │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              Hardware Manager (Coordinator)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  hardware_manager.py                                  │  │
│  │  - Component initialization                           │  │
│  │  - Safety system coordination                         │  │
│  │  - Status aggregation                                 │  │
│  │  - Emergency handling                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
┌──────────────┬──────────────┬──────────────┐
│   Motor      │    Servo     │     LED      │
│ Controller   │  Controller  │  Controller  │
└──────────────┴──────────────┴──────────────┘
        ↓            ↓            ↓
┌──────────────┬──────────────┬──────────────┐
│  Ultrasonic  │   Camera     │   Safety     │
│  Controller  │  Controller  │   Systems    │
└──────────────┴──────────────┴──────────────┘
        ↓            ↓            ↓
┌─────────────────────────────────────────────┐
│         GPIO/PWM Managers                    │
│  (Centralized hardware access)              │
└─────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────┐
│         Physical Hardware                    │
│  (Motors, Servos, LEDs, Sensors, Camera)   │
└─────────────────────────────────────────────┘
```

## 📦 Component Details

### 1. Hardware Layer (Drivers/)

#### GPIO/PWM Managers
**Purpose**: Centralized hardware access control

**Components**:
- `gpio_manager.py` - GPIO pin management (singleton)
- `pwm_manager.py` - PWM channel management (singleton)
- `pin_definitions.py` - Configuration loader

**Key Features**:
- Thread-safe operations
- Pin conflict detection
- Reserved pin protection
- Simulation mode for development

**Design Pattern**: Singleton (ensures single hardware access point)

#### Component Controllers

**Motor Controller** (`motor/`)
- High-level: `motor_controller.py` - User-friendly API
- Low-level: `motor_driver.py` - L298N driver interface
- Safety: `motor_safety.py` - Speed/direction validation

**Servo Controller** (`servo/`)
- High-level: `servo_controller.py` - Angle-based control
- Calibration: `servo_calibration.py` - Angle to PWM conversion
- Limits: `servo_limits.py` - Angle validation

**LED Controller** (`led/`)
- Controller: `led_controller.py` - RGB control
- Effects: `led_effects.py` - Animation implementations
- Patterns: `led_patterns.py` - Color definitions

**Ultrasonic Controller** (`ultrasonic/`)
- Controller: `ultrasonic_controller.py` - Distance measurement
- Filter: `distance_filter.py` - Noise reduction
- Detection: `obstacle_detection.py` - Obstacle logic

**Camera Controller** (`camera/`)
- Controller: `camera_controller.py` - Capture management
- Stream: `stream_handler.py` - Frame streaming
- Buffer: `frame_buffer.py` - Dual buffer system

#### Safety Systems (`safety/`)

**Emergency Stop** (`emergency_stop.py`)
- Multiple trigger types
- Callback system
- State management

**Watchdog** (`watchdog.py`)
- Component heartbeat monitoring
- Timeout detection
- Auto-emergency trigger

**Hardware Monitor** (`hardware_monitor.py`)
- Component state tracking
- Health checking
- System-wide status

#### Hardware Manager (`managers/`)

**hardware_manager.py** - Central coordinator
- Initializes all components
- Coordinates safety systems
- Aggregates status
- Handles emergencies
- Provides unified API

**Design Pattern**: Facade (simplifies complex subsystem)

### 2. Network Layer (Network/)

#### MQTT Module (`MQTT/`)

**mqtt_device_controller_integrated.py** - Main controller
- Command routing (motor, LED, servo)
- Status publishing
- Sensor data streaming
- Emergency alerts
- Heartbeat management

**connection_manager.py** - Connection management
- Local/cloud broker support
- Auto-reconnection
- Exponential backoff
- TLS support

**mqtt_topics.py** - Topic definitions
- Centralized topic management
- Command topics
- Status topics
- Sensor topics

**Design Pattern**: Observer (MQTT pub/sub)

### 3. Configuration Layer (config/)

#### Hardware Configurations (`hardware/`)

**gpio_config.yaml** - Pin mappings
```yaml
motor:
  left_motor:
    enable: 12
    input1: 23
    input2: 24
```

**pwm_config.yaml** - PWM settings
```yaml
motor:
  frequency: 1000
  duty_cycle_range: [0, 100]
```

**servo_config.yaml** - Servo limits
```yaml
pan:
  min_angle: -90
  max_angle: 90
  center: 0
```

**safety_config.yaml** - Safety thresholds
```yaml
obstacle_detection:
  threshold: 20
  emergency_threshold: 15
```

### 4. System Orchestration

**main.py** - Entry point
- System initialization
- Component lifecycle
- Graceful shutdown
- Signal handling

**Design Pattern**: Orchestrator

## 🔄 Data Flow

### Command Flow (User → Hardware)

```
User/Client
    ↓ (MQTT publish)
MQTT Broker
    ↓ (subscribe)
mqtt_device_controller_integrated
    ↓ (parse & route)
hardware_manager
    ↓ (delegate)
Component Controller (motor/servo/led)
    ↓ (validate)
GPIO/PWM Manager
    ↓ (execute)
Physical Hardware
```

### Status Flow (Hardware → User)

```
Physical Hardware
    ↓ (read)
Component Controller
    ↓ (process)
hardware_manager.get_status()
    ↓ (aggregate)
mqtt_device_controller_integrated
    ↓ (publish)
MQTT Broker
    ↓ (deliver)
User/Client
```

### Sensor Flow (Continuous)

```
Ultrasonic Sensor
    ↓ (measure - 10Hz)
ultrasonic_controller
    ↓ (filter)
distance_filter
    ↓ (check threshold)
obstacle_detection
    ↓ (if obstacle)
emergency_stop
    ↓ (trigger)
hardware_manager
    ↓ (stop motors)
Motor Controller
```

### Emergency Flow

```
Trigger Source (obstacle/timeout/manual)
    ↓
emergency_stop.trigger_emergency()
    ↓
Execute Callbacks
    ├→ Stop Motors
    ├→ Set LED Red
    ├→ Publish MQTT Alert
    └→ Log Event
    ↓
Block New Commands
```

## 🧵 Threading Architecture

### Thread Overview

```
Main Thread
├── System initialization
├── MQTT connection
└── Signal handling

MQTT Loop Thread (paho-mqtt)
├── Message receiving
├── Callback execution
└── Keep-alive

Camera Capture Thread
├── Frame capture (30 FPS)
├── Buffer management
└── Frame processing

Ultrasonic Monitor Thread
├── Distance measurement (10 Hz)
├── Filtering
└── Obstacle detection

LED Effect Thread (when active)
├── Animation execution
└── Color transitions

Watchdog Thread
├── Heartbeat monitoring (1 Hz)
├── Timeout detection
└── Emergency triggering

Sensor Publishing Thread
├── Sensor data collection
└── MQTT publishing (10 Hz)

Heartbeat Thread
├── Component heartbeats (1 Hz)
└── Watchdog updates
```

### Thread Safety

**Mechanisms**:
- `threading.RLock` - Reentrant locks for nested calls
- `queue.Queue` - Thread-safe frame buffers
- `@thread_safe` decorator - Automatic locking
- `threading.Event` - Thread synchronization

**Critical Sections**:
- GPIO pin access (protected by gpio_manager lock)
- PWM channel access (per-channel locks)
- Hardware manager operations (RLock)
- Emergency stop state (lock)

## 🔒 Safety Architecture

### Safety Layers

**Layer 1: Input Validation**
- Speed limits (0-100)
- Angle limits (servo ranges)
- Direction validation
- Parameter type checking

**Layer 2: Component Safety**
- Motor safety (acceleration limits, direction change delays)
- Servo limits (angle boundaries)
- Emergency stop state checking

**Layer 3: System Safety**
- Obstacle detection (ultrasonic threshold)
- Watchdog monitoring (component timeouts)
- Hardware health checking

**Layer 4: Emergency Override**
- Emergency stop (immediate halt)
- Callback system (coordinated response)
- State blocking (prevent new commands)

### Emergency Triggers

1. **OBSTACLE_DETECTED** - Ultrasonic < threshold
2. **COMMUNICATION_TIMEOUT** - No heartbeat
3. **INVALID_GPIO_STATE** - Hardware error
4. **MANUAL_BUTTON** - User trigger
5. **WATCHDOG_TIMEOUT** - Component failure
6. **HARDWARE_ERROR** - Exception in hardware

### Emergency Response

```
Trigger Detected
    ↓
emergency_stop.trigger_emergency(trigger, message)
    ↓
Set emergency_active = True
    ↓
Execute Registered Callbacks
    ├→ hardware_manager._emergency_handler()
    │   ├→ motor.emergency_stop()
    │   └→ led.set_status_color('emergency')
    └→ mqtt_controller._on_emergency()
        └→ Publish emergency alert
    ↓
Block New Commands
    └→ All controllers check emergency_active
```

## 📊 Configuration Architecture

### Configuration Hierarchy

```
config/
└── hardware/
    ├── gpio_config.yaml      (Pin mappings)
    ├── pwm_config.yaml       (PWM settings)
    ├── servo_config.yaml     (Servo limits)
    └── safety_config.yaml    (Safety thresholds)
```

### Configuration Loading

**Path Resolution** (tries in order):
1. `../config/hardware/[config].yaml` (relative to module)
2. `config/hardware/[config].yaml` (from project root)
3. `configs/[config].yaml` (legacy path)

**Loading Strategy**:
- Loaded at module initialization
- Singleton pattern ensures single load
- Validation on load
- Defaults if config missing

### Configuration Usage

```python
# In component controller
from hardware.gpio.pin_definitions import pin_defs

# Access configuration
motor_pins = pin_defs.motor
enable_pin = motor_pins.left_enable

# Validate
pin_defs.validate_pin(enable_pin)
```

## 🔌 Integration Points

### Hardware ↔ MQTT

**Interface**: `mqtt_device_controller_integrated.py`

**Flow**:
```python
# MQTT command received
def handle_motor_command(data):
    direction = data['direction']
    speed = data['speed']
    
    # Call hardware manager
    hardware_manager.motor.move_forward(speed)
    
    # Send confirmation
    self.send_status("motor_moved", {...})
```

### Hardware ↔ AI (Future)

**Interface**: `AI/vision_controller.py` (to be created)

**Flow**:
```python
# Get frame from hardware
frame = hardware_manager.camera.get_ai_frame()

# Process with AI
detections = ai_model.detect(frame)

# Control hardware based on AI
if person_detected:
    hardware_manager.servo.set_angle(pan=angle)
```

### MQTT ↔ WebSocket (Future)

**Interface**: `Network/WebSockets/websocket_server.py` (to be created)

**Flow**:
```python
# Bridge MQTT to WebSocket
mqtt_client.subscribe("sensors/#")

def on_mqtt_message(msg):
    # Forward to WebSocket clients
    websocket.broadcast(msg)
```

## 🎯 Design Patterns Used

1. **Singleton** - GPIO Manager, PWM Manager, Hardware Manager
2. **Facade** - Hardware Manager (simplifies subsystem)
3. **Observer** - MQTT pub/sub, Emergency callbacks
4. **Strategy** - LED effects (different animation algorithms)
5. **Factory** - PWM channel creation
6. **Decorator** - @thread_safe for automatic locking
7. **Orchestrator** - main.py (coordinates lifecycle)

## 📈 Scalability

### Adding New Hardware

1. Create controller in `Drivers/hardware/[component]/`
2. Add configuration to `config/hardware/`
3. Initialize in `hardware_manager.py`
4. Add MQTT handlers in `mqtt_device_controller_integrated.py`
5. Add tests

### Adding New Communication Protocol

1. Create module in `Network/[protocol]/`
2. Use `hardware_manager` for hardware access
3. Implement protocol-specific logic
4. Update `main.py` to initialize

### Adding AI Features

1. Create module in `AI/`
2. Get frames from `hardware_manager.camera`
3. Control hardware via `hardware_manager`
4. Publish results via MQTT

## 🔍 Monitoring & Debugging

### Status Monitoring

```python
# Get comprehensive status
status = hardware_manager.get_status()

# Returns:
{
    'initialized': True,
    'emergency': {...},
    'watchdog': {...},
    'health': 'healthy',
    'motor': {...},
    'servo': {...},
    'led': {...},
    'ultrasonic': {...},
    'camera': {...}
}
```

### Logging

- All components use centralized logger
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Format: `[COMPONENT] Message`
- Example: `[MQTT] Connected to broker successfully`

### MQTT Monitoring

```bash
# Monitor all topics
mosquitto_sub -h localhost -t '#' -v

# Monitor specific subsystem
mosquitto_sub -h localhost -t 'sensors/#' -v
mosquitto_sub -h localhost -t 'emergency/#' -v
```

---

**Document Version**: 1.0  
**Last Updated**: Integration Complete  
**Status**: Production Ready
