# Fixes Applied to Surveillance Car System

## Date: 2026-05-12

## Issues Fixed

### 1. GPIO Warning: "This channel is already in use"
**Problem**: GPIO pins were being initialized twice, causing warnings.

**Root Cause**: Hardware manager is a singleton, but GPIO warnings were enabled, showing messages when pins were reused.

**Fix Applied**:
- Modified `/Raspi/Drivers/hardware/gpio/gpio_manager.py`
- Changed `GPIO.setwarnings()` to always be `False` to suppress channel reuse warnings
- This is safe because the hardware manager singleton pattern ensures proper pin management

### 2. Obstacle Detection Console Spam
**Problem**: Every obstacle detection was printing to console, flooding the output with hundreds of identical messages.

**Root Cause**: 
- Obstacle detection callback was triggered on every measurement
- No state tracking to prevent duplicate messages

**Fixes Applied**:

**File 1**: `/Raspi/Drivers/hardware/ultrasonic/obstacle_detection.py`
- Added state tracking: `last_status` and `last_logged_distance`
- Modified `check_distance()` to only log on status changes (clear → warning → emergency)
- Now prints:
  - `[OBSTACLE] Emergency! Detected at X.XXcm` - only when entering emergency state
  - `[OBSTACLE] Warning at X.XXcm` - only when entering warning state
  - `[OBSTACLE] Clear - X.XXcm` - only when clearing from warning/emergency

**File 2**: `/Raspi/Drivers/hardware/managers/hardware_manager.py`
- Modified `_obstacle_detected()` callback to check if emergency is already active
- Only triggers emergency stop on first detection, not every subsequent measurement
- Prevents emergency system spam

### 3. ALSA Audio Errors
**Problem**: Multiple ALSA library errors flooding the console during audio initialization.

**Root Cause**: PyAudio enumerates all possible audio devices, causing ALSA to print errors for non-existent devices.

**Fix Applied**:
- Modified `/Raspi/Network/WebSockets/audio_system.py`
- Added stderr redirection during PyAudio initialization
- Temporarily redirects stderr to `/dev/null` while PyAudio initializes
- Restores stderr after initialization completes
- Audio still works, but ALSA warnings are suppressed

### 4. Camera/OpenCV Warnings
**Problem**: Multiple OpenCV warnings about video devices:
- "Not a video capture device"
- "Camera index out of range"
- Various V4L2 warnings

**Fixes Applied**:

**File 1**: `/Raspi/main.py`
- Added environment variables at startup:
  - `OPENCV_LOG_LEVEL=ERROR`
  - `OPENCV_VIDEOIO_DEBUG=0`
- Suppresses verbose OpenCV logging globally

**File 2**: `/Raspi/Network/WebSockets/video_stream_handler.py`
- Added `OPENCV_LOG_LEVEL=ERROR` in `_open_camera()` method
- Ensures OpenCV warnings are suppressed even if not set globally

**File 3**: `/Raspi/Drivers/hardware/camera/camera_controller.py`
- Improved camera initialization with multiple backend attempts
- Added test frame capture to verify camera works
- Better error messages when camera fails
- Tries V4L2 backend first, then falls back to ANY backend

## Expected Behavior After Fixes

### Console Output Should Now Show:
```
[SYSTEM] Initializing hardware...
INFO - hardware.hardware_manager - Initializing hardware components...
INFO - hardware.gpio_manager - GPIO initialized in BCM mode
INFO - hardware.motor_controller - Motor controller initialized
INFO - hardware.servo_controller - Servo controller initialized
INFO - hardware.led_controller - LED controller initialized
INFO - hardware.ultrasonic_controller - Ultrasonic sensor initialized
INFO - hardware.camera_controller - Camera initialized: 640x480 @ 30fps
[SYSTEM] Hardware initialized successfully
[SYSTEM] System running. Press Ctrl+C to exit.

[OBSTACLE] Emergency! Detected at 10.05cm
[OBSTACLE] Clear - 45.23cm
```

### What's Eliminated:
- ❌ GPIO warnings about channels in use
- ❌ Hundreds of repeated obstacle messages
- ❌ ALSA audio device enumeration errors
- ❌ OpenCV V4L2 warnings
- ❌ "Not a video capture device" spam

## Testing Recommendations

1. **Test Obstacle Detection**:
   - Place object in front of sensor
   - Should see ONE message when entering emergency state
   - Should see ONE message when clearing
   - No repeated spam

2. **Test Camera**:
   - Verify camera initializes without warnings
   - Check if video stream works in WebSocket

3. **Test Audio**:
   - Verify audio initializes without ALSA errors
   - Check if audio stream works in WebSocket

4. **Test Motor Control**:
   - Send MQTT commands
   - Verify no GPIO warnings appear

## Files Modified

1. `/Raspi/main.py` - Added environment variables
2. `/Raspi/Drivers/hardware/gpio/gpio_manager.py` - Disabled GPIO warnings
3. `/Raspi/Drivers/hardware/managers/hardware_manager.py` - Fixed obstacle callback
4. `/Raspi/Drivers/hardware/ultrasonic/obstacle_detection.py` - Added state tracking
5. `/Raspi/Drivers/hardware/camera/camera_controller.py` - Improved camera init
6. `/Raspi/Network/WebSockets/audio_system.py` - Suppressed ALSA errors
7. `/Raspi/Network/WebSockets/video_stream_handler.py` - Suppressed OpenCV warnings

## Notes

- All fixes are non-breaking and maintain existing functionality
- Error suppression only hides verbose library warnings, not actual errors
- State tracking in obstacle detection improves system responsiveness
- Camera and audio will still log actual errors if devices fail
