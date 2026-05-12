#!/usr/bin/env python3
"""
Run All - MQTT Control + WebSocket Streaming
Complete surveillance car system
"""
import sys
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

# ========== WebSocket Clients ==========
ws_clients = set()

# ========== MQTT Handlers ==========
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[MQTT] ✅ Connected to HiveMQ Cloud")
        client.subscribe("dev/motor")
        client.subscribe("dev/servo")
        client.subscribe("dev/led")
        client.subscribe("dev/commands")
        client.publish("dev/status", "online", qos=1)
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
    except Exception as e:
        print(f"[MQTT] Error: {e}")

def handle_motor(data):
    direction = data.get("direction", "")
    speed = data.get("speed", 70)
    
    if direction == "forward":
        motor.forward(speed)
        led.set_color(0, 0, 255)
    elif direction == "backward":
        motor.backward(speed)
        led.set_color(255, 255, 0)
    elif direction == "left":
        motor.left(speed)
        led.set_color(255, 0, 255)
    elif direction == "right":
        motor.right(speed)
        led.set_color(0, 255, 255)
    elif direction == "stop":
        motor.stop()
        led.set_color(0, 255, 0)

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

# ========== WebSocket Handlers ==========
async def handle_ws_client(websocket):
    client_addr = websocket.remote_address
    print(f"[WebSocket] Client connected: {client_addr}")
    ws_clients.add(websocket)
    
    try:
        welcome = json.dumps({"event": "connected", "server": "surveillance-car"})
        await websocket.send(b'\x00' + welcome.encode())
        
        async for message in websocket:
            pass  # Handle incoming if needed
    except:
        pass
    finally:
        ws_clients.discard(websocket)
        print(f"[WebSocket] Client disconnected: {client_addr}")

async def broadcast_frame(frame_data):
    if not ws_clients:
        return
    
    tagged_frame = b'\x01' + frame_data
    disconnected = set()
    
    for client in ws_clients:
        try:
            await client.send(tagged_frame)
        except Exception as e:
            print(f"[WebSocket] Error sending frame: {e}")
            disconnected.add(client)
    
    ws_clients -= disconnected

# ========== Camera Thread ==========
def camera_loop(loop):
    print("[Camera] Opening camera...")
    camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        print("[Camera] Failed to open")
        return
    
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
    camera.set(cv2.CAP_PROP_FPS, VIDEO_FPS)
    
    print(f"[Camera] Streaming {VIDEO_WIDTH}x{VIDEO_HEIGHT} @ {VIDEO_FPS}fps")
    
    frame_interval = 1.0 / VIDEO_FPS
    next_frame_time = time.time()
    frame_count = 0
    last_log_time = time.time()
    
    while True:
        ret, frame = camera.read()
        if not ret:
            time.sleep(0.1)
            continue
        
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
        ret, buffer = cv2.imencode('.jpg', frame, encode_params)
        
        if ret:
            frame_data = buffer.tobytes()
            asyncio.run_coroutine_threadsafe(broadcast_frame(frame_data), loop)
            frame_count += 1
            
            # Log stats every 5 seconds
            now = time.time()
            if now - last_log_time >= 5:
                fps = frame_count / (now - last_log_time)
                print(f"[Camera] {fps:.1f} fps | {len(ws_clients)} client(s) | {len(frame_data)} bytes/frame")
                frame_count = 0
                last_log_time = now
        
        next_frame_time += frame_interval
        sleep_time = next_frame_time - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            next_frame_time = time.time()

# ========== Main ==========
async def main():
    global motor, servo, led, ultrasonic
    
    print("=" * 60)
    print("Surveillance Car - Full System")
    print("=" * 60)
    print(f"MQTT: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"WebSocket: ws://{WS_HOST}:{WS_PORT}")
    print("=" * 60)
    
    # Initialize hardware
    print("\n[Hardware] Initializing...")
    motor = Motor()
    servo = Servo()
    led = LED()
    ultrasonic = Ultrasonic()
    
    motor.setup()
    servo.setup()
    led.setup()
    ultrasonic.setup()
    
    led.set_color(255, 0, 0)  # Red = starting
    print("[Hardware] ✓ Initialized")
    
    # Setup MQTT
    print("\n[MQTT] Connecting...")
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, MQTT_CLIENT_ID)
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
    mqtt_client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    
    # Start camera thread
    loop = asyncio.get_running_loop()
    camera_thread = threading.Thread(target=camera_loop, args=(loop,), daemon=True)
    camera_thread.start()
    
    # Start WebSocket server
    print(f"\n[WebSocket] Starting server on ws://{WS_HOST}:{WS_PORT}")
    print("\n[System] ✓ All systems running")
    print("=" * 60)
    
    async with websockets.serve(handle_ws_client, WS_HOST, WS_PORT):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[System] Shutting down...")
        if motor:
            motor.cleanup()
        if servo:
            servo.cleanup()
        if led:
            led.cleanup()
        print("[System] Shutdown complete")
