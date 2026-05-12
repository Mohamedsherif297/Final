#!/usr/bin/env python3
"""
Hardware Test Script
Test each component individually
"""
import sys
import time
sys.path.insert(0, 'hardware')

from motor import Motor
from servo import Servo
from led import LED
from ultrasonic import Ultrasonic
from camera import Camera

def test_motor():
    print("\n=== Testing Motor ===")
    motor = Motor()
    motor.setup()
    
    try:
        print("Forward...")
        motor.forward(50)
        time.sleep(2)
        
        print("Backward...")
        motor.backward(50)
        time.sleep(2)
        
        print("Left...")
        motor.left(50)
        time.sleep(2)
        
        print("Right...")
        motor.right(50)
        time.sleep(2)
        
        motor.stop()
        print("Motor test PASSED ✓")
        
    except Exception as e:
        print(f"Motor test FAILED: {e}")
    finally:
        motor.cleanup()

def test_servo():
    print("\n=== Testing Servo ===")
    servo = Servo()
    servo.setup()
    
    try:
        print("Center...")
        servo.center()
        time.sleep(1)
        
        print("Pan left...")
        servo.set_angle(pan=0)
        time.sleep(1)
        
        print("Pan right...")
        servo.set_angle(pan=180)
        time.sleep(1)
        
        print("Center...")
        servo.center()
        time.sleep(1)
        
        print("Tilt up...")
        servo.set_angle(tilt=45)
        time.sleep(1)
        
        print("Tilt down...")
        servo.set_angle(tilt=135)
        time.sleep(1)
        
        servo.center()
        print("Servo test PASSED ✓")
        
    except Exception as e:
        print(f"Servo test FAILED: {e}")
    finally:
        servo.cleanup()

def test_led():
    print("\n=== Testing LED ===")
    led = LED()
    led.setup()
    
    try:
        print("Red...")
        led.set_color(255, 0, 0)
        time.sleep(1)
        
        print("Green...")
        led.set_color(0, 255, 0)
        time.sleep(1)
        
        print("Blue...")
        led.set_color(0, 0, 255)
        time.sleep(1)
        
        print("White...")
        led.set_color(255, 255, 255)
        time.sleep(1)
        
        led.off()
        print("LED test PASSED ✓")
        
    except Exception as e:
        print(f"LED test FAILED: {e}")
    finally:
        led.cleanup()

def test_ultrasonic():
    print("\n=== Testing Ultrasonic ===")
    sensor = Ultrasonic()
    sensor.setup()
    
    try:
        print("Reading distance (5 times)...")
        for i in range(5):
            distance = sensor.get_distance()
            if distance:
                print(f"  {i+1}. Distance: {distance} cm")
            else:
                print(f"  {i+1}. No reading")
            time.sleep(0.5)
        
        print("Ultrasonic test PASSED ✓")
        
    except Exception as e:
        print(f"Ultrasonic test FAILED: {e}")
    finally:
        sensor.cleanup()

def test_camera():
    print("\n=== Testing Camera ===")
    camera = Camera()
    
    if not camera.setup():
        print("Camera test FAILED: Cannot open camera")
        return
    
    try:
        print("Capturing 3 frames...")
        for i in range(3):
            frame = camera.get_frame()
            if frame is not None:
                print(f"  {i+1}. Frame captured: {frame.shape}")
            else:
                print(f"  {i+1}. Failed to capture")
            time.sleep(0.5)
        
        print("Camera test PASSED ✓")
        
    except Exception as e:
        print(f"Camera test FAILED: {e}")
    finally:
        camera.cleanup()

def main():
    print("=" * 50)
    print("Hardware Component Test")
    print("=" * 50)
    
    while True:
        print("\nSelect test:")
        print("1. Motor")
        print("2. Servo")
        print("3. LED")
        print("4. Ultrasonic")
        print("5. Camera")
        print("6. All")
        print("0. Exit")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == '1':
            test_motor()
        elif choice == '2':
            test_servo()
        elif choice == '3':
            test_led()
        elif choice == '4':
            test_ultrasonic()
        elif choice == '5':
            test_camera()
        elif choice == '6':
            test_motor()
            test_servo()
            test_led()
            test_ultrasonic()
            test_camera()
        elif choice == '0':
            print("Exiting...")
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
