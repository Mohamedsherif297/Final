#!/usr/bin/env python3
"""
MQTT Control - HiveMQ Cloud (WAN Access)
Control the car from anywhere in the world
"""
import sys
import ssl
import time
import paho.mqtt.client as mqtt
sys.path.insert(0, 'hardware')

from motor import Motor
from servo import Servo
from led import LED
from ultrasonic import Ultrasonic

# HiveMQ Cloud Configuration
BROKER_HOST = "78ed3eab06c348d0948ef7681cf4a377.s1.eu.hivemq.cloud"
BROKER_PORT = 8883  # TLS port
USERNAME = "mohamed"
PASSWORD = "P@ssw0rd"
CLIENT_ID = "raspi-car"

# MQTT Topics
TOPIC_MOTOR = "dev/motor"
TOPIC_SERVO = "dev/servo"
TOPIC_LED = "dev/led"
TOPIC_COMMANDS = "dev/commands"
TOPIC_STATUS = "dev/status"
TOPIC_SENSORS = "sensors/distance"

# Hardware
motor = None
servo = None
led = None
ultrasonic = None

def on_connect(client, userdata, flags, rc):
    """Called when connected to MQTT broker"""
    if rc == 0:
        print(f"[MQTT] ✅ Connected to HiveMQ Cloud!")
        
        # Subscribe to command topics
        client.subscribe(TOPIC_MOTOR)
        client.subscribe(TOPIC_SERVO)
        client.subscribe(TOPIC_LED)
        client.subscribe(TOPIC_COMMANDS)
        
        print(f"[MQTT] Subscribed to topics")
        
        # Send online status
        client.publish(TOPIC_STATUS, "online", qos=1)
        
        # Set LED to green (ready)
        if led:
            led.set_color(0, 255, 0)
    else:
        print(f"[MQTT] ❌ Connection failed with code {rc}")

def on_disconnect(client, userdata, rc):
    """Called when disconnected"""
    print(f"[MQTT] Disconnected (code: {rc})")
    if led:
        led.set_color(255, 0, 0)  # Red = disconnected

def on_message(client, userdata, msg):
    """Handle incoming MQTT messages"""
    try:
        topic = msg.topic
        payload = msg.payload.decode()
        
        print(f"[MQTT] {topic}: {payload}")
        
        # Parse JSON if needed
        import json
        try:
            data = json.loads(payload)
        except:
            data = {"command": payload}
        
        # Route to handlers
        if topic == TOPIC_MOTOR:
            handle_motor(data)
        elif topic == TOPIC_SERVO:
            handle_servo(data)
        elif topic == TOPIC_LED:
            handle_led(data)
        elif topic == TOPIC_COMMANDS:
            handle_command(data)
            
    except Exception as e:
        print(f"[MQTT] Error: {e}")

def handle_motor(data):
    """Handle motor commands"""
    direction = data.get("direction", "")
    speed = data.get("speed", 70)
    
    if direction == "forward":
        motor.forward(speed)
        led.set_color(0, 0, 255)  # Blue
    elif direction == "backward":
        motor.backward(speed)
        led.set_color(255, 255, 0)  # Yellow
    elif direction == "left":
        motor.left(speed)
        led.set_color(255, 0, 255)  # Magenta
    elif direction == "right":
        motor.right(speed)
        led.set_color(0, 255, 255)  # Cyan
    elif direction == "stop":
        motor.stop()
        led.set_color(0, 255, 0)  # Green

def handle_servo(data):
    """Handle servo commands"""
    pan = data.get("pan")
    tilt = data.get("tilt")
    
    if pan is not None or tilt is not None:
        servo.set_angle(pan=pan, tilt=tilt)

def handle_led(data):
    """Handle LED commands"""
    red = data.get("red", 0)
    green = data.get("green", 0)
    blue = data.get("blue", 0)
    
    led.set_color(red, green, blue)

def handle_command(data):
    """Handle general commands"""
    command = data.get("command", "")
    
    if command == "status":
        # Send status
        distance = ultrasonic.get_distance()
        status = {
            "status": "online",
            "distance": distance,
            "timestamp": time.time()
        }
        import json
        client.publish(TOPIC_STATUS, json.dumps(status), qos=1)
    
    elif command == "center":
        servo.center()
    
    elif command == "stop_all":
        motor.stop()
        led.set_color(0, 255, 0)

def publish_sensors(client):
    """Publish sensor data periodically"""
    while True:
        try:
            distance = ultrasonic.get_distance()
            if distance:
                import json
                data = json.dumps({"distance": distance, "timestamp": time.time()})
                client.publish(TOPIC_SENSORS, data, qos=0)
            time.sleep(0.5)  # 2Hz
        except Exception as e:
            print(f"[Sensors] Error: {e}")
            time.sleep(1)

def main():
    global motor, servo, led, ultrasonic, client
    
    print("=" * 60)
    print("MQTT Control - HiveMQ Cloud (WAN Access)")
    print("=" * 60)
    print(f"Broker: {BROKER_HOST}:{BROKER_PORT}")
    print(f"Client ID: {CLIENT_ID}")
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
    
    led.set_color(255, 0, 0)  # Red = not connected
    print("[Hardware] Initialized ✓")
    
    # Setup MQTT client
    print("\n[MQTT] Connecting to HiveMQ Cloud...")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, CLIENT_ID)
    client.username_pw_set(USERNAME, PASSWORD)
    
    # Configure TLS
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)
    
    # Set callbacks
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    
    # Connect
    try:
        client.connect(BROKER_HOST, BROKER_PORT, 60)
    except Exception as e:
        print(f"[MQTT] Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check internet connection")
        print("2. Verify HiveMQ credentials")
        print("3. Check firewall (port 8883)")
        return 1
    
    # Start MQTT loop in background
    client.loop_start()
    
    # Start sensor publishing in background
    import threading
    sensor_thread = threading.Thread(target=publish_sensors, args=(client,), daemon=True)
    sensor_thread.start()
    
    print("\n[System] Running. Press Ctrl+C to exit.")
    print("=" * 60)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[System] Shutting down...")
    
    # Cleanup
    client.publish(TOPIC_STATUS, "offline", qos=1)
    client.loop_stop()
    client.disconnect()
    
    motor.cleanup()
    servo.cleanup()
    led.cleanup()
    
    print("[System] Shutdown complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())
