"""
Simple Camera Control
"""
import cv2

class Camera:
    def __init__(self, device_id=0):
        self.device_id = device_id
        self.cap = None
        
    def setup(self):
        """Initialize camera"""
        self.cap = cv2.VideoCapture(self.device_id)
        
        if not self.cap.isOpened():
            print("[Camera] Failed to open camera")
            return False
        
        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("[Camera] Initialized")
        return True
    
    def get_frame(self):
        """Get a frame"""
        if self.cap is None:
            return None
        
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
    
    def cleanup(self):
        """Cleanup"""
        if self.cap:
            self.cap.release()
        print("[Camera] Cleanup done")
