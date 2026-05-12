# MQTT Module

This folder contains all MQTT-related files for the surveillance car.

## 📁 Files

### Core Controllers
- **`mqtt_device_controller.py`** - Local MQTT broker controller
  - Connects to local Mosquitto broker
  - Handles motor, LED, and sensor commands
  - Use for local network operation

- **`mqtt_device_controller_cloud.py`** - Cloud MQTT controller
  - Connects to HiveMQ cloud broker
  - Same functionality as local controller
  - Use for internet-based remote control

- **`connection_manager.py`** - Connection management
  - Handles broker connections (local/cloud)
  - Manages authentication
  - Auto-reconnection logic

### Configuration
- **`mqtt_topics.py`** - Centralized topic definitions
  - All MQTT topics defined here
  - Import topics from this file
  - Single source of truth

- **`config/`** - MQTT configuration files
  - `client_config.json` - Client settings
  - `mqtt_topics.json` - Topic mappings
  - `server_profiles.json` - Broker profiles

## 🚀 Usage

### Local Broker Mode
```python
from Network.MQTT.mqtt_device_controller import MQTTDeviceController

controller = MQTTDeviceController(
    broker_host="localhost",
    broker_port=1883
)
controller.start()
```

### Cloud Broker Mode
```python
from Network.MQTT.mqtt_device_controller_cloud import main

# Uses config/client_config.json for HiveMQ settings
main()
```

### Using Topics
```python
from Network.MQTT.mqtt_topics import TOPIC_MOTOR, TOPIC_STATUS

# Subscribe to motor commands
client.subscribe(TOPIC_MOTOR)

# Publish status
client.publish(TOPIC_STATUS, json.dumps({"status": "online"}))
```

## 📋 MQTT Topics

### Command Topics (Subscribe)
- `dev/motor` - Motor control
- `dev/led` - LED control
- `dev/servo` - Servo control
- `dev/commands` - General commands
- `control/mode` - Mode switching
- `emergency/stop` - Emergency stop

### Status Topics (Publish)
- `dev/status` - Device status
- `sensors/ultrasonic` - Distance data
- `vision/faces` - Face detection
- `vision/objects` - Object detection
- `telemetry/system` - System health

## 🔧 Configuration

### Local Broker Setup
1. Install Mosquitto: `sudo apt-get install mosquitto`
2. Start broker: `sudo systemctl start mosquitto`
3. Run controller: `python3 mqtt_device_controller.py`

### Cloud Broker Setup
1. Edit `config/client_config.json`
2. Add HiveMQ credentials
3. Run: `python3 mqtt_device_controller_cloud.py`

## 🧪 Testing

Test files are in `../../tests/`:
- `mqtt_client_tester.py` - Test MQTT pub/sub
- `test_mqtt_system.py` - Full system test

## 📚 Message Formats

### Motor Command
```json
{
  "direction": "forward",
  "speed": 80
}
```

### LED Command
```json
{
  "state": "on",
  "color": "green"
}
```

### Status Update
```json
{
  "type": "motor_moved",
  "message": "Moving forward",
  "timestamp": 1234567890
}
```

## 🔐 Security

- Use authentication for cloud brokers
- Configure TLS/SSL for production
- Keep credentials in config files (not in code)
- Add config files to `.gitignore`

## 🐛 Troubleshooting

**Cannot connect to broker:**
- Check broker is running: `sudo systemctl status mosquitto`
- Check firewall: `sudo ufw allow 1883`
- Verify broker IP/port in config

**Messages not received:**
- Check topic subscriptions
- Verify QoS settings
- Check broker logs: `sudo journalctl -u mosquitto`

**Cloud connection fails:**
- Verify HiveMQ credentials
- Check internet connection
- Ensure TLS/SSL settings are correct
