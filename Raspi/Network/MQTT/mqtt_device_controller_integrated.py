"""
Integrated MQTT Device Controller
Uses hardware_manager for professional hardware control with safety features
"""

import paho.mqtt.client as mqtt
import json
import time
import threading
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Drivers.hardware.managers.hardware_manager import hardware_manager
from Drivers.hardware.safety.emergency_stop import EmergencyTrigger


class MQTTDeviceController:
    """
    MQTT Device Controller with integrated hardware management
    
    Features:
    - Professional hardware control via hardware_manager
    - Emergency stop system
    - Watchdog monitoring
    - Sensor data publishing
    - Thread-safe operations
    """
    
    def __init__(self, broker_host="localhost", broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        
        # MQTT Topics
        self.TOPIC_COMMANDS = "dev/commands"
        self.TOPIC_STATUS = "dev/status"
        self.TOPIC_MOTOR = "dev/motor"
        self.TOPIC_LED = "dev/led"
        self.TOPIC_SERVO = "dev/servo"
        self.TOPIC_SENSORS = "sensors/ultrasonic"
        self.TOPIC_EMERGENCY = "emergency/alert"
        
        # MQTT Client setup
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # Status
        self.connected = False
        self.running = False
        self.start_time = None
        
        print(f"[MQTT] Device controller initialized for {broker_host}:{broker_port}")
    
    def initialize_hardware(self):
        """Initialize hardware manager"""
        try:
            print("[MQTT] Initializing hardware manager...")
            hardware_manager.initialize()
            
            # Register emergency callback
            hardware_manager.emergency_stop.register_callback(self._on_emergency)
            
            # Register obstacle detection callback
            hardware_manager.ultrasonic.register_obstacle_callback(self._on_obstacle_detected)
            
            print("[MQTT] Hardware initialized successfully")
            return True
            
        except Exception as e:
            print(f"[MQTT] Hardware initialization failed: {e}")
            return False
    
    def on_connect(self, client, userdata, flags, rc):
        """Handle MQTT connection"""
        if rc == 0:
            print(f"[MQTT] Connected to broker successfully")
            self.connected = True
            
            # Subscribe to command topics
            topics = [
                self.TOPIC_COMMANDS,
                self.TOPIC_MOTOR,
                self.TOPIC_LED,
                self.TOPIC_SERVO
            ]
            
            for topic in topics:
                client.subscribe(topic)
                print(f"[MQTT] Subscribed to {topic}")
            
            # Send online status
            self.send_status("online", "Device connected and ready")
            
            # Set status LED to idle
            try:
                hardware_manager.led.set_status_color('idle')
            except Exception as e:
                print(f"[MQTT] LED status warning: {e}")
            
            # Start sensor publishing
            self.start_sensor_publishing()
            
            # Start heartbeat thread
            self.start_heartbeat()
            
        else:
            print(f"[MQTT] Connection failed with code {rc}")
            self.connected = False
    
    def on_disconnect(self, client, userdata, rc):
        """Handle MQTT disconnection"""
        print(f"[MQTT] Disconnected from broker (code: {rc})")
        self.connected = False
    
    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages"""
        try:
            topic = msg.topic
            payload = msg.payload.decode()
            
            print(f"[MQTT] Received on {topic}: {payload}")
            
            # Parse JSON payload
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                data = {"command": payload}
            
            # Route message based on topic
            if topic == self.TOPIC_MOTOR:
                self.handle_motor_command(data)
            elif topic == self.TOPIC_LED:
                self.handle_led_command(data)
            elif topic == self.TOPIC_SERVO:
                self.handle_servo_command(data)
            elif topic == self.TOPIC_COMMANDS:
                self.handle_general_command(data)
            
        except Exception as e:
            print(f"[MQTT] Error processing message: {e}")
            self.send_status("error", f"Message processing error: {str(e)}")
    
    def handle_motor_command(self, data):
        """Handle motor control commands"""
        try:
            direction = data.get("direction")
            speed = data.get("speed", 70)
            
            if not direction:
                self.send_status("error", "Motor command missing 'direction' field")
                return
            
            # Validate direction
            valid_directions = ["forward", "backward", "left", "right", "stop"]
            if direction not in valid_directions:
                self.send_status("error", f"Invalid direction: {direction}")
                return
            
            # Validate speed
            if not (0 <= speed <= 100):
                self.send_status("error", f"Invalid speed: {speed}")
                return
            
            # Execute motor command using hardware_manager
            if direction == "forward":
                hardware_manager.motor.move_forward(speed)
                hardware_manager.led.set_status_color('moving')
            
            elif direction == "backward":
                hardware_manager.motor.move_backward(speed)
                hardware_manager.led.set_status_color('moving')
            
            elif direction == "left":
                hardware_manager.motor.turn_left(speed)
                hardware_manager.led.set_color(255, 255, 0)  # Yellow
            
            elif direction == "right":
                hardware_manager.motor.turn_right(speed)
                hardware_manager.led.set_color(255, 255, 0)  # Yellow
            
            elif direction == "stop":
                hardware_manager.motor.stop()
                hardware_manager.led.set_status_color('idle')
            
            # Send heartbeat to watchdog
            hardware_manager.heartbeat('motor')
            
            # Send confirmation
            self.send_status("motor_moved", {
                "direction": direction,
                "speed": speed,
                "timestamp": time.time()
            })
            
        except Exception as e:
            print(f"[MQTT] Motor command error: {e}")
            self.send_status("error", f"Motor command failed: {str(e)}")
    
    def handle_led_command(self, data):
        """Handle LED control commands"""
        try:
            action = data.get("action")
            
            if not action:
                self.send_status("error", "LED command missing 'action' field")
                return
            
            if action == "set_color":
                color = data.get("color", "off")
                hardware_manager.led.set_status_color(color)
            
            elif action == "set_rgb":
                red = data.get("red", 0)
                green = data.get("green", 0)
                blue = data.get("blue", 0)
                hardware_manager.led.set_color(red, green, blue)
            
            elif action == "start_effect":
                from Drivers.hardware.led.led_effects import LEDEffect
                effect_name = data.get("effect", "blink")
                effect = LEDEffect[effect_name.upper()]
                hardware_manager.led.start_effect(effect)
            
            elif action == "stop_effect":
                hardware_manager.led.stop_effect()
            
            elif action == "off":
                hardware_manager.led.set_color(0, 0, 0)
            
            else:
                self.send_status("error", f"Unknown LED action: {action}")
                return
            
            # Send confirmation
            self.send_status("led_controlled", {
                "action": action,
                "timestamp": time.time()
            })
            
        except Exception as e:
            print(f"[MQTT] LED command error: {e}")
            self.send_status("error", f"LED command failed: {str(e)}")
    
    def handle_servo_command(self, data):
        """Handle servo control commands"""
        try:
            action = data.get("action")
            
            if not action:
                self.send_status("error", "Servo command missing 'action' field")
                return
            
            if action == "set_angle":
                pan = data.get("pan")
                tilt = data.get("tilt")
                hardware_manager.servo.set_angle(pan=pan, tilt=tilt)
            
            elif action == "center":
                hardware_manager.servo.center()
            
            elif action == "preset":
                preset_name = data.get("preset", "center")
                hardware_manager.servo.move_to_preset(preset_name)
            
            elif action == "scan":
                hardware_manager.servo.scan_horizontal()
            
            else:
                self.send_status("error", f"Unknown servo action: {action}")
                return
            
            # Send heartbeat
            hardware_manager.heartbeat('servo')
            
            # Send confirmation
            self.send_status("servo_moved", {
                "action": action,
                "timestamp": time.time()
            })
            
        except Exception as e:
            print(f"[MQTT] Servo command error: {e}")
            self.send_status("error", f"Servo command failed: {str(e)}")
    
    def handle_general_command(self, data):
        """Handle general system commands"""
        try:
            command = data.get("command", "")
            
            if command == "status":
                self.send_device_status()
            
            elif command == "stop_all":
                hardware_manager.motor.stop()
                hardware_manager.led.set_status_color('idle')
                self.send_status("stopped", "All devices stopped")
            
            elif command == "emergency_stop":
                hardware_manager.trigger_emergency(
                    EmergencyTrigger.MANUAL_BUTTON,
                    "Manual emergency stop via MQTT"
                )
            
            elif command == "reset_emergency":
                hardware_manager.reset_emergency()
                self.send_status("emergency_reset", "Emergency stop reset")
            
            elif command == "get_hardware_status":
                status = hardware_manager.get_status()
                self.send_status("hardware_status", status)
            
            else:
                self.send_status("error", f"Unknown command: {command}")
                
        except Exception as e:
            print(f"[MQTT] General command error: {e}")
            self.send_status("error", f"Command failed: {str(e)}")
    
    def start_sensor_publishing(self):
        """Start publishing sensor data to MQTT"""
        def publish_loop():
            while self.running and self.connected:
                try:
                    # Get distance from ultrasonic sensor
                    distance = hardware_manager.ultrasonic.get_filtered_distance()
                    
                    # Publish to MQTT
                    self.client.publish(self.TOPIC_SENSORS, json.dumps({
                        "distance": distance,
                        "timestamp": time.time()
                    }))
                    
                    # Send heartbeat to watchdog
                    hardware_manager.heartbeat('ultrasonic')
                    
                except Exception as e:
                    print(f"[MQTT] Sensor publish error: {e}")
                
                time.sleep(0.1)  # 10Hz
        
        threading.Thread(target=publish_loop, daemon=True).start()
        print("[MQTT] Sensor publishing started")
    
    def start_heartbeat(self):
        """Start heartbeat thread for watchdog"""
        def heartbeat_loop():
            while self.running:
                try:
                    # Send heartbeats to all components
                    hardware_manager.heartbeat('motor')
                    hardware_manager.heartbeat('servo')
                    hardware_manager.heartbeat('ultrasonic')
                    hardware_manager.heartbeat('camera')
                    
                except Exception as e:
                    print(f"[MQTT] Heartbeat error: {e}")
                
                time.sleep(1)  # 1Hz
        
        threading.Thread(target=heartbeat_loop, daemon=True).start()
        print("[MQTT] Heartbeat started")
    
    def _on_emergency(self, trigger, message):
        """Handle hardware emergency events"""
        print(f"[EMERGENCY] {trigger.value}: {message}")
        
        # Publish emergency alert to MQTT
        if self.connected:
            try:
                self.client.publish(self.TOPIC_EMERGENCY, json.dumps({
                    "trigger": trigger.value,
                    "message": message,
                    "timestamp": time.time()
                }))
            except Exception as e:
                print(f"[MQTT] Emergency publish error: {e}")
    
    def _on_obstacle_detected(self, distance):
        """Handle obstacle detection"""
        print(f"[OBSTACLE] Detected at {distance}cm")
        
        # Publish obstacle alert
        if self.connected:
            try:
                self.client.publish("sensors/obstacle", json.dumps({
                    "distance": distance,
                    "timestamp": time.time()
                }))
            except Exception as e:
                print(f"[MQTT] Obstacle publish error: {e}")
    
    def send_status(self, status_type, message):
        """Send status message via MQTT"""
        if self.connected:
            status_data = {
                "type": status_type,
                "message": message,
                "timestamp": time.time()
            }
            
            payload = json.dumps(status_data)
            self.client.publish(self.TOPIC_STATUS, payload)
            print(f"[MQTT] Status sent: {status_type}")
    
    def send_device_status(self):
        """Send comprehensive device status"""
        try:
            hardware_status = hardware_manager.get_status()
            
            status = {
                "device": "surveillance_car",
                "connected": self.connected,
                "running": self.running,
                "uptime": time.time() - self.start_time if self.start_time else 0,
                "hardware": hardware_status,
                "timestamp": time.time()
            }
            
            payload = json.dumps(status)
            self.client.publish(self.TOPIC_STATUS, payload)
            print("[MQTT] Device status sent")
            
        except Exception as e:
            print(f"[MQTT] Status send error: {e}")
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            print(f"[MQTT] Connecting to {self.broker_host}:{self.broker_port}...")
            self.client.connect(self.broker_host, self.broker_port, 60)
            return True
        except Exception as e:
            print(f"[MQTT] Connection error: {e}")
            return False
    
    def start(self):
        """Start the MQTT device controller"""
        # Initialize hardware first
        if not self.initialize_hardware():
            print("[MQTT] Failed to initialize hardware - exiting")
            return False
        
        # Connect to MQTT broker
        if self.connect():
            self.running = True
            self.start_time = time.time()
            
            print("[MQTT] Starting MQTT loop...")
            # Use loop_start() instead of loop_forever() for better control
            self.client.loop_start()
            
            # Keep running until stopped
            try:
                while self.running:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\n[MQTT] Keyboard interrupt in MQTT thread")
            finally:
                self.client.loop_stop()
        else:
            print("[MQTT] Failed to connect to broker")
            return False
    
    def stop(self):
        """Stop the device controller"""
        print("[MQTT] Stopping device controller...")
        self.running = False
        
        # Send offline status
        if self.connected:
            try:
                self.send_status("offline", "Device shutting down")
            except:
                pass
        
        # Disconnect MQTT
        try:
            self.client.disconnect()
        except:
            pass
        
        # Cleanup hardware
        try:
            hardware_manager.cleanup()
        except Exception as e:
            print(f"[MQTT] Hardware cleanup warning: {e}")
        
        print("[MQTT] Device controller stopped")


def main():
    """Main entry point"""
    # Configuration
    BROKER_HOST = "localhost"  # Change to your MQTT broker IP
    BROKER_PORT = 1883
    
    print("=" * 60)
    print("MQTT Device Controller - Integrated Hardware Management")
    print("=" * 60)
    print(f"Broker: {BROKER_HOST}:{BROKER_PORT}")
    print("\nTopics:")
    print("  - dev/motor      (motor commands)")
    print("  - dev/led        (LED commands)")
    print("  - dev/servo      (servo commands)")
    print("  - dev/commands   (general commands)")
    print("  - dev/status     (status messages)")
    print("  - sensors/*      (sensor data)")
    print("  - emergency/*    (emergency alerts)")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)
    
    controller = MQTTDeviceController(BROKER_HOST, BROKER_PORT)
    
    try:
        controller.start()
    except KeyboardInterrupt:
        print("\n[SYSTEM] Shutting down...")
    finally:
        controller.stop()


if __name__ == "__main__":
    main()
