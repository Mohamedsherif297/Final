# System Diagram

Visual representation of the Surveillance Car system architecture.

## 🎯 Complete System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ MQTT Client  │  │ Web Dashboard│  │  Mobile App  │             │
│  │ (mosquitto)  │  │   (Browser)  │  │   (Phone)    │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
└─────────┼──────────────────┼──────────────────┼────────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │  MQTT Broker    │
                    │  (Mosquitto)    │
                    │  Port: 1883     │
                    └────────┬────────┘
                             │
┌────────────────────────────┼────────────────────────────────────────┐
│                    NETWORK LAYER                                     │
│                    ┌────────▼────────┐                              │
│                    │ MQTT Controller │                              │
│                    │  (Integrated)   │                              │
│                    │                 │                              │
│                    │ • Command Route │                              │
│                    │ • Status Pub    │                              │
│                    │ • Sensor Stream │                              │
│                    │ • Emergency Pub │                              │
│                    └────────┬────────┘                              │
└─────────────────────────────┼──────────────────────────────────────┘
                              │
┌─────────────────────────────┼──────────────────────────────────────┐
│                    HARDWARE MANAGER                                  │
│                    ┌────────▼────────┐                              │
│                    │ hardware_manager│                              │
│                    │   (Coordinator) │                              │
│                    │                 │                              │
│                    │ • Initialize    │                              │
│                    │ • Coordinate    │                              │
│                    │ • Monitor       │                              │
│                    │ • Emergency     │                              │
│                    └────────┬────────┘                              │
└─────────────────────────────┼──────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌───────▼────────┐
│ Motor Control  │   │ Servo Control   │   │  LED Control   │
│                │   │                 │   │                │
│ • Forward      │   │ • Pan/Tilt      │   │ • RGB Colors   │
│ • Backward     │   │ • Angle Limits  │   │ • Effects      │
│ • Turn L/R     │   │ • Smooth Move   │   │ • Status       │
│ • Smooth Accel │   │ • Presets       │   │ • Animations   │
└───────┬────────┘   └────────┬────────┘   └───────┬────────┘
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌───────▼────────┐
│   Ultrasonic   │   │     Camera      │   │ Safety Systems │
│                │   │                 │   │                │
│ • Distance     │   │ • Capture       │   │ • Emergency    │
│ • Filtering    │   │ • Dual Buffer   │   │ • Watchdog     │
│ • Obstacle Det │   │ • 30 FPS        │   │ • Monitor      │
│ • Callbacks    │   │ • AI Buffer     │   │ • Health Check │
└───────┬────────┘   └────────┬────────┘   └───────┬────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
┌─────────────────────────────┼──────────────────────────────────────┐
│                    GPIO/PWM LAYER                                    │
│                    ┌────────▼────────┐                              │
│                    │  GPIO Manager   │                              │
│                    │  PWM Manager    │                              │
│                    │                 │                              │
│                    │ • Pin Control   │                              │
│                    │ • PWM Channels  │                              │
│                    │ • Thread-Safe   │                              │
│                    │ • Validation    │                              │
│                    └────────┬────────┘                              │
└─────────────────────────────┼──────────────────────────────────────┘
                              │
┌─────────────────────────────┼──────────────────────────────────────┐
│                    PHYSICAL HARDWARE                                 │
│                                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │  Motors  │  │  Servos  │  │   LEDs   │  │  Sensors │          │
│  │  (L298N) │  │ (Pan/Tilt│  │  (RGB)   │  │(HC-SR04) │          │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘          │
│                                                                      │
│  ┌──────────────────────────────────────────────────────┐          │
│  │              Camera (USB/CSI)                         │          │
│  └──────────────────────────────────────────────────────┘          │
└──────────────────────────────────────────────────────────────────────┘
```

## 📡 MQTT Topic Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      MQTT TOPICS                             │
└─────────────────────────────────────────────────────────────┘

COMMAND TOPICS (Subscribe) ──────────────────────────────────┐
                                                              │
dev/motor          ──→  Motor commands                       │
  {"direction": "forward", "speed": 80}                      │
                                                              │
dev/led            ──→  LED commands                         │
  {"action": "set_rgb", "red": 255, "green": 0, "blue": 0}  │
                                                              │
dev/servo          ──→  Servo commands                       │
  {"action": "set_angle", "pan": 45, "tilt": 20}            │
                                                              │
dev/commands       ──→  General commands                     │
  {"command": "status"}                                      │
                                                              │
                                                              ▼
                                              ┌───────────────────────┐
                                              │  MQTT Controller      │
                                              │  (Process & Route)    │
                                              └───────────────────────┘
                                                              │
                                                              ▼
                                              ┌───────────────────────┐
                                              │  Hardware Manager     │
                                              │  (Execute Commands)   │
                                              └───────────────────────┘
                                                              │
                                                              ▼
STATUS TOPICS (Publish) ◄─────────────────────────────────────┘

dev/status         ◄──  Status updates
  {"type": "motor_moved", "message": {...}}

sensors/ultrasonic ◄──  Distance data (10 Hz)
  {"distance": 35.2, "timestamp": 1234567890}

sensors/obstacle   ◄──  Obstacle alerts
  {"distance": 15.0, "timestamp": 1234567890}

emergency/alert    ◄──  Emergency events
  {"trigger": "OBSTACLE_DETECTED", "message": "..."}
```

## 🔄 Data Flow Diagrams

### Motor Command Flow

```
User
  │
  │ mosquitto_pub -t dev/motor -m '{"direction": "forward", "speed": 80}'
  │
  ▼
MQTT Broker
  │
  │ (message delivery)
  │
  ▼
mqtt_device_controller_integrated.py
  │
  │ on_message() → handle_motor_command()
  │
  ▼
hardware_manager.motor.move_forward(80)
  │
  │ (validate speed, check emergency)
  │
  ▼
motor_controller.py
  │
  │ (smooth acceleration, direction validation)
  │
  ▼
motor_driver.py
  │
  │ (set GPIO pins, PWM duty cycle)
  │
  ▼
gpio_manager / pwm_manager
  │
  │ (thread-safe GPIO access)
  │
  ▼
Physical Motors
  │
  │ (motors spin)
  │
  ▼
Status Published
  │
  │ dev/status: {"type": "motor_moved", ...}
  │
  ▼
User Receives Confirmation
```

### Sensor Data Flow

```
Ultrasonic Sensor (HC-SR04)
  │
  │ (trigger pulse, measure echo)
  │
  ▼
ultrasonic_controller.py
  │
  │ (continuous monitoring thread - 10 Hz)
  │
  ▼
distance_filter.py
  │
  │ (moving average, median filter)
  │
  ▼
obstacle_detection.py
  │
  ├─→ (distance > threshold) → Normal
  │
  └─→ (distance < threshold) → Trigger Emergency
      │
      ▼
  emergency_stop.trigger_emergency()
      │
      ├─→ Stop Motors
      ├─→ Set LED Red
      └─→ Publish Alert
          │
          ▼
      emergency/alert topic
```

### Emergency Flow

```
Trigger Source
  │
  ├─→ Obstacle Detected (ultrasonic < 20cm)
  ├─→ Watchdog Timeout (no heartbeat > 10s)
  ├─→ Manual Button (MQTT command)
  ├─→ Hardware Error (exception)
  │
  ▼
emergency_stop.trigger_emergency(trigger, message)
  │
  │ (set emergency_active = True)
  │
  ▼
Execute Callbacks
  │
  ├─→ hardware_manager._emergency_handler()
  │   │
  │   ├─→ motor.emergency_stop()
  │   │   └─→ Motors stop immediately
  │   │
  │   └─→ led.set_status_color('emergency')
  │       └─→ LED turns red
  │
  └─→ mqtt_controller._on_emergency()
      │
      └─→ Publish to emergency/alert
          └─→ User notified
  │
  ▼
Block New Commands
  │
  └─→ All controllers check emergency_active
      └─→ Reject commands until reset
```

## 🧵 Thread Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      MAIN THREAD                             │
│  • System initialization                                     │
│  • Signal handling (Ctrl+C)                                  │
│  • Graceful shutdown                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ spawns
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ MQTT Loop    │    │ Camera       │    │ Ultrasonic   │
│ Thread       │    │ Capture      │    │ Monitor      │
│              │    │ Thread       │    │ Thread       │
│ • Receive    │    │              │    │              │
│ • Callbacks  │    │ • Capture    │    │ • Measure    │
│ • Keep-alive │    │ • Buffer     │    │ • Filter     │
│              │    │ • 30 FPS     │    │ • Detect     │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Sensor Pub   │    │ LED Effect   │    │ Watchdog     │
│ Thread       │    │ Thread       │    │ Thread       │
│              │    │ (when active)│    │              │
│ • Collect    │    │              │    │ • Monitor    │
│ • Publish    │    │ • Animate    │    │ • Timeout    │
│ • 10 Hz      │    │ • Transitions│    │ • Emergency  │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Heartbeat Thread │
                    │                  │
                    │ • Send beats     │
                    │ • 1 Hz           │
                    └──────────────────┘
```

## 🔒 Safety System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    SAFETY LAYERS                             │
└─────────────────────────────────────────────────────────────┘

Layer 1: INPUT VALIDATION
┌─────────────────────────────────────────────────────────────┐
│ • Speed limits (0-100)                                       │
│ • Angle limits (servo ranges)                               │
│ • Direction validation                                       │
│ • Parameter type checking                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Layer 2: COMPONENT SAFETY
┌─────────────────────────────────────────────────────────────┐
│ • Motor safety (acceleration limits)                        │
│ • Direction change delays                                    │
│ • Servo angle boundaries                                     │
│ • Emergency stop state checking                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Layer 3: SYSTEM SAFETY
┌─────────────────────────────────────────────────────────────┐
│ • Obstacle detection (ultrasonic threshold)                 │
│ • Watchdog monitoring (component timeouts)                  │
│ • Hardware health checking                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Layer 4: EMERGENCY OVERRIDE
┌─────────────────────────────────────────────────────────────┐
│ • Emergency stop (immediate halt)                           │
│ • Callback system (coordinated response)                    │
│ • State blocking (prevent new commands)                     │
│ • Alert publishing (notify users)                           │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Configuration Hierarchy

```
config/
└── hardware/
    │
    ├── gpio_config.yaml
    │   ├── motor pins
    │   ├── servo pins
    │   ├── led pins
    │   ├── ultrasonic pins
    │   └── reserved pins
    │
    ├── pwm_config.yaml
    │   ├── motor frequency
    │   ├── servo frequency
    │   └── led frequency
    │
    ├── servo_config.yaml
    │   ├── pan limits
    │   ├── tilt limits
    │   └── presets
    │
    └── safety_config.yaml
        ├── obstacle threshold
        ├── motor safety
        └── watchdog timeout
```

## 🎯 Integration Points

```
┌─────────────────────────────────────────────────────────────┐
│                    CURRENT SYSTEM                            │
│                                                              │
│  Hardware Layer ◄──► MQTT Controller                        │
│       ✅ Complete                                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    FUTURE INTEGRATIONS                       │
│                                                              │
│  Hardware Layer ◄──► AI Vision Controller                   │
│       🚧 To be integrated                                    │
│                                                              │
│  MQTT ◄──► WebSocket ◄──► Web Dashboard                     │
│       📝 To be implemented                                   │
│                                                              │
│  AI Vision ◄──► WebSocket ◄──► Video Stream                 │
│       📝 To be implemented                                   │
└─────────────────────────────────────────────────────────────┘
```

---

**This diagram shows the complete integrated system architecture.**  
**All components are connected and working together seamlessly.**
