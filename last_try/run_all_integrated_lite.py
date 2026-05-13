#!/usr/bin/env python3
"""
Integrated Surveillance Car System - LITE VERSION
MQTT Control + WebSocket Streaming + AI Face Tracking (Detection Only)
Uses only MediaPipe - no face_recognition (much faster installation!)
"""
import sys
import os
import asyncio
import ssl
import time
import threading
import websockets
import cv2
import json
sys.path.insert(0, 'hardware')

import paho.mqtt.client as mqtt
from motor import Motor
from servo import Servo
from led import LED
from ultrasonic import Ultrasonic
from system_state import SystemState, ControlMode
from ai_controller_lite import AIControllerLite  # Lite version!

# ========== MQTT Configuration ==========
MQTT_BROKER = "78ed3eab06c348d0948ef7681cf4a377.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "mohamed"
MQTT_PASS = "P@ssw0rd"
MQTT_CLIENT_ID = "raspi-car"

# ========== WebSocket Configuration ==========
WS_HOST = "0.0.0.0"
WS_PORT = 8765
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
VIDEO_FPS = 20
JPEG_QUALITY = 65

# ========== Hardware ==========
motor = None
servo = None
led = None
ultrasonic = None

# ========== System State ==========
system_state = None
ai_controller = None

# ========== WebSocket Clients ==========
ws_clients = set()
frame_data_latest = None
frame_lock = threading.Lock()

# ========== MQTT Handlers ==========
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[MQTT] ✅ Connected to HiveMQ Cloud")
        client.subscribe("dev/motor")
        client.subscribe("dev/servo")
        client.subscribe("dev/led")
        client.subscribe("dev/commands")
        client.subscribe("dev/mode")
        client.publish("dev/status", json.dumps({"status": "online", "mode": "manual", "version": "lite"}), qos=1)
        if led:
            led.set_color(0, 255, 0)
    else:
        print(f"[MQTT] ❌ Connection failed: {rc}")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        topic = msg.topic
        
        if topic == "dev/motor":
            handle_motor(data)
        elif topic == "dev/servo":
            handle_servo(data)
        elif topic == "dev/led":
            handle_led(data)
        elif topic == "dev/commands":
            handle_command(data)
        elif topic == "dev/mode":
            handle_mode(data)
    except Exception as e:
        print(f"[MQTT] Error: {e}")

def handle_mode(data):
    """Handle mode switching commands"""
    mode = data.get("mode", "")
    
    if mode == "manual":
        system_state.set_mode("manual")
        print("[Mode] Switched to MANUAL control")
        if led:
            led.set_color(0, 255, 0)
    elif mode == "ai_follow":
        system_state.set_mode("ai_follow")
        print("[Mode] Switched to AI FOLLOW mode (Lite - follows any person)")
        if led:
            led.set_color(255, 0, 255)
    else:
        print(f"[Mode] Unknown mode: {mode}")

def handle_motor(data):
    """Handle manual motor commands (only in MANUAL mode)"""
    if system_state.mode != ControlMode.MANUAL:
        print("[Motor] Ignoring manual command - not in MANUAL mode")
        return
    
    direction = data.get("direction", "")
    speed = data.get("speed", 70)
    system_state.send_motor_command(direction, speed, source="manual")

def handle_servo(data):
    pan = data.get("pan")
    tilt = data.get("tilt")
    if pan is not None or tilt is not None:
        servo.set_angle(pan=pan, tilt=tilt)

def handle_led(data):
    red = data.get("red", 0)
    green = data.get("green", 0)
    blue = data.get("blue", 0)
    led.set_color(red, green, blue)

def handle_command(data):
    command = data.get("command", "")
    
    if command == "center":
        servo.center()
    elif command == "stop_all":
        motor.stop()
        led.set_color(0, 255, 0)
    elif command == "emergency_stop":
        system_state.trigger_emergency_stop()
        motor.stop()
        led.set_color(255, 0, 0)
    elif command == "reset_emergency":
        system_state.reset_emergency_stop()
        led.set_color(0, 255, 0)

# ========== Motor Command Processor ==========
def motor_command_processor():
    """Process motor commands from queue (AI or Manual)"""
    print("[MotorProc] Started")
    
    try:
        os.sched_setaffinity(0, {0})
        print("[MotorProc] Pinned to core 0")
    except Exception as e:
        print(f"[MotorProc] Could not pin to core: {e}")
    
    while not system_state.shutdown.is_set():
        if system_state.emergency_stop.is_set():
            motor.stop()
            time.sleep(0.1)
            continue
        
        cmd = system_state.get_motor_command(timeout=0.05)
        
        if cmd is None:
            continue
        
        with system_state.motor_lock:
            if cmd.direction == "forward":
                motor.forward(cmd.speed)
                if cmd.source == "ai":
                    led.set_color(0, 0, 255)
            elif cmd.direction == "backward":
                motor.backward(cmd.speed)
                if cmd.source == "ai":
                    led.set_color(255, 255, 0)
            elif cmd.direction == "left":
                motor.left(cmd.speed)
                if cmd.source == "ai":
                    led.set_color(255, 0, 255)
            elif cmd.direction == "right":
                motor.right(cmd.speed)
                if cmd.source == "ai":
                    led.set_color(0, 255, 255)
            elif cmd.direction == "stop":
                motor.stop()
    
    print("[MotorProc] Stopped")

# ========== WebSocket Handlers ==========
async def handle_ws_client(websocket):
    client_addr = websocket.remote_address
    print(f"[WebSocket] Client connected: {client_addr}")
    ws_clients.add(websocket)
    
    try:
        welcome = json.dumps({
            "event": "connected",
            "server": "surveillance-car-ai-lite",
            "mode": system_state.mode.value,
            "version": "lite"
        })
        await websocket.send(b'\x00' + welcome.encode())
        
        async for message in websocket:
            pass
    except websockets.exceptions.ConnectionClosedOK:
        print(f"[WebSocket] Client disconnected (clean): {client_addr}")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"[WebSocket] Client disconnected (error): {client_addr} - {e}")
    except Exception as e:
        print(f"[WebSocket] Client error: {client_addr} - {e}")
    finally:
        ws_clients.discard(websocket)
        print(f"[WebSocket] Client cleaned up: {client_addr}")

async def frame_broadcaster():
    """Continuously broadcast frames to all clients"""
    print("[Broadcaster] Started")
    global frame_data_latest, ws_clients
    
    while True:
        try:
            await asyncio.sleep(0.05)
            
            if not ws_clients or frame_data_latest is None:
                continue
            
            with frame_lock:
                frame_data = frame_data_latest
            
            if frame_data is None:
                continue
            
            tagged_frame = b'\x01' + frame_data
            disconnected = set()
            
            for client in list(ws_clients):
                try:
                    await client.send(tagged_frame)
                except Exception as e:
                    print(f"[WebSocket] Send error: {e}")
                    disconnected.add(client)
            
            ws_clients -= disconnected
            
        except Exception as e:
            print(f"[Broadcaster] Error: {e}")
            await asyncio.sleep(0.1)

async def ai_status_broadcaster():
    """Broadcast AI status to dashboard"""
    print("[AI Status] Broadcaster started")
    global ws_clients
    
    while True:
        try:
            await asyncio.sleep(0.5)
            
            if not ws_clients:
                continue
            
            ai_status = system_state.get_ai_status()
            
            status_msg = json.dumps({
                "event": "ai_status",
                "mode": system_state.mode.value,
                "tracking": ai_status.tracking,
                "confidence": ai_status.confidence,
                "action": ai_status.action,
                "face_detected": ai_status.face_detected,
                "body_detected": ai_status.body_detected
            })
            
            tagged_msg = b'\x00' + status_msg.encode()
            disconnected = set()
            
            for client in list(ws_clients):
                try:
                    await client.send(tagged_msg)
                except Exception:
                    disconnected.add(client)
            
            ws_clients -= disconnected
            
        except Exception as e:
            print(f"[AI Status] Error: {e}")
            await asyncio.sleep(0.1)

# ========== Camera Thread ==========
def camera_loop():
    global frame_data_latest
    
    print("[Camera] Opening camera...")
    camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        print("[Camera] Failed to open")
        return
    
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
    camera.set(cv2.CAP_PROP_FPS, VIDEO_FPS)
    
    print(f"[Camera] Streaming {VIDEO_WIDTH}x{VIDEO_HEIGHT} @ {VIDEO_FPS}fps")
    
    try:
        os.sched_setaffinity(0, {0})
        print("[Camera] Pinned to core 0")
    except Exception as e:
        print(f"[Camera] Could not pin to core: {e}")
    
    frame_interval = 1.0 / VIDEO_FPS
    next_frame_time = time.time()
    frame_count = 0
    last_log_time = time.time()
    
    while not system_state.shutdown.is_set():
        ret, frame = camera.read()
        if not ret:
            time.sleep(0.1)
            continue
        
        if ai_controller:
            ai_controller.set_frame(frame)
        
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
        ret, buffer = cv2.imencode('.jpg', frame, encode_params)
        
        if ret:
            with frame_lock:
                frame_data_latest = buffer.tobytes()
            
            frame_count += 1
            
            now = time.time()
            if now - last_log_time >= 5:
                fps = frame_count / (now - last_log_time)
                mode_str = system_state.mode.value
                print(f"[Camera] {fps:.1f} fps | {len(ws_clients)} client(s) | Mode: {mode_str}")
                frame_count = 0
                last_log_time = now
        
        next_frame_time += frame_interval
        sleep_time = next_frame_time - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            next_frame_time = time.time()
    
    camera.release()
    print("[Camera] Stopped")

# ========== Main ==========
async def main():
    global motor, servo, led, ultrasonic, system_state, ai_controller
    
    print("=" * 60)
    print("Surveillance Car - AI Lite System")
    print("=" * 60)
    print(f"MQTT: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"WebSocket: ws://{WS_HOST}:{WS_PORT}")
    print("AI: Lite mode (follows any person, no recognition)")
    print("=" * 60)
    
    print("\n[System] Initializing state manager...")
    system_state = SystemState()
    
    print("\n[Hardware] Initializing...")
    motor = Motor()
    servo = Servo()
    led = LED()
    ultrasonic = Ultrasonic()
    
    motor.setup()
    servo.setup()
    led.setup()
    ultrasonic.setup()
    
    led.set_color(255, 0, 0)
    print("[Hardware] ✓ Initialized")
    
    print("\n[AI] Initializing AI controller (Lite mode)...")
    ai_controller = AIControllerLite(system_state, speed=60)
    ai_controller.start()
    
    print("\n[MQTT] Connecting...")
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, MQTT_CLIENT_ID)
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
    mqtt_client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    
    motor_thread = threading.Thread(target=motor_command_processor, daemon=True)
    motor_thread.start()
    
    camera_thread = threading.Thread(target=camera_loop, daemon=True)
    camera_thread.start()
    
    broadcaster_task = asyncio.create_task(frame_broadcaster())
    ai_status_task = asyncio.create_task(ai_status_broadcaster())
    
    print(f"\n[WebSocket] Starting server on ws://{WS_HOST}:{WS_PORT}")
    print("\n[System] ✓ All systems running (Lite mode)")
    print("=" * 60)
    print("\n💡 AI Lite Mode:")
    print("   • Follows ANY person (no recognition)")
    print("   • Much faster, lighter on CPU")
    print("   • Only MediaPipe required")
    print("=" * 60)
    
    async with websockets.serve(
        handle_ws_client,
        WS_HOST,
        WS_PORT,
        ping_interval=20,
        ping_timeout=20,
    ):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[System] Shutting down...")
        if system_state:
            system_state.request_shutdown()
        time.sleep(1)
        if ai_controller:
            ai_controller.stop()
        if motor:
            motor.cleanup()
        if servo:
            servo.cleanup()
        if led:
            led.cleanup()
        print("[System] Shutdown complete")
