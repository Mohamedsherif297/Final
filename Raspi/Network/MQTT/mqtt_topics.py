"""
MQTT Topics Configuration
Centralized topic definitions for the surveillance car
All MQTT components should import topics from here
"""

# Device Control Topics
TOPIC_MOTOR = "dev/motor"           # Motor control commands
TOPIC_LED = "dev/led"               # LED control commands
TOPIC_SERVO = "dev/servo"           # Servo control (camera pan/tilt)
TOPIC_COMMANDS = "dev/commands"     # General system commands
TOPIC_STATUS = "dev/status"         # Device status updates

# Sensor Topics
TOPIC_ULTRASONIC = "sensors/ultrasonic"     # Distance sensor data
TOPIC_BATTERY = "sensors/battery"           # Battery voltage/status

# AI/Vision Topics
TOPIC_CAMERA = "vision/camera"              # Camera control
TOPIC_FACE_DETECTION = "vision/faces"       # Face detection results
TOPIC_OBJECT_DETECTION = "vision/objects"   # Object detection results
TOPIC_TRACKING = "vision/tracking"          # Target tracking data

# Telemetry Topics
TOPIC_TELEMETRY = "telemetry/system"        # System health metrics
TOPIC_PERFORMANCE = "telemetry/performance" # Performance metrics

# Mode Control
TOPIC_MODE = "control/mode"                 # Operating mode changes

# Emergency
TOPIC_EMERGENCY = "emergency/stop"          # Emergency stop

# Audio
TOPIC_AUDIO = "audio/stream"                # Audio streaming

# All topics list (for easy subscription)
ALL_COMMAND_TOPICS = [
    TOPIC_MOTOR,
    TOPIC_LED,
    TOPIC_SERVO,
    TOPIC_COMMANDS,
    TOPIC_CAMERA,
    TOPIC_MODE,
    TOPIC_EMERGENCY
]

ALL_STATUS_TOPICS = [
    TOPIC_STATUS,
    TOPIC_ULTRASONIC,
    TOPIC_BATTERY,
    TOPIC_FACE_DETECTION,
    TOPIC_OBJECT_DETECTION,
    TOPIC_TRACKING,
    TOPIC_TELEMETRY,
    TOPIC_PERFORMANCE
]

# Topic descriptions for documentation
TOPIC_DESCRIPTIONS = {
    TOPIC_MOTOR: "Motor control: {direction: 'forward'|'backward'|'left'|'right'|'stop', speed: 0-100}",
    TOPIC_LED: "LED control: {state: 'on'|'off'|'blink', color: 'red'|'green'|'blue'}",
    TOPIC_SERVO: "Servo control: {pan: 0-180, tilt: 0-180}",
    TOPIC_COMMANDS: "General commands: {command: 'status'|'stop_all'|'emergency_stop'}",
    TOPIC_STATUS: "Device status updates",
    TOPIC_ULTRASONIC: "Distance sensor readings in cm",
    TOPIC_FACE_DETECTION: "Detected faces with coordinates",
    TOPIC_OBJECT_DETECTION: "Detected objects with bounding boxes",
    TOPIC_TRACKING: "Target tracking coordinates",
    TOPIC_MODE: "Operating mode: {mode: 1|2|3}",
    TOPIC_EMERGENCY: "Emergency stop signal"
}

def get_all_topics():
    """Get all topics as a list"""
    return ALL_COMMAND_TOPICS + ALL_STATUS_TOPICS

def get_topic_description(topic):
    """Get description for a specific topic"""
    return TOPIC_DESCRIPTIONS.get(topic, "No description available")

def print_topics():
    """Print all topics with descriptions"""
    print("=" * 60)
    print("MQTT Topics Configuration")
    print("=" * 60)
    
    print("\n📤 COMMAND TOPICS (Subscribe on device):")
    for topic in ALL_COMMAND_TOPICS:
        print(f"  • {topic}")
        print(f"    {get_topic_description(topic)}")
    
    print("\n📥 STATUS TOPICS (Publish from device):")
    for topic in ALL_STATUS_TOPICS:
        print(f"  • {topic}")
        print(f"    {get_topic_description(topic)}")
    
    print("=" * 60)

if __name__ == "__main__":
    print_topics()
