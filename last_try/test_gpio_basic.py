#!/usr/bin/env python3
"""
Basic GPIO Test - Check if GPIO pins are working at all
"""
import RPi.GPIO as GPIO
import time

def test_single_pin(pin_number):
    """Test a single GPIO pin by toggling it"""
    print(f"\nTesting GPIO {pin_number}...")
    
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(pin_number, GPIO.OUT)
        
        print(f"  Setting HIGH...")
        GPIO.output(pin_number, GPIO.HIGH)
        time.sleep(1)
        
        print(f"  Setting LOW...")
        GPIO.output(pin_number, GPIO.LOW)
        time.sleep(1)
        
        print(f"  GPIO {pin_number} - OK ✓")
        return True
        
    except Exception as e:
        print(f"  GPIO {pin_number} - FAILED: {e}")
        return False
    finally:
        GPIO.cleanup(pin_number)

def test_all_pins():
    """Test all pins we're using"""
    print("=" * 50)
    print("GPIO Basic Test")
    print("=" * 50)
    
    pins = {
        'Motor Left Enable': 12,
        'Motor Left IN1': 23,
        'Motor Left IN2': 24,
        'Motor Right Enable': 13,
        'Motor Right IN3': 27,
        'Motor Right IN4': 22,
        'Servo Pan': 17,
        'Servo Tilt': 18,
        'LED Red': 16,
        'LED Green': 20,
        'LED Blue': 21,
        'Ultrasonic Trigger': 5,
    }
    
    results = {}
    for name, pin in pins.items():
        print(f"\n{name} (GPIO {pin}):")
        results[name] = test_single_pin(pin)
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print("RESULTS:")
    print("=" * 50)
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name}: {status}")
    
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        test_all_pins()
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        GPIO.cleanup()
