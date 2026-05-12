"""
Simple Ultrasonic Sensor (HC-SR04)
"""
import RPi.GPIO as GPIO
import time

class Ultrasonic:
    def __init__(self):
        # Ultrasonic Pins (BCM)
        self.TRIGGER = 5
        self.ECHO = 6
        
    def setup(self):
        """Initialize ultrasonic sensor"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        GPIO.setup(self.TRIGGER, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)
        
        GPIO.output(self.TRIGGER, GPIO.LOW)
        time.sleep(0.1)
        
        print("[Ultrasonic] Initialized")
    
    def get_distance(self):
        """Get distance in cm"""
        # Send trigger pulse
        GPIO.output(self.TRIGGER, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.TRIGGER, GPIO.LOW)
        
        # Wait for echo
        timeout = time.time() + 0.1
        while GPIO.input(self.ECHO) == 0:
            pulse_start = time.time()
            if pulse_start > timeout:
                return None
        
        timeout = time.time() + 0.1
        while GPIO.input(self.ECHO) == 1:
            pulse_end = time.time()
            if pulse_end > timeout:
                return None
        
        # Calculate distance
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        
        if 2 <= distance <= 400:
            return distance
        return None
    
    def cleanup(self):
        """Cleanup"""
        GPIO.output(self.TRIGGER, GPIO.LOW)
        print("[Ultrasonic] Cleanup done")
