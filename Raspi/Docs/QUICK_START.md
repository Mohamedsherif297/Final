# Quick Start Guide

Get your surveillance car running in 5 minutes!

## 📋 Prerequisites

- Raspberry Pi 3 or 4
- Hardware connected (motors, servos, LEDs, sensors)
- Internet connection (for initial setup)

## 🚀 Installation

### Step 1: Copy Files to Raspberry Pi

```bash
# On your computer, copy the Final/Raspi folder to your Pi
scp -r Final/Raspi pi@raspberrypi.local:~/surveillance-car

# Or use a USB drive
```

### Step 2: Run Setup Script

```bash
# SSH into your Raspberry Pi
ssh pi@raspberrypi.local

# Navigate to project
cd ~/surveillance-car

# Run setup script
./setup.sh

# Reboot
sudo reboot
```

### Step 3: Verify Hardware Connections

Check that your hardware matches `config/hardware/gpio_config.yaml`:

```yaml
motor:
  left_motor:
    enable: 12    # BCM GPIO 12
    input1: 23    # BCM GPIO 23
    input2: 24    # BCM GPIO 24
  right_motor:
    enable: 13    # BCM GPIO 13
    input3: 27    # BCM GPIO 27
    input4: 22    # BCM GPIO 22

servo:
  pan:
    pin: 17       # BCM GPIO 17
  tilt:
    pin: 18       # BCM GPIO 18

led:
  red: 16         # BCM GPIO 16
  green: 20       # BCM GPIO 20
  blue: 21        # BCM GPIO 21

ultrasonic:
  trigger: 5      # BCM GPIO 5
  echo: 6         # BCM GPIO 6
```

⚠️ **Important**: Connect external 12V power to motors!

## ▶️ Run the System

```bash
cd ~/surveillance-car
python3 main.py
```

You should see:
```
============================================================
Surveillance Car System - Initializing
============================================================
[SYSTEM] Initializing hardware...
[SYSTEM] Hardware initialized successfully
[SYSTEM] Initializing MQTT controller...
[MQTT] Connected to broker successfully
[SYSTEM] System running. Press Ctrl+C to exit.
```

## 🎮 Test Control

Open a new terminal and test commands:

### Test Motor

```bash
# Move forward
mosquitto_pub -h localhost -t dev/motor -m '{"direction": "forward", "speed": 50}'

# Stop
mosquitto_pub -h localhost -t dev/motor -m '{"direction": "stop"}'
```

### Test LED

```bash
# Set green color
mosquitto_pub -h localhost -t dev/led -m '{"action": "set_rgb", "red": 0, "green": 255, "blue": 0}'
```

### Test Servo

```bash
# Center servos
mosquitto_pub -h localhost -t dev/servo -m '{"action": "center"}'
```

### Monitor Status

```bash
# Watch all status updates
mosquitto_sub -h localhost -t dev/status -v

# Watch sensor data
mosquitto_sub -h localhost -t sensors/# -v
```

## 🔧 Troubleshooting

### "Permission denied" on GPIO

```bash
sudo usermod -a -G gpio $USER
sudo reboot
```

### "Cannot connect to MQTT broker"

```bash
# Check broker is running
sudo systemctl status mosquitto

# Restart broker
sudo systemctl restart mosquitto
```

### Motors not moving

1. Check external power is connected
2. Check common ground between Pi and motor driver
3. Verify GPIO pins in config match your wiring
4. Test GPIO: `gpio readall`

### Camera not working

```bash
# Enable camera
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot
```

## 📱 Remote Control

### From Another Computer

```bash
# Replace 'raspberrypi.local' with your Pi's IP
mosquitto_pub -h raspberrypi.local -t dev/motor -m '{"direction": "forward", "speed": 70}'
```

### Using Python

```python
import paho.mqtt.client as mqtt
import json

client = mqtt.Client()
client.connect("raspberrypi.local", 1883, 60)

# Move forward
client.publish("dev/motor", json.dumps({
    "direction": "forward",
    "speed": 80
}))
```

## 🎯 Next Steps

1. **Test all hardware**: Run through all motor, LED, and servo commands
2. **Adjust configuration**: Edit `config/hardware/*.yaml` for your setup
3. **Add AI vision**: Integrate with AI module in `AI/` folder
4. **Build dashboard**: Create web interface for control
5. **Add features**: Extend with additional sensors or capabilities

## 📚 More Information

- **Full documentation**: See `README.md`
- **MQTT topics**: See `Network/MQTT/README.md`
- **Hardware architecture**: See `Drivers/hardware/` modules
- **Configuration**: See `config/hardware/` YAML files

## 🆘 Getting Help

If you encounter issues:

1. Check the logs in the terminal
2. Verify hardware connections
3. Test individual components
4. Check configuration files
5. Review `README.md` troubleshooting section

---

**Happy building! 🚗💨**
