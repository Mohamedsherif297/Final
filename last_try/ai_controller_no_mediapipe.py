"""
AI Controller - No MediaPipe Version
Uses face_recognition for both detection and recognition
Works with Python 3.13
"""
import os
import pickle
import time
import threading
import cv2
import numpy as np

try:
    import face_recognition
    FACE_RECOG_AVAILABLE = True
    print("[AI] face_recognition loaded successfully")
except ImportError:
    FACE_RECOG_AVAILABLE = False
    print("[AI] Warning: face_recognition not installed")

from system_state import SystemState

# ========== AI Configuration ==========
# ⚠️ EASY REVERT: Change USE_HIGH_RES to False to revert to 640x480
USE_HIGH_RES = True  # Set to False to use old 640x480 resolution

if USE_HIGH_RES:
    FRAME_WIDTH = 1280
    FRAME_HEIGHT = 720
    PROCESS_EVERY_N_FRAMES = 3  # Skip more frames for performance
    DETECTION_SCALE = 0.4  # Resize to 40% for detection (512x288)
else:
    # Original settings (FALLBACK)
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    PROCESS_EVERY_N_FRAMES = 2
    DETECTION_SCALE = 0.5  # Resize to 50% for detection (320x240)

# ⚠️ EASY REVERT: Change USE_DISTANCE_CONTROL to False to use old area-based logic
USE_DISTANCE_CONTROL = True  # Set to False to use old face_area logic

# Camera Configuration
CAMERA_TILT_ANGLE = 50  # degrees upward (optimal for 0.5-2m range)

# Distance Control Thresholds (NEW - used if USE_DISTANCE_CONTROL = True)
TARGET_DISTANCE_M = 1.0  # Hover at 1 meter
DISTANCE_TOLERANCE_M = 0.2  # ±0.2m acceptable
TOO_CLOSE_M = 0.7  # Back up if closer than this
TOO_FAR_M = 2.0  # Give up tracking if farther than this
MIN_FACE_SIZE_PX = 50  # Minimum face width to attempt tracking

# Area Control Thresholds (OLD - used if USE_DISTANCE_CONTROL = False)
CLOSE_AREA = 0.04  # 4% of frame (was 0.25) - stops at ~1m with high res
TOO_CLOSE_AREA = 0.06  # 6% of frame - backup threshold
MIN_FACE_AREA = 0.008  # 0.8% minimum to track

# Recognition Thresholds
DEADZONE_PX = 80  # Horizontal deadzone for centering
NO_FACE_TIMEOUT_S = 2.0  # Keep tracking for 2s after losing face
RECOG_TOLERANCE = 0.5  # Relaxed (was 0.4) - distance threshold for match
MIN_CONFIDENCE_TO_ACT = 0.45  # Relaxed (was 0.40) - minimum confidence to act

# Paths
KNOWN_FACES_DIR = "pi_minimal/known_faces/images"
ENCODINGS_FILE = "pi_minimal/known_faces/encodings.pkl"

class AIController:
    """AI-based person following controller using face_recognition only"""
    
    def __init__(self, state: SystemState, speed: int = 60):
        self.state = state
        self.speed = speed
        self.running = False
        self.thread = None
        
        # Known faces
        self.known_encodings = []
        self.known_names = []
        
        # Tracking state
        self.last_face_seen = 0.0
        self.tracking_name = None
        self.frame_counter = 0
        
        # Frame sharing
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
        # Debug info for overlay
        self.debug_info = {
            "distance": 0.0,
            "face_size": (0, 0),
            "confidence": 0.0
        }
    
    def load_known_faces(self):
        """Load known faces from pre-computed encodings or generate if needed"""
        if not FACE_RECOG_AVAILABLE:
            print("[AI] face_recognition not available, skipping face loading")
            return False
        
        # Try to load from pre-computed encodings file
        if os.path.exists(ENCODINGS_FILE):
            try:
                start_time = time.time()
                print(f"[AI] Loading pre-computed encodings from {ENCODINGS_FILE}")
                
                with open(ENCODINGS_FILE, "rb") as f:
                    data = pickle.load(f)
                
                self.known_encodings = data["encodings"]
                self.known_names = data["names"]
                
                load_time = time.time() - start_time
                print(f"[AI] Loaded {len(self.known_encodings)} encodings in {load_time:.2f}s")
                print(f"[AI] Generated at: {data.get('generated_at', 'Unknown')}")
                
                # Show breakdown by person
                unique_names = set(self.known_names)
                for name in sorted(unique_names):
                    count = sum(1 for n in self.known_names if n == name)
                    print(f"[AI]   - {name}: {count} encodings")
                
                return True
            
            except Exception as e:
                print(f"[AI] Error loading encodings file: {e}")
                print("[AI] Falling back to generating encodings from images...")
        
        else:
            print(f"[AI] Encodings file not found: {ENCODINGS_FILE}")
            print("[AI] Generating encodings from images (this may take a while)...")
        
        # Fallback: Generate encodings from images
        if not os.path.isdir(KNOWN_FACES_DIR):
            print(f"[AI] Known faces directory not found: {KNOWN_FACES_DIR}")
            print("[AI] Please run: python3 collect_dataset.py YourName")
            return False
        
        start_time = time.time()
        count = 0
        
        for person in os.listdir(KNOWN_FACES_DIR):
            person_dir = os.path.join(KNOWN_FACES_DIR, person)
            if not os.path.isdir(person_dir):
                continue
            
            for fname in os.listdir(person_dir):
                if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue
                
                path = os.path.join(person_dir, fname)
                try:
                    image = face_recognition.load_image_file(path)
                    encs = face_recognition.face_encodings(image)
                    if encs:
                        self.known_encodings.append(encs[0])
                        self.known_names.append(person)
                        count += 1
                except Exception as e:
                    print(f"[AI] Error loading {path}: {e}")
        
        load_time = time.time() - start_time
        print(f"[AI] Generated {count} encodings in {load_time:.2f}s")
        print(f"[AI] Tip: Run 'python3 generate_encodings.py' to pre-compute encodings for faster startup")
        
        return count > 0
    
    def set_frame(self, frame):
        """Set current frame from camera (called by main thread)"""
        with self.frame_lock:
            self.current_frame = frame.copy() if frame is not None else None
    
    def get_frame(self):
        """Get current frame for processing"""
        with self.frame_lock:
            return self.current_frame.copy() if self.current_frame is not None else None
    
    def get_debug_info(self):
        """Get current debug information"""
        return self.debug_info.copy()
    
    def estimate_distance_from_face_size(self, face_width_pixels):
        """
        Estimate horizontal distance based on face size in pixels
        
        Assumptions:
        - Average face width: 15 cm
        - Camera FOV: ~60 degrees (typical webcam)
        - Calibrated for 1280x720 resolution
        
        Returns: estimated horizontal distance in meters
        """
        if not USE_DISTANCE_CONTROL:
            return None
        
        # Empirical calibration (adjust based on your actual camera)
        # At 1280px width with 60° FOV:
        # - 1m distance → ~120px face width
        # - 2m distance → ~60px face width
        # - 0.5m distance → ~240px face width
        
        if USE_HIGH_RES:
            # High resolution calibration (1280x720)
            if face_width_pixels < 50:
                return 2.5  # Too far or not a face
            elif face_width_pixels < 70:
                return 2.0  # Far
            elif face_width_pixels < 100:
                return 1.5  # Getting there
            elif face_width_pixels < 130:
                return 1.0  # TARGET - perfect distance
            elif face_width_pixels < 170:
                return 0.8  # Getting close
            elif face_width_pixels < 220:
                return 0.6  # Close
            else:
                return 0.4  # Too close
        else:
            # Low resolution calibration (640x480)
            if face_width_pixels < 25:
                return 2.5
            elif face_width_pixels < 35:
                return 2.0
            elif face_width_pixels < 50:
                return 1.5
            elif face_width_pixels < 65:
                return 1.0  # TARGET
            elif face_width_pixels < 85:
                return 0.8
            elif face_width_pixels < 110:
                return 0.6
            else:
                return 0.4
    
    def decide_action_distance_based(self, target_center_x, face_width_pixels, estimated_distance):
        """
        NEW: Distance-based control logic with hover state
        
        Returns action: stop, forward, backward, left, right
        """
        frame_center_x = FRAME_WIDTH // 2
        
        # Check if face is too small/far
        if face_width_pixels < MIN_FACE_SIZE_PX:
            print(f"[AI] Face too small ({face_width_pixels}px), giving up")
            return "stop"
        
        # Check if too far
        if estimated_distance > TOO_FAR_M:
            print(f"[AI] Too far ({estimated_distance:.1f}m), giving up")
            return "stop"
        
        # Too close - back up!
        if estimated_distance < TOO_CLOSE_M:
            print(f"[AI] Too close ({estimated_distance:.1f}m), backing up")
            return "backward"
        
        # Perfect distance - maintain position (HOVER STATE)
        if abs(estimated_distance - TARGET_DISTANCE_M) <= DISTANCE_TOLERANCE_M:
            # Only adjust horizontal position
            if target_center_x < frame_center_x - DEADZONE_PX:
                print(f"[AI] At target distance ({estimated_distance:.1f}m), turning left")
                return "left"
            elif target_center_x > frame_center_x + DEADZONE_PX:
                print(f"[AI] At target distance ({estimated_distance:.1f}m), turning right")
                return "right"
            else:
                print(f"[AI] At target distance ({estimated_distance:.1f}m), HOVERING")
                return "stop"  # HOVER - perfect position!
        
        # Too far - move forward
        if estimated_distance > TARGET_DISTANCE_M + DISTANCE_TOLERANCE_M:
            # Turn while moving forward
            if target_center_x < frame_center_x - DEADZONE_PX:
                print(f"[AI] Too far ({estimated_distance:.1f}m), forward+left")
                return "left"  # Will turn left while moving
            elif target_center_x > frame_center_x + DEADZONE_PX:
                print(f"[AI] Too far ({estimated_distance:.1f}m), forward+right")
                return "right"  # Will turn right while moving
            else:
                print(f"[AI] Too far ({estimated_distance:.1f}m), moving forward")
                return "forward"
        
        # Slightly too close - just turn to maintain center
        if estimated_distance < TARGET_DISTANCE_M - DISTANCE_TOLERANCE_M:
            if target_center_x < frame_center_x - DEADZONE_PX:
                return "left"
            elif target_center_x > frame_center_x + DEADZONE_PX:
                return "right"
            else:
                return "stop"
        
        # Default - stop
        return "stop"
    
    def decide_action(self, target_center_x, target_area):
        """
        OLD: Area-based control logic (FALLBACK)
        Used when USE_DISTANCE_CONTROL = False
        """
        frame_center_x = FRAME_WIDTH // 2
        
        # Too close - stop (or backup if implemented)
        if target_area >= CLOSE_AREA:
            return "stop"
        
        # Turn left
        if target_center_x < frame_center_x - DEADZONE_PX:
            return "left"
        
        # Turn right
        if target_center_x > frame_center_x + DEADZONE_PX:
            return "right"
        
        # Move forward
        return "forward"
    
    def process_loop(self):
        """Main AI processing loop"""
        print("[AI] Processing loop started")
        
        # Pin to cores 1-3
        try:
            os.sched_setaffinity(0, {1, 2, 3})
            print("[AI] Pinned to cores 1-3")
        except Exception as e:
            print(f"[AI] Could not pin to cores: {e}")
        
        while self.running and not self.state.shutdown.is_set():
            # Wait for AI mode to be active
            if not self.state.ai_active.wait(timeout=0.1):
                continue
            
            # Check emergency stop
            if self.state.emergency_stop.is_set():
                self.state.send_motor_command("stop", source="ai")
                time.sleep(0.1)
                continue
            
            # Get frame
            frame = self.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue
            
            # Skip frames for performance
            self.frame_counter += 1
            if self.frame_counter % PROCESS_EVERY_N_FRAMES != 0:
                time.sleep(0.01)
                continue
            
            try:
                # Resize for faster processing
                small_frame = cv2.resize(frame, (0, 0), fx=DETECTION_SCALE, fy=DETECTION_SCALE)
                rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                # Detect faces
                face_locations = face_recognition.face_locations(rgb_small, model="hog")
                
                if face_locations:
                    # Get face encodings
                    face_encodings = face_recognition.face_encodings(rgb_small, face_locations)
                    
                    best_match = None
                    best_distance = None
                    best_location = None
                    
                    # Match each face
                    for face_encoding, face_location in zip(face_encodings, face_locations):
                        if not self.known_encodings:
                            # No known faces, just track any face
                            best_match = "Unknown"
                            best_distance = 0.0
                            best_location = face_location
                            break
                        
                        # Compare with known faces
                        distances = face_recognition.face_distance(self.known_encodings, face_encoding)
                        min_distance = float(np.min(distances))
                        
                        # Calculate face dimensions
                        top, right, bottom, left = face_location
                        face_width = (right - left) * 2  # Scale back up
                        face_height = (bottom - top) * 2
                        
                        # Debug print
                        print(f"[AI DEBUG] Distance: {min_distance:.4f}, Face: {face_width}x{face_height}px, Threshold: {RECOG_TOLERANCE}")
                        
                        if min_distance <= RECOG_TOLERANCE:
                            best_idx = int(np.argmin(distances))
                            name = self.known_names[best_idx]
                            
                            if best_distance is None or min_distance < best_distance:
                                best_match = name
                                best_distance = min_distance
                                best_location = face_location
                                
                                # Update debug info
                                self.debug_info["distance"] = min_distance
                                self.debug_info["face_size"] = (face_width, face_height)
                                self.debug_info["confidence"] = 1.0 - min_distance
                    
                    # Process best match
                    if best_match and best_location:
                        # Calculate confidence (1.0 - distance)
                        confidence = 1.0 - best_distance if best_distance is not None else 0.5
                        
                        # Only act if confidence is high enough
                        if confidence < MIN_CONFIDENCE_TO_ACT:
                            print(f"[AI] Low confidence ({confidence:.2f}) - ignoring")
                            self.state.update_ai_status(
                                tracking=best_match,
                                confidence=confidence,
                                action="low_confidence",
                                face_detected=True,
                                body_detected=False
                            )
                            continue
                        
                        self.last_face_seen = time.time()
                        self.tracking_name = best_match
                        
                        # Scale back up (face_location is (top, right, bottom, left))
                        top, right, bottom, left = best_location
                        scale_factor = 1.0 / DETECTION_SCALE
                        top = int(top * scale_factor)
                        right = int(right * scale_factor)
                        bottom = int(bottom * scale_factor)
                        left = int(left * scale_factor)
                        
                        # Calculate face metrics
                        face_center_x = int((left + right) / 2)
                        face_width = right - left
                        face_height = bottom - top
                        face_area = float((right - left) * (bottom - top)) / float(FRAME_WIDTH * FRAME_HEIGHT)
                        
                        # Decide action based on mode
                        if USE_DISTANCE_CONTROL:
                            # NEW: Distance-based control
                            estimated_distance = self.estimate_distance_from_face_size(face_width)
                            action = self.decide_action_distance_based(face_center_x, face_width, estimated_distance)
                            print(f"[AI] Tracking: {best_match} | Distance: {estimated_distance:.1f}m | Face: {face_width}x{face_height}px | Action: {action} | Confidence: {confidence:.2f}")
                        else:
                            # OLD: Area-based control (fallback)
                            action = self.decide_action(face_center_x, face_area)
                            print(f"[AI] Tracking: {best_match} | Area: {face_area:.3f} | Action: {action} | Confidence: {confidence:.2f}")
                        
                        # Send motor command
                        self.state.send_motor_command(action, self.speed, source="ai")
                        
                        # Update status
                        self.state.update_ai_status(
                            tracking=best_match,
                            confidence=confidence,
                            action=action,
                            face_detected=True,
                            body_detected=False
                        )
                
                # No face detected
                elif self.tracking_name and time.time() - self.last_face_seen <= NO_FACE_TIMEOUT_S:
                    # Keep last known state briefly
                    self.state.update_ai_status(
                        tracking=self.tracking_name,
                        action="searching",
                        face_detected=False,
                        body_detected=False
                    )
                else:
                    # Lost track - stop
                    self.state.send_motor_command("stop", source="ai")
                    self.tracking_name = None
                    self.state.update_ai_status(
                        tracking=None,
                        action="idle",
                        face_detected=False,
                        body_detected=False
                    )
            
            except Exception as e:
                print(f"[AI] Processing error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(0.1)
            
            time.sleep(0.05)  # ~20 FPS max
        
        print("[AI] Processing loop stopped")
    
    def start(self):
        """Start AI controller"""
        if self.running:
            print("[AI] Already running")
            return
        
        print("[AI] Starting AI controller...")
        
        # Load known faces
        if not self.load_known_faces():
            print("[AI] Warning: No known faces loaded, will track any face")
        
        # Start processing thread
        self.running = True
        self.thread = threading.Thread(target=self.process_loop, daemon=True)
        self.thread.start()
        
        print("[AI] ✅ AI controller started (face_recognition mode)")
    
    def stop(self):
        """Stop AI controller"""
        if not self.running:
            return
        
        print("[AI] Stopping AI controller...")
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2.0)
        
        print("[AI] AI controller stopped")
