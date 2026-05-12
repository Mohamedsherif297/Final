SURVEILLANCE CAR - SIMPLE BUILD
================================

STEP 1: TEST HARDWARE
---------------------
Run the hardware test to verify all connections:

    cd /Users/user/IOT\ /Final/last_try
    python3 test_hardware.py

Test each component:
- Motor: Should move forward, backward, left, right
- Servo: Should pan and tilt
- LED: Should show red, green, blue, white
- Ultrasonic: Should read distance
- Camera: Should capture frames

If any test fails, check your wiring!


STEP 2: KEYBOARD CONTROL
-------------------------
Control the car with keyboard:

    python3 keyboard_control.py

Controls:
    w = Forward
    s = Backward  
    a = Left
    d = Right
    x = Stop
    q = Quit


STEP 3: MQTT CONTROL (Next)
----------------------------
After hardware works, we'll add MQTT control with HiveMQ


STEP 4: WEBSOCKET STREAMING (Final)
------------------------------------
After MQTT works, we'll add WebSocket video streaming


PIN CONNECTIONS (L298N)
------------------------
Motor Left:
  Enable: GPIO 12
  IN1: GPIO 23
  IN2: GPIO 24

Motor Right:
  Enable: GPIO 13
  IN3: GPIO 27
  IN4: GPIO 22

Servo:
  Pan: GPIO 17
  Tilt: GPIO 18

LED:
  Red: GPIO 16
  Green: GPIO 20
  Blue: GPIO 21

Ultrasonic:
  Trigger: GPIO 5
  Echo: GPIO 6

Camera:
  USB Webcam (auto-detected)
