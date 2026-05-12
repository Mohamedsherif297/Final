#!/usr/bin/env python3
"""
Check if we have the right permissions to access GPIO
"""
import os
import sys

def check_permissions():
    print("=" * 50)
    print("Permission Check")
    print("=" * 50)
    
    # Check if running as root
    if os.geteuid() == 0:
        print("✓ Running as root (sudo)")
    else:
        print("✗ NOT running as root")
        print("\n  You need to run with sudo:")
        print("  sudo python3 test_hardware.py")
        return False
    
    # Check if RPi.GPIO is installed
    try:
        import RPi.GPIO as GPIO
        print("✓ RPi.GPIO is installed")
    except ImportError:
        print("✗ RPi.GPIO is NOT installed")
        print("\n  Install it with:")
        print("  sudo apt-get install python3-rpi.gpio")
        return False
    
    # Check if /dev/gpiomem exists
    if os.path.exists('/dev/gpiomem'):
        print("✓ /dev/gpiomem exists")
    else:
        print("✗ /dev/gpiomem does NOT exist")
        print("  This might not be a Raspberry Pi!")
        return False
    
    # Check if we can access GPIO
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(16, GPIO.OUT)  # Test LED red pin
        GPIO.output(16, GPIO.HIGH)
        GPIO.output(16, GPIO.LOW)
        GPIO.cleanup()
        print("✓ Can access GPIO")
    except Exception as e:
        print(f"✗ Cannot access GPIO: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("All checks PASSED ✓")
    print("=" * 50)
    return True

if __name__ == "__main__":
    if check_permissions():
        print("\nYou can now run the hardware tests!")
    else:
        print("\nFix the issues above before testing hardware")
        sys.exit(1)
