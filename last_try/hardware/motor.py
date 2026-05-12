"""
Simple Motor Control - L298N via PCA9685 PWM Driver
"""
from adafruit_pca9685 import PCA9685
import board
import busio

class Motor:
    def __init__(self):
        # PCA9685 Channels for L298N
        self.LEFT_IN1 = 2   # Channel 2
        self.LEFT_IN2 = 3   # Channel 3
        self.LEFT_EN = 6    # Channel 6 (PWM for speed)
        
        self.RIGHT_IN3 = 4  # Channel 4
        self.RIGHT_IN4 = 5  # Channel 5
        self.RIGHT_EN = 7   # Channel 7 (PWM for speed)
        
        self.pca = None
        
    def setup(self):
        """Initialize PCA9685"""
        try:
            # Initialize I2C
            i2c = busio.I2C(board.SCL, board.SDA)
            
            # Initialize PCA9685
            self.pca = PCA9685(i2c)
            self.pca.frequency = 1000  # 1000 Hz for motors
            
            # Start with motors off
            self.stop()
            
            print("[Motor] Initialized with PCA9685")
            return True
            
        except Exception as e:
            print(f"[Motor] Failed to initialize PCA9685: {e}")
            print("[Motor] Check I2C connection (SDA=GPIO2, SCL=GPIO3)")
            return False
    
    def _set_channel(self, channel, value):
        """Set PCA9685 channel (0=LOW, 1=HIGH)"""
        if value:
            self.pca.channels[channel].duty_cycle = 0xFFFF  # Full HIGH
        else:
            self.pca.channels[channel].duty_cycle = 0       # Full LOW
    
    def _set_speed(self, channel, speed):
        """Set PWM speed (0-100%)"""
        duty = int((speed / 100) * 0xFFFF)
        self.pca.channels[channel].duty_cycle = duty
    
    def forward(self, speed=70):
        """Move forward"""
        self._set_channel(self.LEFT_IN1, 1)
        self._set_channel(self.LEFT_IN2, 0)
        self._set_channel(self.RIGHT_IN3, 1)
        self._set_channel(self.RIGHT_IN4, 0)
        
        self._set_speed(self.LEFT_EN, speed)
        self._set_speed(self.RIGHT_EN, speed)
        print(f"[Motor] Forward at {speed}%")
    
    def backward(self, speed=70):
        """Move backward"""
        self._set_channel(self.LEFT_IN1, 0)
        self._set_channel(self.LEFT_IN2, 1)
        self._set_channel(self.RIGHT_IN3, 0)
        self._set_channel(self.RIGHT_IN4, 1)
        
        self._set_speed(self.LEFT_EN, speed)
        self._set_speed(self.RIGHT_EN, speed)
        print(f"[Motor] Backward at {speed}%")
    
    def left(self, speed=70):
        """Turn left"""
        self._set_channel(self.LEFT_IN1, 0)
        self._set_channel(self.LEFT_IN2, 1)
        self._set_channel(self.RIGHT_IN3, 1)
        self._set_channel(self.RIGHT_IN4, 0)
        
        self._set_speed(self.LEFT_EN, speed)
        self._set_speed(self.RIGHT_EN, speed)
        print(f"[Motor] Left at {speed}%")
    
    def right(self, speed=70):
        """Turn right"""
        self._set_channel(self.LEFT_IN1, 1)
        self._set_channel(self.LEFT_IN2, 0)
        self._set_channel(self.RIGHT_IN3, 0)
        self._set_channel(self.RIGHT_IN4, 1)
        
        self._set_speed(self.LEFT_EN, speed)
        self._set_speed(self.RIGHT_EN, speed)
        print(f"[Motor] Right at {speed}%")
    
    def stop(self):
        """Stop motors"""
        self._set_speed(self.LEFT_EN, 0)
        self._set_speed(self.RIGHT_EN, 0)
        print("[Motor] Stopped")
    
    def cleanup(self):
        """Cleanup"""
        self.stop()
        if self.pca:
            self.pca.deinit()
        print("[Motor] Cleanup done")
