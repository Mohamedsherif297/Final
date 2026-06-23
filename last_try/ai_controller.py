"""
AI Controller
Wraps the face recognition/tracking AI and integrates with system state
"""
import os
import pickle
import time
import threading
import cv2
import numpy as np

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("[AI] Warning: mediapipe not installed")

try:
    import face_recognition
    FACE_RECOG_AVAILABLE = True
except ImportError:
    FACE_RECOG_AVAILABLE = False
    print("[AI] Warning: face_recognition not installed")

from system_state import SystemState

# AI Configuration
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
DEADZONE_PX = 80
CLOSE_AREA = 0.25
NO_FACE_TIMEOUT_S = 0.5
RECOG_TOLERANCE = 0.5
BODY_CLOSE_AREA = 0.35
BODY_LOST_TIMEOUT_S = 0.5
KNOWN_FACES_DIR = "pi_minimal/known_faces/images"
ENCODINGS_FILE = "pi_minimal/known_faces/encodings.pkl"

class AIController:
    """AI-based person following controller"""
    
    def __init__(self, state: SystemState, speed: int = 60):
        self.state = state
        self.speed = speed
        self.running = False
        self.thread = None
        
        # AI models
        self.mp_face = None
        self.mp_pose = None
        self.known_encodings = []
        self.known_names = []
        
        # Tracking state
        self.last_face_seen = 0.0
        self.last_body_seen = 0.0
        self.tracking_name = None
        
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
            return
        
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
                
                return
            
            except Exception as e:
                print(f"[AI] Error loading encodings file: {e}")
                print("[AI] Falling back to generating encodings from images...")
        
        else:
            print(f"[AI] Encodings file not found: {ENCODINGS_FILE}")
            print("[AI] Generating encodings from images (this may take a while)...")
        
        # Fallback: Generate encodings from images
        if not os.path.isdir(KNOWN_FACES_DIR):
            print(f"[AI] Known faces directory not found: {KNOWN_FACES_DIR}")
            print("[AI] Please run: python generate_encodings.py")
            return
        
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
        print(f"[AI] Tip: Run 'python generate_encodings.py' to pre-compute encodings for faster startup")
    
    def initialize_models(self):
        """Initialize MediaPipe models"""
        if not MEDIAPIPE_AVAILABLE:
            print("[AI] MediaPipe not available")
            return False
        
        try:
            self.mp_face = mp.solutions.face_detection.FaceDetection(
                min_detection_confidence=0.6
            )
            self.mp_pose = mp.solutions.pose.Pose(
                model_complexity=0,
                smooth_landmarks=True,
                enable_segmentation=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            print("[AI] MediaPipe models initialized")
            return True
        except Exception as e:
            print(f"[AI] Error initializing models: {e}")
            return False
    
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
    
    def draw_overlay(self, frame, tracking_name, distance, face_size, action):
        """Draw debug overlay on frame"""
        if frame is None:
            return frame
        
        overlay_frame = frame.copy()
        
        # Calculate confidence (inverse of distance, normalized to 0-100%)
        confidence = max(0, min(100, (1.0 - distance) * 100)) if distance is not None else 0
        
        # Background for text
        overlay = overlay_frame.copy()
        cv2.rectangle(overlay, (10, 10), (630, 130), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, overlay_frame, 0.4, 0, overlay_frame)
        
        # Display information
        y_offset = 35
        
        if tracking_name:
            cv2.putText(overlay_frame, f"Tracking: {tracking_name}", (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(overlay_frame, "Tracking: None", (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        
        y_offset += 30
        
        if distance is not None:
            cv2.putText(overlay_frame, f"Distance: {distance:.4f}", (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        y_offset += 25
        
        cv2.putText(overlay_frame, f"Confidence: {confidence:.1f}%", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        y_offset += 25
        
        if face_size and face_size[0] > 0:
            cv2.putText(overlay_frame, f"Face Size: {face_size[0]}x{face_size[1]}px", (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        y_offset += 25
        
        if action:
            action_color = (0, 255, 0) if action == "stop" else (255, 165, 0)
            cv2.putText(overlay_frame, f"Action: {action.upper()}", (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, action_color, 2)
        
        return overlay_frame
    
    def recognize_face(self, rgb_frame, face_bbox):
        """Recognize face in bounding box with debugging info"""
        if not self.known_encodings:
            return None, None, None
        
        top, right, bottom, left = face_bbox
        try:
            encs = face_recognition.face_encodings(rgb_frame, [(top, right, bottom, left)])
            if not encs:
                return None, None, None
            
            face_enc = encs[0]
            distances = face_recognition.face_distance(self.known_encodings, face_enc)
            best_idx = int(np.argmin(distances))
            best_distance = float(distances[best_idx])
            
            # Calculate face dimensions
            face_width = right - left
            face_height = bottom - top
            
            # Debug print
            print(f"[AI DEBUG] Best distance: {best_distance:.4f}, "
                  f"Face size: {face_width}x{face_height}px, "
                  f"Threshold: {RECOG_TOLERANCE}")
            
            if best_distance <= RECOG_TOLERANCE:
                return self.known_names[best_idx], best_distance, (face_width, face_height)
        except Exception as e:
            print(f"[AI] Recognition error: {e}")
        
        return None, None, None
    
    def pose_bbox(self, landmarks):
        """Get bounding box from pose landmarks"""
        pts = []
        for lm in landmarks:
            if lm.visibility < 0.5:
                continue
            pts.append((int(lm.x * FRAME_WIDTH), int(lm.y * FRAME_HEIGHT)))
        
        if not pts:
            return None
        
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x1, x2 = max(0, min(xs)), min(FRAME_WIDTH, max(xs))
        y1, y2 = max(0, min(ys)), min(FRAME_HEIGHT, max(ys))
        
        if x2 <= x1 or y2 <= y1:
            return None
        
        return x1, y1, x2, y2
    
    def decide_action(self, target_center_x, target_area, close_area):
        """Decide motor action based on target position"""
        frame_center_x = FRAME_WIDTH // 2
        
        if target_area >= close_area:
            return "stop"
        
        if target_center_x < frame_center_x - DEADZONE_PX:
            return "left"
        
        if target_center_x > frame_center_x + DEADZONE_PX:
            return "right"
        
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
            
            try:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_result = self.mp_face.process(rgb)
                
                known_face = None
                known_bbox = None
                
                # Detect and recognize faces
                if face_result.detections:
                    best_match = None
                    best_distance = None
                    
                    for det in face_result.detections:
                        box = det.location_data.relative_bounding_box
                        left = int(box.xmin * FRAME_WIDTH)
                        top = int(box.ymin * FRAME_HEIGHT)
                        right = int((box.xmin + box.width) * FRAME_WIDTH)
                        bottom = int((box.ymin + box.height) * FRAME_HEIGHT)
                        
                        left = max(0, left)
                        top = max(0, top)
                        right = min(FRAME_WIDTH, right)
                        bottom = min(FRAME_HEIGHT, bottom)
                        
                        name, dist, face_size = self.recognize_face(rgb, (top, right, bottom, left))
                        if name and (best_distance is None or dist < best_distance):
                            best_distance = dist
                            best_match = name
                            known_bbox = (top, right, bottom, left)
                            
                            # Update debug info
                            self.debug_info["distance"] = dist
                            self.debug_info["face_size"] = face_size
                            self.debug_info["confidence"] = (1.0 - dist) if dist else 0.0
                    
                    if best_match:
                        known_face = best_match
                
                # Process known face
                if known_face and known_bbox:
                    self.last_face_seen = time.time()
                    self.tracking_name = known_face
                    
                    top, right, bottom, left = known_bbox
                    face_center_x = int((left + right) / 2)
                    face_area = float((right - left) * (bottom - top)) / float(FRAME_WIDTH * FRAME_HEIGHT)
                    
                    action = self.decide_action(face_center_x, face_area, CLOSE_AREA)
                    
                    # Send motor command
                    self.state.send_motor_command(action, self.speed, source="ai")
                    
                    # Update status
                    self.state.update_ai_status(
                        tracking=known_face,
                        confidence=1.0 - best_distance if best_distance else 0.0,
                        action=action,
                        face_detected=True,
                        body_detected=False
                    )
                
                # Fall back to body tracking
                elif self.tracking_name and time.time() - self.last_face_seen <= NO_FACE_TIMEOUT_S:
                    pose_result = self.mp_pose.process(rgb)
                    
                    if pose_result.pose_landmarks:
                        bbox = self.pose_bbox(pose_result.pose_landmarks.landmark)
                        
                        if bbox:
                            self.last_body_seen = time.time()
                            x1, y1, x2, y2 = bbox
                            body_center_x = int((x1 + x2) / 2)
                            body_area = float((x2 - x1) * (y2 - y1)) / float(FRAME_WIDTH * FRAME_HEIGHT)
                            
                            action = self.decide_action(body_center_x, body_area, BODY_CLOSE_AREA)
                            
                            self.state.send_motor_command(action, self.speed, source="ai")
                            
                            self.state.update_ai_status(
                                tracking=self.tracking_name,
                                action=action,
                                face_detected=False,
                                body_detected=True
                            )
                        elif time.time() - self.last_body_seen > BODY_LOST_TIMEOUT_S:
                            self.state.send_motor_command("stop", source="ai")
                            self.tracking_name = None
                            self.state.update_ai_status(
                                tracking=None,
                                action="stop",
                                face_detected=False,
                                body_detected=False
                            )
                    elif time.time() - self.last_body_seen > BODY_LOST_TIMEOUT_S:
                        self.state.send_motor_command("stop", source="ai")
                        self.tracking_name = None
                        self.state.update_ai_status(
                            tracking=None,
                            action="stop",
                            face_detected=False,
                            body_detected=False
                        )
                else:
                    self.state.send_motor_command("stop", source="ai")
                    self.state.update_ai_status(
                        tracking=None,
                        action="idle",
                        face_detected=False,
                        body_detected=False
                    )
            
            except Exception as e:
                print(f"[AI] Processing error: {e}")
                time.sleep(0.1)
            
            time.sleep(0.01)
        
        print("[AI] Processing loop stopped")
    
    def start(self):
        """Start AI controller"""
        if self.running:
            print("[AI] Already running")
            return
        
        print("[AI] Starting AI controller...")
        
        # Load known faces
        self.load_known_faces()
        
        # Initialize models
        if not self.initialize_models():
            print("[AI] Failed to initialize models")
            return
        
        # Start processing thread
        self.running = True
        self.thread = threading.Thread(target=self.process_loop, daemon=True)
        self.thread.start()
        
        print("[AI] AI controller started")
    
    def stop(self):
        """Stop AI controller"""
        if not self.running:
            return
        
        print("[AI] Stopping AI controller...")
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2.0)
        
        print("[AI] AI controller stopped")
