# Laptop Controller - Surveillance Car

Desktop GUI controller for the surveillance car using Tkinter and MQTT.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run GUI Controller
```bash
python mqtt_gui_controller.py
```

## 🎮 Features

### Movement Controls
- **D-Pad Buttons**: Click to move (Forward, Backward, Left, Right, Stop)
- **Keyboard**: Arrow keys or WASD
- **Speed Slider**: Adjust speed 0-100%
- **Auto-Stop**: Release key to stop

### Peripherals
- **Servo Control**: Slider 0-180° or Q/E keys
- **LED Control**: On/Off/Blink buttons
- **Beep**: Sound buzzer
- **Center**: Reset servo to 90°

### Monitoring
- **Real-time Status**: Live feedback from Raspberry Pi
- **Log Viewer**: See all commands and responses
- **Connection Status**: Visual indicator

### Broker Modes
- **Local Mode**: Connect to Raspberry Pi on same network
- **Cloud Mode**: Connect via HiveMQ from anywhere
- **Easy Switch**: Toggle between modes in GUI

## 📁 Files

- `mqtt_gui_controller.py` - Main GUI application
- `ui_components.py` - Reusable UI components
- `connection_manager.py` - MQTT broker management
- `utils/batch_commands.py` - Automated command sequences
- `utils/connection_test.py` - Test MQTT connection
- `utils/message_validator.py` - Validate message formats
- `utils/network_scanner.py` - Find Pi on network

## 🔧 Configuration

Edit broker settings in the GUI or modify `connection_manager.py`:
- **Local**: localhost:1883
- **Cloud**: HiveMQ credentials in config

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| ↑ / W | Forward |
| ↓ / S | Backward |
| ← / A | Left |
| → / D | Right |
| Space | Stop |
| Q | Servo left |
| E | Servo right |

## 🧪 Testing

### Batch Commands
Run automated sequences:
```bash
python utils/batch_commands.py forward left right stop
```

### Connection Test
```bash
python utils/connection_test.py
```

## 📊 MQTT Topics

### Commands (Publish)
- `dev/motor` - Motor control
- `dev/led` - LED control
- `dev/servo` - Servo control
- `dev/commands` - General commands

### Status (Subscribe)
- `dev/status` - Device status updates
- `sensors/ultrasonic` - Distance data
- `emergency/alert` - Emergency events

## 🎯 Usage Tips

1. **Start Raspberry Pi first** - Run `python3 main.py` on Pi
2. **Choose broker mode** - Local for same network, Cloud for internet
3. **Test connection** - Check status indicator turns green
4. **Control the car** - Use buttons or keyboard
5. **Monitor status** - Watch log and Pi status display

## 🔍 Troubleshooting

**GUI won't start:**
- Ensure Python 3.7+ installed
- Install paho-mqtt: `pip install paho-mqtt`
- Tkinter should be included with Python

**Can't connect:**
- Local: Check Pi IP address and Mosquitto running
- Cloud: Verify HiveMQ credentials
- Firewall: Allow port 1883 (local) or 8883 (cloud)

**Commands not working:**
- Check Raspberry Pi is running main.py
- Verify MQTT topics match
- Check log for errors

## 📝 Notes

- GUI uses same connection_manager as Raspberry Pi
- Supports both local and cloud MQTT brokers
- Real-time status updates from Pi
- Keyboard controls for quick testing
- Beautiful dark theme UI

---

**Platform**: Windows, macOS, Linux  
**Python**: 3.7+  
**Status**: Production Ready
