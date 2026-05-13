"""
System State Manager
Shared state between MQTT control and AI control
"""
import threading
import queue
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class ControlMode(Enum):
    MANUAL = "manual"
    AI_FOLLOW = "ai_follow"

@dataclass
class MotorCommand:
    """Motor command from either MQTT or AI"""
    direction: str  # "forward", "backward", "left", "right", "stop"
    speed: int = 70
    source: str = "manual"  # "manual" or "ai"

@dataclass
class AIStatus:
    """AI tracking status"""
    tracking: Optional[str] = None  # Person name being tracked
    confidence: float = 0.0
    action: str = "idle"
    face_detected: bool = False
    body_detected: bool = False

class SystemState:
    """Thread-safe system state"""
    
    def __init__(self):
        # Current mode
        self._mode = ControlMode.MANUAL
        self._mode_lock = threading.Lock()
        
        # Motor command queue (AI → Motor controller)
        self.motor_queue = queue.Queue(maxsize=10)
        
        # AI status
        self._ai_status = AIStatus()
        self._ai_status_lock = threading.Lock()
        
        # Control flags
        self.emergency_stop = threading.Event()
        self.ai_active = threading.Event()
        self.shutdown = threading.Event()
        
        # Motor lock (prevent simultaneous control)
        self.motor_lock = threading.Lock()
    
    @property
    def mode(self) -> ControlMode:
        with self._mode_lock:
            return self._mode
    
    @mode.setter
    def mode(self, value: ControlMode):
        with self._mode_lock:
            old_mode = self._mode
            self._mode = value
            print(f"[SystemState] Mode changed: {old_mode.value} → {value.value}")
            
            if value == ControlMode.AI_FOLLOW:
                self.ai_active.set()
            else:
                self.ai_active.clear()
    
    def set_mode(self, mode_str: str):
        """Set mode from string"""
        if mode_str == "manual":
            self.mode = ControlMode.MANUAL
        elif mode_str == "ai_follow":
            self.mode = ControlMode.AI_FOLLOW
        else:
            print(f"[SystemState] Unknown mode: {mode_str}")
    
    def get_ai_status(self) -> AIStatus:
        with self._ai_status_lock:
            return AIStatus(
                tracking=self._ai_status.tracking,
                confidence=self._ai_status.confidence,
                action=self._ai_status.action,
                face_detected=self._ai_status.face_detected,
                body_detected=self._ai_status.body_detected
            )
    
    def update_ai_status(self, **kwargs):
        with self._ai_status_lock:
            for key, value in kwargs.items():
                if hasattr(self._ai_status, key):
                    setattr(self._ai_status, key, value)
    
    def send_motor_command(self, direction: str, speed: int = 70, source: str = "manual"):
        """Send motor command to queue"""
        try:
            cmd = MotorCommand(direction=direction, speed=speed, source=source)
            self.motor_queue.put_nowait(cmd)
        except queue.Full:
            # Drop command if queue is full
            pass
    
    def get_motor_command(self, timeout: float = 0.01) -> Optional[MotorCommand]:
        """Get motor command from queue"""
        try:
            return self.motor_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def trigger_emergency_stop(self):
        """Emergency stop - highest priority"""
        print("[SystemState] 🚨 EMERGENCY STOP TRIGGERED")
        self.emergency_stop.set()
        self.mode = ControlMode.MANUAL
        # Clear motor queue
        while not self.motor_queue.empty():
            try:
                self.motor_queue.get_nowait()
            except queue.Empty:
                break
    
    def reset_emergency_stop(self):
        """Reset emergency stop"""
        print("[SystemState] Emergency stop reset")
        self.emergency_stop.clear()
    
    def request_shutdown(self):
        """Request system shutdown"""
        print("[SystemState] Shutdown requested")
        self.shutdown.set()
        self.ai_active.clear()
