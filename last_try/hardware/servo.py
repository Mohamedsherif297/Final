"""
Simple Servo Control
"""
import RPi.GPIO as GPIO

class Servo:
    def __init__(self):
        # Servo Pins (BCM)
        self.PAN_PIN = 17
        self.TILT_PIN = 18
        
        self.pan_pwm = None
        self.tilt_pwm = None
        
    def setup(self):
        """Initialize servos"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        GPIO.setup(self.PAN_PIN, GPIO.OUT)
        GPIO.setup(self.TILT_PIN, GPIO.OUT)
        
        # Servo PWM at 50Hz
        self.pan_pwm = GPIO.PWM(self.PAN_PIN, 50)
        self.tilt_pwm = GPIO.PWM(self.TILT_PIN, 50)
        
        self.pan_pwm.start(0)
        self.tilt_pwm.start(0)
        
        # Center position
        self.center()
        print("[Servo] Initialized")
    
    def set_angle(self, pan=None, tilt=None):
        """Set servo angles (0-180)"""
        if pan is not None:
            duty = 2 + (pan / 18)  # Convert angle to duty cycle
            self.pan_pwm.ChangeDutyCycle(duty)
            print(f"[Servo] Pan: {pan}°")
        
        if tilt is not None:
            duty = 2 + (tilt / 18)
            self.tilt_pwm.ChangeDutyCycle(duty)
            print(f"[Servo] Tilt: {tilt}°")
    
    def center(self):
        """Center both servos"""
        self.set_angle(pan=90, tilt=90)
        print("[Servo] Centered")
    
    def cleanup(self):
        """Cleanup"""
        self.pan_pwm.stop()
        self.tilt_pwm.stop()
        print("[Servo] Cleanup done")
