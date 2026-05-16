"""
gesture_controller.py
Hand gesture → MQTT controller for surveillance car.

Left hand  : motors  (forward / backward / left / right / stop)
Right hand : servos  (pan / tilt via thumb direction)

Camera is mirrored (selfie view).  Pass a camera index as argv[1] (default 0).
Press ESC to quit.
"""

import cv2
import mediapipe as mp
import paho.mqtt.client as mqtt
import json
import ssl
import sys
import time
import os
from collections import deque, Counter

# ── MQTT ──────────────────────────────────────────────────────────────────────
MQTT_HOST   = "78ed3eab06c348d0948ef7681cf4a377.s1.eu.hivemq.cloud"
MQTT_PORT   = 8883          # TCP + TLS
MQTT_USER   = "mohamed"
MQTT_PASS   = "P@ssw0rd"
TOPIC_MOTOR = "dev/motor"
TOPIC_SERVO = "dev/servo"
TOPIC_STATUS = "dev/gesture_status"  # NEW: Publish gesture status

# ── Model ─────────────────────────────────────────────────────────────────────
MODEL_PATH  = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")

# ── Tuning ────────────────────────────────────────────────────────────────────
SMOOTH_WINDOW    = 5    # majority-vote buffer size (frames)
SMOOTH_THRESHOLD = 4    # minimum votes required to confirm a gesture
THUMB_MIN_RATIO  = 0.25 # min thumb displacement / hand_size
HORIZ_BIAS       = 1.3  # |dx| > HORIZ_BIAS × |dy|  →  horizontal axis wins
VERT_BIAS        = 0.8  # |dy| > VERT_BIAS  × |dx|  →  vertical   axis wins
SERVO_STEP       = 5    # degrees applied per confirmed frame (right hand)
SERVO_RATE       = 3    # publish servo MQTT every N frames while active
NO_HAND_GRACE    = 4    # frames a hand may be absent before detector resets

# Finger (tip, pip) landmark index pairs — index through pinky
_FINGER_PAIRS = [(8, 6), (12, 10), (16, 14), (20, 18)]

# Standard hand skeleton connections (21 landmarks)
_HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),          # thumb
    (0,5),(5,6),(6,7),(7,8),          # index
    (0,9),(9,10),(10,11),(11,12),     # middle
    (0,13),(13,14),(14,15),(15,16),   # ring
    (0,17),(17,18),(18,19),(19,20),   # pinky
    (5,9),(9,13),(13,17),             # knuckle bar
]

_FONT = cv2.FONT_HERSHEY_SIMPLEX

_MOTOR_COLORS = {
    "forward":  (0,   210,   0),
    "backward": (0,   165, 255),
    "left":     (255, 200,   0),
    "right":    (0,   200, 255),
    "stop":     (30,  30,  180),
}


# ── GestureDetector ───────────────────────────────────────────────────────────

class GestureDetector:
    """
    Classifies thumb direction from 21 MediaPipe hand landmarks.
    Requires a fist (fingers 2-5 curled) before reporting any direction.
    Applies a majority-vote smoothing buffer to suppress noise.
    """

    def __init__(self):
        self._buf = deque(maxlen=SMOOTH_WINDOW)

    def _is_fist(self, lm):
        # tip.y > pip.y means tip is lower in the image = finger curled toward palm
        return all(lm[t].y > lm[p].y for t, p in _FINGER_PAIRS)

    def classify(self, lm):
        """Return 'up'|'down'|'left'|'right' or None for this single frame."""
        if not self._is_fist(lm):
            return None

        # Palm centroid: wrist + index MCP + pinky MCP
        pcx = (lm[0].x + lm[5].x + lm[17].x) / 3
        pcy = (lm[0].y + lm[5].y + lm[17].y) / 3

        # Normalise by wrist-to-middle-MCP distance
        hand_sz = ((lm[9].x - lm[0].x) ** 2 + (lm[9].y - lm[0].y) ** 2) ** 0.5
        if hand_sz < 0.01:
            return None

        dx = (lm[4].x - pcx) / hand_sz
        dy = (lm[4].y - pcy) / hand_sz

        if (dx ** 2 + dy ** 2) ** 0.5 < THUMB_MIN_RATIO:
            return None   # thumb not extended far enough

        # Axis disambiguation with hysteresis
        if abs(dx) > HORIZ_BIAS * abs(dy):
            return "right" if dx > 0 else "left"
        if abs(dy) > VERT_BIAS * abs(dx):
            return "up" if dy < 0 else "down"
        return None   # ambiguous diagonal → ignore

    def push(self, raw):
        self._buf.append(raw)

    def smoothed(self):
        if len(self._buf) < SMOOTH_WINDOW:
            return None
        top, n = Counter(self._buf).most_common(1)[0]
        return top if n >= SMOOTH_THRESHOLD else None

    def confidence(self):
        if not self._buf:
            return 0.0
        top, n = Counter(self._buf).most_common(1)[0]
        return n / SMOOTH_WINDOW if top is not None else 0.0

    def reset(self):
        self._buf.clear()


# ── ServoState ────────────────────────────────────────────────────────────────

class ServoState:
    def __init__(self):
        self.pan  = 90
        self.tilt = 90
        self._tick = 0

    def apply(self, direction):
        if direction == "up":
            self.tilt = max(0,   self.tilt - SERVO_STEP)
        elif direction == "down":
            self.tilt = min(180, self.tilt + SERVO_STEP)
        elif direction == "right":
            self.pan  = min(180, self.pan  + SERVO_STEP)
        elif direction == "left":
            self.pan  = max(0,   self.pan  - SERVO_STEP)

    def should_publish(self):
        self._tick = (self._tick + 1) % SERVO_RATE
        return self._tick == 0


# ── MQTTController ────────────────────────────────────────────────────────────

class MQTTController:
    def __init__(self):
        self.connected   = False
        self._last_motor = None

        try:
            self._client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id=f"gesture-{int(time.time())}",
            )
        except AttributeError:
            self._client = mqtt.Client(client_id=f"gesture-{int(time.time())}")

        self._client.username_pw_set(MQTT_USER, MQTT_PASS)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self._client.tls_set_context(ctx)
        self._client.on_connect    = self._on_connect
        self._client.on_disconnect = self._on_disconnect

    def _on_connect(self, *args):
        rc = args[3]
        rc_val = rc.value if hasattr(rc, "value") else rc
        self.connected = (rc_val == 0)
        print(f"[MQTT] {'Connected' if self.connected else f'Failed (rc={rc_val})'}")

    def _on_disconnect(self, *args):
        self.connected = False
        print("[MQTT] Disconnected")

    def start(self):
        try:
            self._client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
            self._client.loop_start()
            print(f"[MQTT] Connecting to {MQTT_HOST}:{MQTT_PORT} …")
        except Exception as exc:
            print(f"[MQTT] Connection error: {exc}")

    def send_motor(self, cmd):
        if cmd == self._last_motor:
            return
        if self.connected:
            payload = json.dumps({"direction": cmd, "speed": 70})  # Match Pi format
            self._client.publish(TOPIC_MOTOR, payload, qos=1)
            print(f"[MOTOR] -> {cmd}")
            # Publish status for dashboard
            status = json.dumps({"type": "gesture_motor", "command": cmd})
            self._client.publish(TOPIC_STATUS, status, qos=0)
        self._last_motor = cmd

    def send_servo(self, pan, tilt):
        if self.connected:
            payload = json.dumps({"pan": int(pan), "tilt": int(tilt)})
            self._client.publish(TOPIC_SERVO, payload, qos=1)
            print(f"[SERVO] -> pan={pan}  tilt={tilt}")
            # Publish status for dashboard
            status = json.dumps({"type": "gesture_servo", "pan": int(pan), "tilt": int(tilt)})
            self._client.publish(TOPIC_STATUS, status, qos=0)

    def shutdown(self):
        self._client.loop_stop()
        self._client.disconnect()


# ── Drawing ───────────────────────────────────────────────────────────────────

def draw_hand(frame, landmarks, color):
    h, w = frame.shape[:2]
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for a, b in _HAND_CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], (200, 200, 200), 2, cv2.LINE_AA)
    for pt in pts:
        cv2.circle(frame, pt, 4, color, -1, cv2.LINE_AA)


def _text(img, text, pos, scale=0.7, col=(255, 255, 255), thick=2):
    cv2.putText(img, text, pos, _FONT, scale, col, thick, cv2.LINE_AA)


def draw_ui(frame, motor, servo, mqtt_ok, l_gesture, r_gesture, l_conf, r_conf, fps):
    h, w = frame.shape[:2]

    # Top status bar
    cv2.rectangle(frame, (0, 0), (w, 44), (0, 140, 0) if mqtt_ok else (30, 30, 160), -1)
    _text(frame, "MQTT  CONNECTED" if mqtt_ok else "MQTT  DISCONNECTED", (12, 30), 0.75)
    _text(frame, f"{fps:.0f} fps", (w - 90, 30), 0.65)

    # Motor panel — bottom-left
    mc = _MOTOR_COLORS.get(motor, (50, 50, 50))
    cv2.rectangle(frame, (0, h - 88), (220, h), mc, -1)
    _text(frame, "MOTOR  (left hand)", (10, h - 60), 0.55)
    _text(frame, motor.upper(), (10, h - 18), 1.1)

    # Servo panel — bottom-right
    cv2.rectangle(frame, (w - 250, h - 88), (w, h), (20, 20, 20), -1)
    _text(frame, "SERVO  (right hand)", (w - 240, h - 60), 0.55)
    _text(frame, f"Pan {servo.pan:3d}   Tilt {servo.tilt:3d}", (w - 240, h - 18), 0.85, (180, 220, 255))

    # Left gesture + confidence bar
    if l_conf > 0.05 or l_gesture:
        _text(frame, f"L: {l_gesture or '...'}", (10, 72), 0.9, (0, 240, 100))
        bar_w = int(l_conf * 140)
        cv2.rectangle(frame, (10, 82), (150, 96), (25, 70, 25), -1)
        if bar_w:
            cv2.rectangle(frame, (10, 82), (10 + bar_w, 96), (0, 220, 90), -1)

    # Right gesture + confidence bar
    if r_conf > 0.05 or r_gesture:
        _text(frame, f"R: {r_gesture or '...'}", (w - 210, 72), 0.9, (120, 200, 255))
        bar_w = int(r_conf * 140)
        cv2.rectangle(frame, (w - 210, 82), (w - 70, 96), (20, 40, 80), -1)
        if bar_w:
            cv2.rectangle(frame, (w - 210, 82), (w - 210 + bar_w, 96), (110, 190, 255), -1)

    # Hint
    _text(frame,
          "Fist+Thumb: UP=fwd  DOWN=back  L/R=turn  |  Right hand=Servo  |  ESC=quit",
          (w // 2 - 320, h - 8), 0.44, (155, 155, 155), 1)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    cam_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0

    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model file not found: {MODEL_PATH}")
        print("  Run:  python -c \"import urllib.request,ssl; ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE; o=urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx)); open('hand_landmarker.task','wb').write(o.open('https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task').read())\"")
        return

    HandLandmarker        = mp.tasks.vision.HandLandmarker
    HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
    RunningMode           = mp.tasks.vision.RunningMode
    BaseOptions           = mp.tasks.BaseOptions

    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.8,
        min_hand_presence_confidence=0.8,
        min_tracking_confidence=0.8,
    )

    l_det  = GestureDetector()
    r_det  = GestureDetector()
    servo  = ServoState()
    broker = MQTTController()
    broker.start()

    cap = cv2.VideoCapture(cam_idx)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    motor      = "stop"
    l_no_hand  = 0
    r_no_hand  = 0
    start_ms   = time.time() * 1000
    prev_time  = time.time()

    print("[INFO] Running — show your hands to the camera. ESC to quit.")

    with HandLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)    # mirror (selfie view)
            rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            mp_image     = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            timestamp_ms = int(time.time() * 1000 - start_ms)
            result       = landmarker.detect_for_video(mp_image, timestamp_ms)

            l_raw, r_raw   = None, None
            l_seen, r_seen = False, False

            for i, hand_lm in enumerate(result.hand_landmarks):
                # MediaPipe on flipped frame: "Right" label = user's LEFT hand (front-cam mirror)
                mp_label = result.handedness[i][0].category_name
                side     = "left" if mp_label == "Right" else "right"
                det      = l_det if side == "left" else r_det

                raw = det.classify(hand_lm)
                if side == "left":
                    l_raw, l_seen = raw, True
                else:
                    r_raw, r_seen = raw, True

                col = (0, 220, 90) if side == "left" else (90, 200, 255)
                draw_hand(frame, hand_lm, col)

            # ── Left hand → motor
            if l_seen:
                l_no_hand = 0
                l_det.push(l_raw)
            else:
                l_no_hand += 1
                if l_no_hand >= NO_HAND_GRACE:
                    l_det.reset()

            l_gesture = l_det.smoothed()
            l_conf    = l_det.confidence()
            _MOTOR_MAP = {"up": "forward", "down": "backward", "left": "left", "right": "right"}
            motor     = _MOTOR_MAP.get(l_gesture, "stop")
            broker.send_motor(motor)

            # ── Right hand → servo
            if r_seen:
                r_no_hand = 0
                r_det.push(r_raw)
            else:
                r_no_hand += 1
                if r_no_hand >= NO_HAND_GRACE:
                    r_det.reset()

            r_gesture = r_det.smoothed()
            r_conf    = r_det.confidence()

            if r_gesture:
                servo.apply(r_gesture)
            if servo.should_publish() and r_gesture:
                broker.send_servo(servo.pan, servo.tilt)

            # ── FPS + UI
            now       = time.time()
            fps       = 1.0 / max(now - prev_time, 1e-9)
            prev_time = now

            draw_ui(frame, motor, servo, broker.connected,
                    l_gesture, r_gesture, l_conf, r_conf, fps)

            cv2.imshow("Gesture Car Controller", frame)
            if cv2.waitKey(1) & 0xFF == 27:   # ESC
                break

    broker.send_motor("stop")
    time.sleep(0.3)
    broker.shutdown()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
