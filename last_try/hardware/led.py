"""
Car Lights Control - 3 LEDs + Buzzer
- Left Forward LED
- Right Forward LED  
- Back Light LED
- Buzzer
"""
import RPi.GPIO as GPIO
import time
import threading

class LED:
    def __init__(self):
        # LED Pins (BCM numbering)
        self.LEFT_FORWARD = 16   # Left headlight
        self.RIGHT_FORWARD = 20  # Right headlight
        self.BACK_LIGHT = 21     # Back/brake light
        
        # Buzzer Pin
        self.BUZZER = 26         # Buzzer for alerts
        
        self.buzzer_thread = None
        self.buzzer_stop = threading.Event()
        
    def setup(self):
        """Initialize LEDs and buzzer"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup LED pins
        GPIO.setup(self.LEFT_FORWARD, GPIO.OUT)
        GPIO.setup(self.RIGHT_FORWARD, GPIO.OUT)
        GPIO.setup(self.BACK_LIGHT, GPIO.OUT)
        
        # Setup buzzer pin
        GPIO.setup(self.BUZZER, GPIO.OUT)
        
        # Turn off all
        GPIO.output(self.LEFT_FORWARD, GPIO.LOW)
        GPIO.output(self.RIGHT_FORWARD, GPIO.LOW)
        GPIO.output(self.BACK_LIGHT, GPIO.LOW)
        GPIO.output(self.BUZZER, GPIO.LOW)
        
        print("[LED] Initialized (3 LEDs + Buzzer)")
        return True
    
    def set_color(self, red, green, blue):
        """
        Compatibility method for existing code
        Maps RGB values to LED states:
        - Red (255,0,0) = Back light only (stopped/backward)
        - Green (0,255,0) = Forward lights (moving forward)
        - Blue (0,0,255) = Forward lights (AI tracking)
        - Yellow (255,255,0) = All lights (backward)
        - Magenta (255,0,255) = Forward lights (AI mode)
        - Cyan (0,255,255) = Forward lights (turning)
        - Off (0,0,0) = All off
        """
        # Turn off all first
        GPIO.output(self.LEFT_FORWARD, GPIO.LOW)
        GPIO.output(self.RIGHT_FORWARD, GPIO.LOW)
        GPIO.output(self.BACK_LIGHT, GPIO.LOW)
        
        # Red = Back light (stopped/error)
        if red > 200 and green < 50 and blue < 50:
            GPIO.output(self.BACK_LIGHT, GPIO.HIGH)
            print("[LED] Back light ON (stopped)")
        
        # Green = Forward lights (ready/moving)
        elif green > 200 and red < 50 and blue < 50:
            GPIO.output(self.LEFT_FORWARD, GPIO.HIGH)
            GPIO.output(self.RIGHT_FORWARD, GPIO.HIGH)
            print("[LED] Forward lights ON (ready)")
        
        # Blue = Forward lights (AI tracking)
        elif blue > 200 and red < 50 and green < 50:
            GPIO.output(self.LEFT_FORWARD, GPIO.HIGH)
            GPIO.output(self.RIGHT_FORWARD, GPIO.HIGH)
            print("[LED] Forward lights ON (AI forward)")
        
        # Yellow = All lights (backward)
        elif red > 200 and green > 200 and blue < 50:
            GPIO.output(self.LEFT_FORWARD, GPIO.HIGH)
            GPIO.output(self.RIGHT_FORWARD, GPIO.HIGH)
            GPIO.output(self.BACK_LIGHT, GPIO.HIGH)
            print("[LED] All lights ON (backward)")
        
        # Magenta = Forward lights (AI mode)
        elif red > 200 and blue > 200 and green < 50:
            GPIO.output(self.LEFT_FORWARD, GPIO.HIGH)
            GPIO.output(self.RIGHT_FORWARD, GPIO.HIGH)
            print("[LED] Forward lights ON (AI mode)")
        
        # Cyan = Forward lights (turning)
        elif green > 200 and blue > 200 and red < 50:
            GPIO.output(self.LEFT_FORWARD, GPIO.HIGH)
            GPIO.output(self.RIGHT_FORWARD, GPIO.HIGH)
            print("[LED] Forward lights ON (turning)")
        
        # Off
        else:
            print("[LED] All lights OFF")
    
    def forward_lights_on(self):
        """Turn on forward headlights"""
        GPIO.output(self.LEFT_FORWARD, GPIO.HIGH)
        GPIO.output(self.RIGHT_FORWARD, GPIO.HIGH)
        GPIO.output(self.BACK_LIGHT, GPIO.LOW)
        print("[LED] Forward lights ON")
    
    def back_light_on(self):
        """Turn on back light"""
        GPIO.output(self.LEFT_FORWARD, GPIO.LOW)
        GPIO.output(self.RIGHT_FORWARD, GPIO.LOW)
        GPIO.output(self.BACK_LIGHT, GPIO.HIGH)
        print("[LED] Back light ON")
    
    def all_lights_on(self):
        """Turn on all lights"""
        GPIO.output(self.LEFT_FORWARD, GPIO.HIGH)
        GPIO.output(self.RIGHT_FORWARD, GPIO.HIGH)
        GPIO.output(self.BACK_LIGHT, GPIO.HIGH)
        print("[LED] All lights ON")
    
    def all_lights_off(self):
        """Turn off all lights"""
        try:
            GPIO.output(self.LEFT_FORWARD, GPIO.LOW)
            GPIO.output(self.RIGHT_FORWARD, GPIO.LOW)
            GPIO.output(self.BACK_LIGHT, GPIO.LOW)
            print("[LED] All lights OFF")
        except RuntimeError:
            # GPIO already cleaned up
            pass
    
    def blink_forward(self, times=3, interval=0.2):
        """Blink forward lights"""
        for _ in range(times):
            GPIO.output(self.LEFT_FORWARD, GPIO.HIGH)
            GPIO.output(self.RIGHT_FORWARD, GPIO.HIGH)
            time.sleep(interval)
            GPIO.output(self.LEFT_FORWARD, GPIO.LOW)
            GPIO.output(self.RIGHT_FORWARD, GPIO.LOW)
            time.sleep(interval)
    
    def blink_back(self, times=3, interval=0.2):
        """Blink back light"""
        for _ in range(times):
            GPIO.output(self.BACK_LIGHT, GPIO.HIGH)
            time.sleep(interval)
            GPIO.output(self.BACK_LIGHT, GPIO.LOW)
            time.sleep(interval)
    
    def buzzer_beep(self, duration=0.1):
        """Single beep"""
        GPIO.output(self.BUZZER, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(self.BUZZER, GPIO.LOW)
        print("[Buzzer] Beep")
    
    def buzzer_beep_pattern(self, times=2, duration=0.1, interval=0.1):
        """Beep pattern"""
        for _ in range(times):
            GPIO.output(self.BUZZER, GPIO.HIGH)
            time.sleep(duration)
            GPIO.output(self.BUZZER, GPIO.LOW)
            time.sleep(interval)
        print(f"[Buzzer] Beep x{times}")
    
    def buzzer_alarm(self):
        """Start continuous alarm (runs in background)"""
        if self.buzzer_thread and self.buzzer_thread.is_alive():
            return  # Already running
        
        self.buzzer_stop.clear()
        self.buzzer_thread = threading.Thread(target=self._buzzer_alarm_loop, daemon=True)
        self.buzzer_thread.start()
        print("[Buzzer] Alarm started")
    
    def buzzer_stop_alarm(self):
        """Stop continuous alarm"""
        self.buzzer_stop.set()
        if self.buzzer_thread:
            self.buzzer_thread.join(timeout=1.0)
        try:
            GPIO.output(self.BUZZER, GPIO.LOW)
        except RuntimeError:
            # GPIO already cleaned up
            pass
        print("[Buzzer] Alarm stopped")
    
    def _buzzer_alarm_loop(self):
        """Internal alarm loop"""
        while not self.buzzer_stop.is_set():
            GPIO.output(self.BUZZER, GPIO.HIGH)
            time.sleep(0.2)
            GPIO.output(self.BUZZER, GPIO.LOW)
            time.sleep(0.2)
    
    def off(self):
        """Turn off all lights and buzzer"""
        self.all_lights_off()
        self.buzzer_stop_alarm()
    
    def cleanup(self):
        """Cleanup"""
        self.off()
        print("[LED] Cleanup done")
