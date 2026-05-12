# Deployment Checklist

Complete checklist for deploying the Surveillance Car system to Raspberry Pi.

## 📋 Pre-Deployment

### Hardware Preparation
- [ ] Raspberry Pi 3 or 4 with Raspbian OS installed
- [ ] SD card with at least 16GB (32GB recommended)
- [ ] L298N motor driver board
- [ ] 2x DC motors
- [ ] 2x Servo motors (pan/tilt)
- [ ] RGB LED (common cathode)
- [ ] HC-SR04 ultrasonic sensor
- [ ] Camera module (CSI or USB)
- [ ] 12V external power supply for motors
- [ ] Jumper wires and breadboard
- [ ] Power bank or battery for Raspberry Pi

### Software Preparation
- [ ] Raspberry Pi OS updated to latest version
- [ ] SSH enabled on Raspberry Pi
- [ ] WiFi or Ethernet configured
- [ ] Know your Pi's IP address or hostname

---

## 🔌 Hardware Wiring

### Step 1: Power Connections
- [ ] Connect 12V power supply to L298N motor driver
- [ ] Connect common ground between Pi and motor driver
- [ ] Connect Raspberry Pi to power bank/battery
- [ ] **IMPORTANT**: Do NOT power motors from Raspberry Pi!

### Step 2: Motor Connections (BCM Mode)
- [ ] Left Motor Enable → GPIO 12
- [ ] Left Motor IN1 → GPIO 23
- [ ] Left Motor IN2 → GPIO 24
- [ ] Right Motor Enable → GPIO 13
- [ ] Right Motor IN3 → GPIO 27
- [ ] Right Motor IN4 → GPIO 22
- [ ] Connect motors to L298N outputs

### Step 3: Servo Connections
- [ ] Pan Servo Signal → GPIO 17
- [ ] Tilt Servo Signal → GPIO 18
- [ ] Servo Power → 5V (use external power if > 500mA)
- [ ] Servo Ground → GND

### Step 4: LED Connections
- [ ] Red LED → GPIO 16 (with 220Ω resistor)
- [ ] Green LED → GPIO 20 (with 220Ω resistor)
- [ ] Blue LED → GPIO 21 (with 220Ω resistor)
- [ ] Common cathode → GND

### Step 5: Ultrasonic Sensor
- [ ] Trigger → GPIO 5
- [ ] Echo → GPIO 6
- [ ] VCC → 5V
- [ ] GND → GND

### Step 6: Camera
- [ ] CSI camera connected to CSI port, OR
- [ ] USB camera connected to USB port

### Wiring Verification
- [ ] All connections secure
- [ ] No loose wires
- [ ] Common ground established
- [ ] External power connected
- [ ] No short circuits
- [ ] GPIO pins match configuration

---

## 💻 Software Installation

### Step 1: Copy Files to Raspberry Pi

```bash
# From your computer
scp -r Final/Raspi pi@raspberrypi.local:~/surveillance-car

# Or use USB drive
```

- [ ] Files copied successfully
- [ ] All folders present (Drivers, Network, config, tests)

### Step 2: SSH into Raspberry Pi

```bash
ssh pi@raspberrypi.local
```

- [ ] SSH connection successful
- [ ] Logged in as pi user

### Step 3: Navigate to Project

```bash
cd ~/surveillance-car
ls -la
```

- [ ] In correct directory
- [ ] All files visible

### Step 4: Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

- [ ] Setup script executed successfully
- [ ] System packages installed
- [ ] Python packages installed
- [ ] GPIO permissions configured
- [ ] MQTT broker installed
- [ ] No errors during setup

### Step 5: Reboot

```bash
sudo reboot
```

- [ ] System rebooted
- [ ] Reconnected via SSH

---

## ⚙️ Configuration

### Step 1: Verify GPIO Configuration

```bash
cd ~/surveillance-car
cat config/hardware/gpio_config.yaml
```

- [ ] Pin numbers match your wiring
- [ ] All components defined
- [ ] No conflicts

### Step 2: Adjust Configuration (if needed)

```bash
nano config/hardware/gpio_config.yaml
```

- [ ] Updated pin numbers if different
- [ ] Saved changes
- [ ] Configuration valid

### Step 3: Verify MQTT Broker

```bash
sudo systemctl status mosquitto
```

- [ ] Mosquitto running
- [ ] No errors in status

### Step 4: Test MQTT

```bash
# Terminal 1
mosquitto_sub -h localhost -t test -v

# Terminal 2
mosquitto_pub -h localhost -t test -m "hello"
```

- [ ] Message received
- [ ] MQTT working

---

## 🧪 Testing

### Step 1: Test Hardware Initialization

```bash
cd ~/surveillance-car
python3 -c "from Drivers import hardware_manager; hardware_manager.initialize(); print('SUCCESS')"
```

- [ ] No errors
- [ ] "SUCCESS" printed
- [ ] Hardware initialized

### Step 2: Test Individual Components

```bash
# Test imports
python3 -c "from Drivers.hardware.motor.motor_controller import MotorController; print('Motor OK')"
python3 -c "from Drivers.hardware.servo.servo_controller import ServoController; print('Servo OK')"
python3 -c "from Drivers.hardware.led.led_controller import LEDController; print('LED OK')"
```

- [ ] All imports successful
- [ ] No errors

### Step 3: Run Integration Tests

```bash
pytest tests/test_integration.py -v
```

- [ ] All tests passed
- [ ] No failures

---

## 🚀 System Launch

### Step 1: Start System

```bash
cd ~/surveillance-car
python3 main.py
```

Expected output:
```
============================================================
Surveillance Car System - Initializing
============================================================
[SYSTEM] Initializing hardware...
[MQTT] Initializing hardware manager...
[MQTT] Hardware initialized successfully
[MQTT] Connected to broker successfully
[SYSTEM] System running. Press Ctrl+C to exit.
```

- [ ] System started successfully
- [ ] Hardware initialized
- [ ] MQTT connected
- [ ] No errors

### Step 2: Test Motor Control (New Terminal)

```bash
# Move forward
mosquitto_pub -h localhost -t dev/motor -m '{"direction": "forward", "speed": 50}'

# Stop
mosquitto_pub -h localhost -t dev/motor -m '{"direction": "stop"}'
```

- [ ] Motors moved forward
- [ ] Motors stopped
- [ ] LED changed color
- [ ] Status published

### Step 3: Test LED Control

```bash
# Green
mosquitto_pub -h localhost -t dev/led -m '{"action": "set_rgb", "red": 0, "green": 255, "blue": 0}'

# Red
mosquitto_pub -h localhost -t dev/led -m '{"action": "set_rgb", "red": 255, "green": 0, "blue": 0}'
```

- [ ] LED changed to green
- [ ] LED changed to red
- [ ] Colors correct

### Step 4: Test Servo Control

```bash
# Center
mosquitto_pub -h localhost -t dev/servo -m '{"action": "center"}'

# Set angle
mosquitto_pub -h localhost -t dev/servo -m '{"action": "set_angle", "pan": 45, "tilt": 20}'
```

- [ ] Servos centered
- [ ] Servos moved to angle
- [ ] Smooth movement

### Step 5: Monitor Sensor Data

```bash
mosquitto_sub -h localhost -t sensors/# -v
```

- [ ] Distance data streaming
- [ ] Updates at ~10 Hz
- [ ] Values reasonable

### Step 6: Test Emergency Stop

```bash
mosquitto_pub -h localhost -t dev/commands -m '{"command": "emergency_stop"}'
```

- [ ] Motors stopped immediately
- [ ] LED turned red
- [ ] Emergency alert published
- [ ] Commands blocked

### Step 7: Reset Emergency

```bash
mosquitto_pub -h localhost -t dev/commands -m '{"command": "reset_emergency"}'
```

- [ ] Emergency reset
- [ ] Commands accepted again
- [ ] LED back to normal

---

## 🔍 Verification

### System Status Check

```bash
mosquitto_pub -h localhost -t dev/commands -m '{"command": "get_hardware_status"}'
mosquitto_sub -h localhost -t dev/status -v
```

- [ ] Status received
- [ ] All components initialized
- [ ] No emergency active
- [ ] Watchdog healthy

### Component Status

- [ ] Motor: initialized, speed 0, no emergency
- [ ] Servo: initialized, centered
- [ ] LED: initialized, color set
- [ ] Ultrasonic: initialized, distance reading
- [ ] Camera: initialized, capturing frames
- [ ] Emergency: not active
- [ ] Watchdog: running, no timeouts

---

## 📱 Remote Access

### From Another Computer

```bash
# Replace with your Pi's IP
mosquitto_pub -h 192.168.1.100 -t dev/motor -m '{"direction": "forward", "speed": 70}'
```

- [ ] Remote control working
- [ ] Commands received
- [ ] Status published

### Monitor from Remote

```bash
mosquitto_sub -h 192.168.1.100 -t '#' -v
```

- [ ] All topics visible
- [ ] Data streaming
- [ ] Real-time updates

---

## 🐛 Troubleshooting

### If Hardware Initialization Fails

```bash
# Check GPIO permissions
groups | grep gpio

# If not in gpio group
sudo usermod -a -G gpio $USER
sudo reboot
```

- [ ] In gpio group
- [ ] Rebooted if needed

### If MQTT Connection Fails

```bash
# Check broker
sudo systemctl status mosquitto

# Restart broker
sudo systemctl restart mosquitto

# Check firewall
sudo ufw allow 1883
```

- [ ] Broker running
- [ ] Port open

### If Motors Don't Move

- [ ] External power connected
- [ ] Common ground connected
- [ ] GPIO pins correct
- [ ] Motor driver enabled
- [ ] No emergency stop active

### If Camera Fails

```bash
# Enable camera
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot
```

- [ ] Camera enabled
- [ ] Rebooted

---

## ✅ Final Verification

### System Health

- [ ] All hardware components working
- [ ] MQTT communication stable
- [ ] Sensor data streaming
- [ ] Emergency stop functional
- [ ] Watchdog monitoring active
- [ ] No errors in logs

### Performance

- [ ] Motor response < 100ms
- [ ] Servo movement smooth
- [ ] Camera FPS ~30
- [ ] Sensor update ~10 Hz
- [ ] MQTT latency < 50ms

### Safety

- [ ] Emergency stop tested
- [ ] Obstacle detection working
- [ ] Watchdog timeout tested
- [ ] LED emergency indication working
- [ ] Commands blocked during emergency

---

## 🎉 Deployment Complete!

### System is Ready When:

✅ All hardware components initialized  
✅ MQTT communication working  
✅ Sensor data streaming  
✅ Remote control functional  
✅ Emergency systems tested  
✅ No errors in operation  

### Next Steps:

1. **Test thoroughly**: Run through all commands multiple times
2. **Monitor stability**: Let system run for extended period
3. **Document issues**: Note any problems for troubleshooting
4. **Integrate AI**: Add vision system when ready
5. **Build dashboard**: Create web interface for control

---

## 📝 Deployment Notes

### Date: _______________

### Deployed By: _______________

### Issues Encountered:
- 
- 
- 

### Resolutions:
- 
- 
- 

### Performance Notes:
- 
- 
- 

### Configuration Changes:
- 
- 
- 

---

## 🆘 Support

### Documentation
- `README.md` - Complete guide
- `QUICK_START.md` - Quick setup
- `ARCHITECTURE.md` - System architecture
- `SYSTEM_DIAGRAM.md` - Visual diagrams

### Logs
- Check terminal output for errors
- MQTT messages: `mosquitto_sub -h localhost -t '#' -v`
- System logs: `journalctl -u mosquitto`

### Common Commands

```bash
# Start system
python3 main.py

# Stop system
Ctrl+C

# Check status
mosquitto_pub -h localhost -t dev/commands -m '{"command": "status"}'

# Emergency stop
mosquitto_pub -h localhost -t dev/commands -m '{"command": "emergency_stop"}'

# Monitor everything
mosquitto_sub -h localhost -t '#' -v
```

---

**Deployment Checklist Complete!**  
**System Ready for Operation! 🚗💨**
