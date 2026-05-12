# Hardware Test Guide

## Overview

The `test_hardware.py` script tests all hardware components sequentially for 5 seconds each. This helps verify that all your connections are correct and working.

## What Gets Tested

1. **Motors** (20 seconds total)
   - Forward movement (5s)
   - Backward movement (5s)
   - Left turn (5s)
   - Right turn (5s)

2. **Servos** (25 seconds total)
   - Center position
   - Pan left (-90°) (5s)
   - Pan right (+90°) (5s)
   - Tilt up (+45°) (5s)
   - Tilt down (-45°) (5s)

3. **LED** (25 seconds total)
   - Red color (5s)
   - Green color (5s)
   - Blue color (5s)
   - Yellow color (5s)
   - Blink effect (5s)

4. **Ultrasonic Sensor** (5 seconds)
   - Continuous distance readings
   - Statistics (min, max, average)

5. **Camera** (5 seconds)
   - Frame capture test
   - FPS measurement

6. **Emergency Stop** (10 seconds)
   - Trigger test
   - Block verification
   - Reset test

**Total Test Duration**: ~90 seconds (1.5 minutes)

---

## Prerequisites

### Hardware Requirements
- ✅ All components connected as per `Docs/CONNECTIONS_GUIDE.md`
- ✅ External 12V power supply connected to motor driver
- ✅ Common ground between Raspberry Pi and motor driver
- ✅ Camera enabled (if using CSI camera)

### Software Requirements
- ✅ Running on Raspberry Pi
- ✅ Python 3.7+
- ✅ All dependencies installed (`pip install -r Raspi/requirements.txt`)
- ✅ GPIO permissions configured

### Safety Requirements
- ✅ Car has space to move (at least 1 meter clearance)
- ✅ Wheels are off the ground OR car is on a safe surface
- ✅ No obstacles in front of ultrasonic sensor
- ✅ You can reach the keyboard to press Ctrl+C if needed

---

## Usage

### Basic Usage

```bash
cd Final
python3 test_hardware.py
```

### Step-by-Step

1. **Navigate to Final folder**:
   ```bash
   cd /path/to/IOT/Final
   ```

2. **Run the test script**:
   ```bash
   python3 test_hardware.py
   ```

3. **Follow the prompts**:
   - Read the safety warnings
   - Wait 3 seconds for test to start
   - Watch each component test

4. **Observe the tests**:
   - Motors will move in all directions
   - Servos will pan and tilt
   - LED will change colors
   - Ultrasonic will show distance readings
   - Camera will capture frames

5. **Stop anytime**:
   - Press `Ctrl+C` to stop immediately
   - Script will cleanup gracefully

---

## Expected Output

### Successful Test

```
============================================================
  🔧 HARDWARE COMPONENT TEST SUITE
  Testing all components for 5 seconds each
============================================================

⚠️  SAFETY WARNINGS:
   - Ensure 12V external power is connected to motor driver
   - Keep hands away from moving parts
   - Press Ctrl+C to stop at any time
   - Make sure car has space to move

⏳ Starting tests in 3 seconds...

============================================================
  INITIALIZING HARDWARE MANAGER
============================================================
🔄 Initializing all hardware components...
✅ Hardware manager initialized successfully

============================================================
  TEST 1: MOTOR CONTROLLER
============================================================
🔧 Testing Motors: Moving FORWARD at 60% speed
✅ Forward movement complete
🔧 Testing Motors: Moving BACKWARD at 60% speed
✅ Backward movement complete
🔧 Testing Motors: Turning LEFT at 60% speed
✅ Left turn complete
🔧 Testing Motors: Turning RIGHT at 60% speed
✅ Right turn complete

✅ Motor tests complete

============================================================
  TEST 2: SERVO CONTROLLER
============================================================
🔧 Testing Servos: Moving to CENTER position
✅ Center position set
🔧 Testing Servos: Panning LEFT (-90°)
✅ Pan left complete
🔧 Testing Servos: Panning RIGHT (+90°)
✅ Pan right complete
🔧 Testing Servos: Tilting UP (+45°)
✅ Tilt up complete
🔧 Testing Servos: Tilting DOWN (-45°)
✅ Tilt down complete

✅ Servo tests complete

============================================================
  TEST 3: LED CONTROLLER
============================================================
🔧 Testing LED: Setting color to RED
✅ Red color complete
🔧 Testing LED: Setting color to GREEN
✅ Green color complete
🔧 Testing LED: Setting color to BLUE
✅ Blue color complete
🔧 Testing LED: Setting color to YELLOW
✅ Yellow color complete
🔧 Testing LED: Starting BLINK effect (white)
✅ Blink effect complete

✅ LED tests complete

============================================================
  TEST 4: ULTRASONIC SENSOR
============================================================
🔧 Testing Ultrasonic: Reading distance for 5 seconds
   📏 Move your hand in front of the sensor to see readings change
   📊 Statistics:
      Average: 45.3 cm
      Min: 12.5 cm
      Max: 78.2 cm
      Readings: 25/25
✅ Ultrasonic sensor test complete

============================================================
  TEST 5: CAMERA
============================================================
🔧 Testing Camera: Capturing frames for 5 seconds
   📊 Statistics:
      Total frames: 50
      Average FPS: 10.0
      Duration: 5.0s
✅ Camera test complete

============================================================
  TEST 6: EMERGENCY STOP SYSTEM
============================================================
🔧 Testing Emergency Stop: Testing emergency stop functionality
   🚗 Starting motor at 50% speed...
   🚨 Triggering EMERGENCY STOP...
   ✅ Emergency stop triggered
   ⚠️  All operations should now be blocked
   🔒 Testing if motor is blocked...
   ✅ Motor correctly blocked during emergency
   🔄 Resetting emergency stop...
   ✅ Emergency stop reset successfully
✅ Emergency stop test complete

============================================================
  TEST SUMMARY
============================================================
✅ All hardware tests completed successfully!

📋 Components tested:
   ✅ Motors (forward, backward, left, right)
   ✅ Servos (pan and tilt)
   ✅ LED (colors and effects)
   ✅ Ultrasonic sensor (distance readings)
   ✅ Camera (frame capture)
   ✅ Emergency stop system

🎉 Your hardware is ready to use!

============================================================
  CLEANUP
============================================================
🔄 Shutting down hardware manager...
✅ Hardware manager shutdown complete
```

---

## Troubleshooting

### Motors Not Moving

**Symptoms**: Motors don't move during test

**Possible Causes**:
1. External 12V power not connected
2. Common ground not connected
3. GPIO pins incorrect
4. Motor driver not enabled

**Solutions**:
```bash
# Check GPIO pins
cat Raspi/config/hardware/gpio_config.yaml

# Verify connections match CONNECTIONS_GUIDE.md
cat Docs/CONNECTIONS_GUIDE.md

# Check motor driver power LED is on
```

### Servos Not Responding

**Symptoms**: Servos don't move or jitter

**Possible Causes**:
1. 5V power not connected
2. Signal wire on wrong GPIO
3. Servo drawing too much current

**Solutions**:
```bash
# Check servo config
cat Raspi/config/hardware/servo_config.yaml

# Verify GPIO 17 (pan) and GPIO 18 (tilt)
# Use external 5V power if servos jitter
```

### LED Not Lighting

**Symptoms**: LED stays off or wrong colors

**Possible Causes**:
1. Missing 220Ω resistors
2. Wrong GPIO pins
3. LED polarity reversed
4. Common cathode not grounded

**Solutions**:
```bash
# Check LED GPIO pins (16, 20, 21)
# Verify common cathode to GND
# Check resistors are in place
```

### Ultrasonic Sensor Not Reading

**Symptoms**: "Out of range" or no readings

**Possible Causes**:
1. Sensor not powered (5V)
2. Wrong GPIO pins
3. Obstacle too close/far
4. Sensor facing wrong direction

**Solutions**:
```bash
# Check GPIO 5 (trigger) and GPIO 6 (echo)
# Ensure sensor has clear view
# Test range: 2cm - 400cm
```

### Camera Not Working

**Symptoms**: "Frame capture failed" messages

**Possible Causes**:
1. Camera not enabled
2. Camera not connected
3. Wrong camera type in config

**Solutions**:
```bash
# Enable camera
sudo raspi-config
# Interface Options → Camera → Enable

# Check camera
vcgencmd get_camera

# Reboot
sudo reboot
```

### Permission Denied Errors

**Symptoms**: "Permission denied" when accessing GPIO

**Solutions**:
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Add to video group (for camera)
sudo usermod -a -G video $USER

# Reboot
sudo reboot
```

### Import Errors

**Symptoms**: "ModuleNotFoundError" or import errors

**Solutions**:
```bash
# Install dependencies
cd Raspi
pip3 install -r requirements.txt

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Advanced Usage

### Test Individual Components

You can modify the script to test only specific components by commenting out tests in the `run_all_tests()` method:

```python
# In test_hardware.py, comment out tests you don't want:
def run_all_tests(self):
    # ...
    self.test_motors()      # Comment this to skip motors
    # self.test_servos()    # Commented = skipped
    self.test_led()
    # ...
```

### Adjust Test Duration

Change the test duration at the top of the class:

```python
def __init__(self):
    self.test_duration = 10  # Change from 5 to 10 seconds
```

### Run Without Camera

If you don't have a camera connected, comment out the camera test:

```python
# self.test_camera()  # Skip camera test
```

---

## Safety Notes

⚠️ **IMPORTANT SAFETY WARNINGS**:

1. **External Power**: ALWAYS use external 12V power for motors. NEVER power motors from Raspberry Pi.

2. **Common Ground**: MUST connect common ground between Pi and motor driver. Missing this can damage components.

3. **Moving Parts**: Keep hands, wires, and objects away from wheels and servos during testing.

4. **Emergency Stop**: Press `Ctrl+C` at any time to stop all tests immediately.

5. **Space**: Ensure car has at least 1 meter of clearance in all directions.

6. **Supervision**: Never leave the test running unattended.

7. **First Time**: For first-time testing, consider elevating the car so wheels don't touch the ground.

---

## Next Steps

After successful testing:

1. ✅ All components verified working
2. ✅ Ready to run main system: `python3 Raspi/main.py`
3. ✅ Ready to use laptop controller: `python3 Laptop/mqtt_gui_controller.py`
4. ✅ Ready for MQTT control via broker

---

## Quick Reference

### Test Script Location
```
Final/test_hardware.py
```

### Run Command
```bash
python3 test_hardware.py
```

### Stop Test
```
Ctrl+C
```

### Test Duration
- Per component: 5 seconds
- Total: ~90 seconds

### Components Tested
- Motors ✓
- Servos ✓
- LED ✓
- Ultrasonic ✓
- Camera ✓
- Emergency Stop ✓

---

**Last Updated**: Hardware Test Script Created  
**Status**: Ready for Testing  
**Duration**: ~90 seconds total
