"""
Simple Motor Control - L298N Driver
"""
import RPi.GPIO as GPIO
import time

class Motor:
    def __init__(self):
        # L298N Pins (BCM numbering)
        self.LEFT_EN = 12
        self.LEFT_IN1 = 24
        self.LEFT_IN2 = 23
        
        self.RIGHT_EN = 13
        self.RIGHT_IN3 = 27
        self.RIGHT_IN4 = 22
        
        self.left_pwm = None
        self.right_pwm = None
        
    def setup(self):
        """Initialize GPIO and PWM"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup motor pins
        GPIO.setup(self.LEFT_EN, GPIO.OUT)
        GPIO.setup(self.LEFT_IN1, GPIO.OUT)
        GPIO.setup(self.LEFT_IN2, GPIO.OUT)
        GPIO.setup(self.RIGHT_EN, GPIO.OUT)
        GPIO.setup(self.RIGHT_IN3, GPIO.OUT)
        GPIO.setup(self.RIGHT_IN4, GPIO.OUT)
        
        # Setup PWM (100 Hz)
        self.left_pwm = GPIO.PWM(self.LEFT_EN, 100)
        self.right_pwm = GPIO.PWM(self.RIGHT_EN, 100)
        
        # Start PWM at 0%
        self.left_pwm.start(0)
        self.right_pwm.start(0)
        
        print("[Motor] Initialized")
        return True
    
    def forward(self, speed=70):
        """Move forward"""
        GPIO.output(self.LEFT_IN1, GPIO.HIGH)
        GPIO.output(self.LEFT_IN2, GPIO.LOW)
        GPIO.output(self.RIGHT_IN3, GPIO.HIGH)
        GPIO.output(self.RIGHT_IN4, GPIO.LOW)
        
        self.left_pwm.ChangeDutyCycle(speed)
        self.right_pwm.ChangeDutyCycle(speed)
        print(f"[Motor] Forward at {speed}%")
    
    def backward(self, speed=70):
        """Move backward"""
        GPIO.output(self.LEFT_IN1, GPIO.LOW)
        GPIO.output(self.LEFT_IN2, GPIO.HIGH)
        GPIO.output(self.RIGHT_IN3, GPIO.LOW)
        GPIO.output(self.RIGHT_IN4, GPIO.HIGH)
        
        self.left_pwm.ChangeDutyCycle(speed)
        self.right_pwm.ChangeDutyCycle(speed)
        print(f"[Motor] Backward at {speed}%")
    
    def left(self, speed=70):
        """Turn left"""
        GPIO.output(self.LEFT_IN1, GPIO.LOW)
        GPIO.output(self.LEFT_IN2, GPIO.HIGH)
        GPIO.output(self.RIGHT_IN3, GPIO.HIGH)
        GPIO.output(self.RIGHT_IN4, GPIO.LOW)
        
        self.left_pwm.ChangeDutyCycle(speed)
        self.right_pwm.ChangeDutyCycle(speed)
        print(f"[Motor] Left at {speed}%")
    
    def right(self, speed=70):
        """Turn right"""
        GPIO.output(self.LEFT_IN1, GPIO.HIGH)
        GPIO.output(self.LEFT_IN2, GPIO.LOW)
        GPIO.output(self.RIGHT_IN3, GPIO.LOW)
        GPIO.output(self.RIGHT_IN4, GPIO.HIGH)
        
        self.left_pwm.ChangeDutyCycle(speed)
        self.right_pwm.ChangeDutyCycle(speed)
        print(f"[Motor] Right at {speed}%")
    
    def stop(self):
        """Stop motors"""
        self.left_pwm.ChangeDutyCycle(0)
        self.right_pwm.ChangeDutyCycle(0)
        print("[Motor] Stopped")
    
    def cleanup(self):
        """Cleanup GPIO"""
        self.stop()
        self.left_pwm.stop()
        self.right_pwm.stop()
        GPIO.cleanup()
        print("[Motor] Cleanup done")
