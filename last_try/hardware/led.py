"""
Simple RGB LED Control
"""
import RPi.GPIO as GPIO

class LED:
    def __init__(self):
        # LED Pins (BCM)
        self.RED_PIN = 16
        self.GREEN_PIN = 20
        self.BLUE_PIN = 21
        
        self.red_pwm = None
        self.green_pwm = None
        self.blue_pwm = None
        
    def setup(self):
        """Initialize LED"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        GPIO.setup(self.RED_PIN, GPIO.OUT)
        GPIO.setup(self.GREEN_PIN, GPIO.OUT)
        GPIO.setup(self.BLUE_PIN, GPIO.OUT)
        
        # PWM for brightness control
        self.red_pwm = GPIO.PWM(self.RED_PIN, 1000)
        self.green_pwm = GPIO.PWM(self.GREEN_PIN, 1000)
        self.blue_pwm = GPIO.PWM(self.BLUE_PIN, 1000)
        
        self.red_pwm.start(0)
        self.green_pwm.start(0)
        self.blue_pwm.start(0)
        
        print("[LED] Initialized")
    
    def set_color(self, red, green, blue):
        """Set RGB color (0-255)"""
        r = (red / 255) * 100
        g = (green / 255) * 100
        b = (blue / 255) * 100
        
        self.red_pwm.ChangeDutyCycle(r)
        self.green_pwm.ChangeDutyCycle(g)
        self.blue_pwm.ChangeDutyCycle(b)
        print(f"[LED] Color: R={red} G={green} B={blue}")
    
    def off(self):
        """Turn off LED"""
        self.set_color(0, 0, 0)
    
    def cleanup(self):
        """Cleanup"""
        self.off()
        self.red_pwm.stop()
        self.green_pwm.stop()
        self.blue_pwm.stop()
        print("[LED] Cleanup done")
