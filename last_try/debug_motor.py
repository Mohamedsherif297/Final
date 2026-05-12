#!/usr/bin/env python3
"""
Motor Debug Script - Test L298N step by step
"""
import RPi.GPIO as GPIO
import time

# L298N Pins
LEFT_EN = 12
LEFT_IN1 = 23
LEFT_IN2 = 24
RIGHT_EN = 13
RIGHT_IN3 = 27
RIGHT_IN4 = 22

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    GPIO.setup(LEFT_EN, GPIO.OUT)
    GPIO.setup(LEFT_IN1, GPIO.OUT)
    GPIO.setup(LEFT_IN2, GPIO.OUT)
    GPIO.setup(RIGHT_EN, GPIO.OUT)
    GPIO.setup(RIGHT_IN3, GPIO.OUT)
    GPIO.setup(RIGHT_IN4, GPIO.OUT)
    
    print("[Setup] GPIO configured")

def test_enable_pins():
    """Test if ENABLE pins work (should control speed)"""
    print("\n=== Testing ENABLE Pins (PWM) ===")
    
    # Set direction first
    GPIO.output(LEFT_IN1, GPIO.HIGH)
    GPIO.output(LEFT_IN2, GPIO.LOW)
    GPIO.output(RIGHT_IN3, GPIO.HIGH)
    GPIO.output(RIGHT_IN4, GPIO.LOW)
    
    print("Testing LEFT motor enable (GPIO 12)...")
    left_pwm = GPIO.PWM(LEFT_EN, 1000)
    left_pwm.start(0)
    
    for speed in [0, 25, 50, 75, 100]:
        print(f"  Speed: {speed}%")
        left_pwm.ChangeDutyCycle(speed)
        time.sleep(2)
    
    left_pwm.stop()
    print("  Left motor test done")
    
    print("\nTesting RIGHT motor enable (GPIO 13)...")
    right_pwm = GPIO.PWM(RIGHT_EN, 1000)
    right_pwm.start(0)
    
    for speed in [0, 25, 50, 75, 100]:
        print(f"  Speed: {speed}%")
        right_pwm.ChangeDutyCycle(speed)
        time.sleep(2)
    
    right_pwm.stop()
    print("  Right motor test done")

def test_direction_pins():
    """Test direction control pins"""
    print("\n=== Testing DIRECTION Pins ===")
    
    # Enable motors at 50%
    left_pwm = GPIO.PWM(LEFT_EN, 1000)
    right_pwm = GPIO.PWM(RIGHT_EN, 1000)
    left_pwm.start(50)
    right_pwm.start(50)
    
    print("\nLeft motor FORWARD (IN1=HIGH, IN2=LOW)...")
    GPIO.output(LEFT_IN1, GPIO.HIGH)
    GPIO.output(LEFT_IN2, GPIO.LOW)
    time.sleep(2)
    
    print("Left motor BACKWARD (IN1=LOW, IN2=HIGH)...")
    GPIO.output(LEFT_IN1, GPIO.LOW)
    GPIO.output(LEFT_IN2, GPIO.HIGH)
    time.sleep(2)
    
    print("Left motor STOP (both LOW)...")
    GPIO.output(LEFT_IN1, GPIO.LOW)
    GPIO.output(LEFT_IN2, GPIO.LOW)
    time.sleep(1)
    
    print("\nRight motor FORWARD (IN3=HIGH, IN4=LOW)...")
    GPIO.output(RIGHT_IN3, GPIO.HIGH)
    GPIO.output(RIGHT_IN4, GPIO.LOW)
    time.sleep(2)
    
    print("Right motor BACKWARD (IN3=LOW, IN4=HIGH)...")
    GPIO.output(RIGHT_IN3, GPIO.LOW)
    GPIO.output(RIGHT_IN4, GPIO.HIGH)
    time.sleep(2)
    
    print("Right motor STOP (both LOW)...")
    GPIO.output(RIGHT_IN3, GPIO.LOW)
    GPIO.output(RIGHT_IN4, GPIO.LOW)
    
    left_pwm.stop()
    right_pwm.stop()

def test_simple_on():
    """Simplest test - just turn on at 100%"""
    print("\n=== Simple ON Test ===")
    
    print("Setting all pins HIGH...")
    GPIO.output(LEFT_EN, GPIO.HIGH)
    GPIO.output(LEFT_IN1, GPIO.HIGH)
    GPIO.output(LEFT_IN2, GPIO.LOW)
    GPIO.output(RIGHT_EN, GPIO.HIGH)
    GPIO.output(RIGHT_IN3, GPIO.HIGH)
    GPIO.output(RIGHT_IN4, GPIO.LOW)
    
    print("Motors should be running at FULL SPEED for 3 seconds...")
    time.sleep(3)
    
    print("Turning OFF...")
    GPIO.output(LEFT_EN, GPIO.LOW)
    GPIO.output(RIGHT_EN, GPIO.LOW)

def main():
    print("=" * 60)
    print("L298N Motor Driver Debug")
    print("=" * 60)
    print("\nIMPORTANT CHECKS:")
    print("1. Is L298N powered? (12V/5V input)")
    print("2. Are motors connected to OUT1-OUT4?")
    print("3. Are jumpers on ENA/ENB removed? (for PWM control)")
    print("4. Is GND connected between Raspi and L298N?")
    print("\nPress Enter to start tests...")
    input()
    
    setup()
    
    while True:
        print("\n" + "=" * 60)
        print("Select test:")
        print("1. Simple ON test (full speed)")
        print("2. Test ENABLE pins (PWM speed control)")
        print("3. Test DIRECTION pins")
        print("4. Run all tests")
        print("0. Exit")
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            test_simple_on()
        elif choice == '2':
            test_enable_pins()
        elif choice == '3':
            test_direction_pins()
        elif choice == '4':
            test_simple_on()
            time.sleep(1)
            test_enable_pins()
            time.sleep(1)
            test_direction_pins()
        elif choice == '0':
            break
        else:
            print("Invalid choice")
    
    GPIO.cleanup()
    print("\nCleanup done")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted")
        GPIO.cleanup()
