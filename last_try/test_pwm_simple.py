#!/usr/bin/env python3
"""
Simple PWM Test - Check if PWM actually controls motor speed
"""
import RPi.GPIO as GPIO
import time

# Pins
LEFT_EN = 12
LEFT_IN1 = 24
LEFT_IN2 = 23

def test_pwm():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup
    GPIO.setup(LEFT_EN, GPIO.OUT)
    GPIO.setup(LEFT_IN1, GPIO.OUT)
    GPIO.setup(LEFT_IN2, GPIO.OUT)
    
    # Set direction FIRST (before PWM)
    GPIO.output(LEFT_IN1, GPIO.HIGH)
    GPIO.output(LEFT_IN2, GPIO.LOW)
    print("Direction set: FORWARD")
    
    # Create PWM
    pwm = GPIO.PWM(LEFT_EN, 100)  # 100 Hz
    pwm.start(0)
    print("PWM started at 0%")
    time.sleep(1)
    
    # Test different speeds
    for speed in [30, 50, 70, 100]:
        print(f"\nSetting speed to {speed}%...")
        pwm.ChangeDutyCycle(speed)
        print(f"Motor should be running at {speed}% speed")
        time.sleep(3)
    
    print("\nStopping...")
    pwm.ChangeDutyCycle(0)
    time.sleep(1)
    
    pwm.stop()
    GPIO.cleanup()
    print("Test complete")

if __name__ == "__main__":
    print("=" * 50)
    print("PWM Speed Control Test")
    print("=" * 50)
    print("\nMake sure:")
    print("1. Jumpers are REMOVED from ENA/ENB")
    print("2. GPIO 12 is connected to ENA")
    print("3. Motor is connected to OUT1/OUT2")
    print("\nPress Enter to start...")
    input()
    
    try:
        test_pwm()
    except KeyboardInterrupt:
        print("\n\nInterrupted")
        GPIO.cleanup()
