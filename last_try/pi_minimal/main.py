import argparse
import os
import pickle
import time

import cv2
import mediapipe as mp
import numpy as np

try:
    import face_recognition
    FACE_RECOG_AVAILABLE = True
except Exception:
    FACE_RECOG_AVAILABLE = False

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except Exception:
    GPIO_AVAILABLE = False

# GPIO pins (BCM)
LEFT_IN1 = 17
LEFT_IN2 = 27
LEFT_ENA = 18
RIGHT_IN3 = 23
RIGHT_IN4 = 24
RIGHT_ENB = 25
TRIG = 5
ECHO = 6

# Camera settings
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Face logic thresholds
DEADZONE_PX = 80
CLOSE_AREA = 0.25
NO_FACE_TIMEOUT_S = 0.5
RECOG_TOLERANCE = 0.5

# Body tracking thresholds
BODY_CLOSE_AREA = 0.35
BODY_LOST_TIMEOUT_S = 0.5

# Known faces directory and encodings file
KNOWN_FACES_DIR = "known_faces/images"
ENCODINGS_FILE = "known_faces/encodings.pkl"

# Ultrasonic settings
OBSTACLE_CM = 25.0
SONIC_SPEED_CM_S = 34300.0


def setup_gpio(dry_run: bool):
    if dry_run or not GPIO_AVAILABLE:
        return None, None

    GPIO.setmode(GPIO.BCM)
    GPIO.setup([LEFT_IN1, LEFT_IN2, LEFT_ENA, RIGHT_IN3, RIGHT_IN4, RIGHT_ENB], GPIO.OUT)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

    left_pwm = GPIO.PWM(LEFT_ENA, 100)
    right_pwm = GPIO.PWM(RIGHT_ENB, 100)
    left_pwm.start(0)
    right_pwm.start(0)

    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.05)

    return left_pwm, right_pwm


def cleanup_gpio(left_pwm, right_pwm, dry_run: bool):
    if dry_run or not GPIO_AVAILABLE:
        return
    stop_motors(left_pwm, right_pwm, dry_run)
    left_pwm.stop()
    right_pwm.stop()
    GPIO.cleanup()


def stop_motors(left_pwm, right_pwm, dry_run: bool):
    if dry_run or not GPIO_AVAILABLE:
        return
    GPIO.output(LEFT_IN1, GPIO.LOW)
    GPIO.output(LEFT_IN2, GPIO.LOW)
    GPIO.output(RIGHT_IN3, GPIO.LOW)
    GPIO.output(RIGHT_IN4, GPIO.LOW)
    left_pwm.ChangeDutyCycle(0)
    right_pwm.ChangeDutyCycle(0)


def forward(left_pwm, right_pwm, speed: int, dry_run: bool):
    if dry_run or not GPIO_AVAILABLE:
        return
    GPIO.output(LEFT_IN1, GPIO.HIGH)
    GPIO.output(LEFT_IN2, GPIO.LOW)
    GPIO.output(RIGHT_IN3, GPIO.HIGH)
    GPIO.output(RIGHT_IN4, GPIO.LOW)
    left_pwm.ChangeDutyCycle(speed)
    right_pwm.ChangeDutyCycle(speed)


def turn_left(left_pwm, right_pwm, speed: int, dry_run: bool):
    if dry_run or not GPIO_AVAILABLE:
        return
    GPIO.output(LEFT_IN1, GPIO.LOW)
    GPIO.output(LEFT_IN2, GPIO.HIGH)
    GPIO.output(RIGHT_IN3, GPIO.HIGH)
    GPIO.output(RIGHT_IN4, GPIO.LOW)
    left_pwm.ChangeDutyCycle(speed)
    right_pwm.ChangeDutyCycle(speed)


def turn_right(left_pwm, right_pwm, speed: int, dry_run: bool):
    if dry_run or not GPIO_AVAILABLE:
        return
    GPIO.output(LEFT_IN1, GPIO.HIGH)
    GPIO.output(LEFT_IN2, GPIO.LOW)
    GPIO.output(RIGHT_IN3, GPIO.LOW)
    GPIO.output(RIGHT_IN4, GPIO.HIGH)
    left_pwm.ChangeDutyCycle(speed)
    right_pwm.ChangeDutyCycle(speed)


def read_ultrasonic_cm(dry_run: bool) -> float:
    if dry_run or not GPIO_AVAILABLE:
        return 9999.0

    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.000002)
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)

    start_time = time.time()
    timeout = start_time + 0.02
    while GPIO.input(ECHO) == 0:
        if time.time() > timeout:
            return 9999.0
        start_time = time.time()

    stop_time = time.time()
    timeout = stop_time + 0.02
    while GPIO.input(ECHO) == 1:
        if time.time() > timeout:
            break
        stop_time = time.time()

    duration = stop_time - start_time
    distance = (duration * SONIC_SPEED_CM_S) / 2.0
    return distance


def decide_and_drive(target_center_x: int, target_area: float, frame_center_x: int,
                     left_pwm, right_pwm, speed: int, dry_run: bool, close_area: float):
    if target_area >= close_area:
        stop_motors(left_pwm, right_pwm, dry_run)
        return "stop_close"

    if target_center_x < frame_center_x - DEADZONE_PX:
        turn_left(left_pwm, right_pwm, speed, dry_run)
        return "turn_left"

    if target_center_x > frame_center_x + DEADZONE_PX:
        turn_right(left_pwm, right_pwm, speed, dry_run)
        return "turn_right"

    forward(left_pwm, right_pwm, speed, dry_run)
    return "forward"


def load_known_faces(base_dir: str, encodings_file: str):
    """Load known faces from pre-computed encodings or generate if needed"""
    if not FACE_RECOG_AVAILABLE:
        raise RuntimeError("face_recognition is not available")

    encodings = []
    names = []

    # Try to load from pre-computed encodings file
    if os.path.exists(encodings_file):
        try:
            start_time = time.time()
            print(f"Loading pre-computed encodings from {encodings_file}")
            
            with open(encodings_file, "rb") as f:
                data = pickle.load(f)
            
            encodings = data["encodings"]
            names = data["names"]
            
            load_time = time.time() - start_time
            print(f"Loaded {len(encodings)} encodings in {load_time:.2f}s")
            print(f"Generated at: {data.get('generated_at', 'Unknown')}")
            
            return encodings, names
        
        except Exception as e:
            print(f"Error loading encodings file: {e}")
            print("Falling back to generating encodings from images...")
    
    else:
        print(f"Encodings file not found: {encodings_file}")
        print("Generating encodings from images (this may take a while)...")

    # Fallback: Generate encodings from images
    if not os.path.isdir(base_dir):
        print(f"Known faces directory not found: {base_dir}")
        return encodings, names

    start_time = time.time()
    for person in os.listdir(base_dir):
        person_dir = os.path.join(base_dir, person)
        if not os.path.isdir(person_dir):
            continue
        for fname in os.listdir(person_dir):
            if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            path = os.path.join(person_dir, fname)
            try:
                image = face_recognition.load_image_file(path)
                encs = face_recognition.face_encodings(image)
                if not encs:
                    continue
                encodings.append(encs[0])
                names.append(person)
            except Exception as e:
                print(f"Error loading {path}: {e}")
    
    load_time = time.time() - start_time
    print(f"Generated {len(encodings)} encodings in {load_time:.2f}s")
    print("Tip: Run 'python generate_encodings.py' to pre-compute encodings for faster startup")

    return encodings, names


def recognize_face(rgb_frame: np.ndarray, face_bbox, known_encodings, known_names):
    """Recognize face with debugging information"""
    if not known_encodings:
        return None, None, None
    
    top, right, bottom, left = face_bbox
    encs = face_recognition.face_encodings(rgb_frame, [(top, right, bottom, left)])
    if not encs:
        return None, None, None
    
    face_enc = encs[0]
    distances = face_recognition.face_distance(known_encodings, face_enc)
    best_idx = int(np.argmin(distances))
    best_distance = float(distances[best_idx])
    
    # Calculate face dimensions
    face_width = right - left
    face_height = bottom - top
    
    # Debug print
    print(f"[DEBUG] Distance: {best_distance:.4f}, Face: {face_width}x{face_height}px, Threshold: {RECOG_TOLERANCE}")
    
    if best_distance <= RECOG_TOLERANCE:
        return known_names[best_idx], best_distance, (face_width, face_height)
    
    return None, None, None


def draw_debug_overlay(frame, tracking_name, distance, face_size, action):
    """Draw debug information on frame"""
    overlay_frame = frame.copy()
    
    # Calculate confidence
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
        action_color = (0, 255, 0) if action == "stop_close" else (255, 165, 0)
        cv2.putText(overlay_frame, f"Action: {action.replace('_', ' ').upper()}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, action_color, 2)
    
    return overlay_frame


def pose_bbox(landmarks, frame_w: int, frame_h: int):
    pts = []
    for lm in landmarks:
        if lm.visibility < 0.5:
            continue
        pts.append((int(lm.x * frame_w), int(lm.y * frame_h)))
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x1, x2 = max(0, min(xs)), min(frame_w, max(xs))
    y1, y2 = max(0, min(ys)), min(frame_h, max(ys))
    if x2 <= x1 or y2 <= y1:
        return None
    return x1, y1, x2, y2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print decisions without GPIO")
    parser.add_argument("--display", action="store_true", help="Show camera window")
    parser.add_argument("--speed", type=int, default=60, help="Motor PWM duty 0-100")
    parser.add_argument("--faces-dir", default=KNOWN_FACES_DIR, help="Known faces directory")
    args = parser.parse_args()

    dry_run = args.dry_run or not GPIO_AVAILABLE

    if not FACE_RECOG_AVAILABLE:
        raise RuntimeError("face_recognition not installed")

    # Determine encodings file path relative to faces_dir
    if args.faces_dir == KNOWN_FACES_DIR:
        encodings_file = ENCODINGS_FILE
    else:
        encodings_file = os.path.join(os.path.dirname(args.faces_dir), "encodings.pkl")
    
    known_encodings, known_names = load_known_faces(args.faces_dir, encodings_file)

    left_pwm, right_pwm = setup_gpio(dry_run)

    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    mp_face = mp.solutions.face_detection.FaceDetection(min_detection_confidence=0.6)
    mp_pose = mp.solutions.pose.Pose(
        model_complexity=0,
        smooth_landmarks=True,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    last_face_seen = 0.0
    last_body_seen = 0.0
    tracking_name = None
    
    # Debug info
    current_distance = None
    current_face_size = (0, 0)
    current_action = "idle"

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_result = mp_face.process(rgb)

            obstacle_cm = read_ultrasonic_cm(dry_run)
            if obstacle_cm < OBSTACLE_CM:
                stop_motors(left_pwm, right_pwm, dry_run)
                if dry_run:
                    print("emergency_stop obstacle_cm=%.1f" % obstacle_cm)
                time.sleep(0.05)
                continue

            known_face = None
            known_bbox = None

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

                    name, dist, face_size = recognize_face(rgb, (top, right, bottom, left), known_encodings, known_names)
                    if name is None:
                        continue
                    if best_distance is None or dist < best_distance:
                        best_distance = dist
                        best_match = name
                        known_bbox = (top, right, bottom, left)
                        current_distance = dist
                        current_face_size = face_size

                if best_match:
                    known_face = best_match

            if known_face and known_bbox:
                last_face_seen = time.time()
                tracking_name = known_face
                top, right, bottom, left = known_bbox
                face_center_x = int((left + right) / 2)
                face_area = float((right - left) * (bottom - top)) / float(FRAME_WIDTH * FRAME_HEIGHT)
                action = decide_and_drive(
                    face_center_x, face_area, FRAME_WIDTH // 2,
                    left_pwm, right_pwm, args.speed, dry_run, CLOSE_AREA
                )
                current_action = action
                if dry_run:
                    print("%s known=%s area=%.3f dist=%.4f" % (action, known_face, face_area, best_distance))
            else:
                if time.time() - last_face_seen <= NO_FACE_TIMEOUT_S:
                    pass
                elif tracking_name:
                    pose_result = mp_pose.process(rgb)
                    if pose_result.pose_landmarks:
                        bbox = pose_bbox(pose_result.pose_landmarks.landmark, FRAME_WIDTH, FRAME_HEIGHT)
                        if bbox:
                            last_body_seen = time.time()
                            x1, y1, x2, y2 = bbox
                            body_center_x = int((x1 + x2) / 2)
                            body_area = float((x2 - x1) * (y2 - y1)) / float(FRAME_WIDTH * FRAME_HEIGHT)
                            action = decide_and_drive(
                                body_center_x, body_area, FRAME_WIDTH // 2,
                                left_pwm, right_pwm, args.speed, dry_run, BODY_CLOSE_AREA
                            )
                            current_action = action
                            if dry_run:
                                print("%s body area=%.3f" % (action, body_area))
                        else:
                            if time.time() - last_body_seen > BODY_LOST_TIMEOUT_S:
                                stop_motors(left_pwm, right_pwm, dry_run)
                                tracking_name = None
                                current_action = "stop_no_body"
                                if dry_run:
                                    print("stop_no_body")
                    else:
                        if time.time() - last_body_seen > BODY_LOST_TIMEOUT_S:
                            stop_motors(left_pwm, right_pwm, dry_run)
                            tracking_name = None
                            current_action = "stop_no_body"
                            if dry_run:
                                print("stop_no_body")
                else:
                    stop_motors(left_pwm, right_pwm, dry_run)
                    current_action = "stop_no_known"
                    if dry_run:
                        print("stop_no_known")

            if args.display:
                display_frame = draw_debug_overlay(frame, tracking_name, current_distance, 
                                                   current_face_size, current_action)
                cv2.imshow("pi_minimal", display_frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            time.sleep(0.01)

    except KeyboardInterrupt:
        pass
    finally:
        stop_motors(left_pwm, right_pwm, dry_run)
        cleanup_gpio(left_pwm, right_pwm, dry_run)
        cap.release()
        if args.display:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
