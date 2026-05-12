"""
Simple Servo Control - Using PCA9685 PWM Driver
"""
from adafruit_servokit import ServoKit

class Servo:
    def __init__(self):
        # PCA9685 channels
        self.PAN_CHANNEL = 0
        self.TILT_CHANNEL = 1
        
        self.kit = None
        
    def setup(self):
        """Initialize PCA9685 servo driver"""
        try:
            # Initialize PCA9685 (16 channels, I2C address 0x40)
            self.kit = ServoKit(channels=16)
            
            # Set servo range (adjust if needed)
            self.kit.servo[self.PAN_CHANNEL].actuation_range = 180
            self.kit.servo[self.TILT_CHANNEL].actuation_range = 180
            
            # Center position
            self.center()
            print("[Servo] Initialized with PCA9685")
            return True
            
        except Exception as e:
            print(f"[Servo] Failed to initialize PCA9685: {e}")
            print("[Servo] Check I2C connection (SDA=GPIO2, SCL=GPIO3)")
            return False
    
    def set_angle(self, pan=None, tilt=None):
        """Set servo angles (0-180)"""
        if self.kit is None:
            print("[Servo] Not initialized")
            return
        
        try:
            if pan is not None:
                self.kit.servo[self.PAN_CHANNEL].angle = pan
                print(f"[Servo] Pan: {pan}°")
            
            if tilt is not None:
                self.kit.servo[self.TILT_CHANNEL].angle = tilt
                print(f"[Servo] Tilt: {tilt}°")
                
        except Exception as e:
            print(f"[Servo] Error setting angle: {e}")
    
    def center(self):
        """Center both servos"""
        self.set_angle(pan=90, tilt=90)
        print("[Servo] Centered")
    
    def cleanup(self):
        """Cleanup"""
        # PCA9685 doesn't need cleanup
        print("[Servo] Cleanup done")
