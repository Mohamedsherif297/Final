import paho.mqtt.client as mqtt
import json
import time
import threading
from simple_motor_controller import SimpleMotorController
from led_controller import LEDController

class MQTTDeviceController:
    def __init__(self, broker_host="localhost", broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        
        # Initialize hardware controllers
        self.motor_controller = SimpleMotorController()
        self.led_controller = LEDController()
        
        # MQTT Topics
        self.TOPIC_COMMANDS = "dev/commands"
        self.TOPIC_STATUS = "dev/status"
        self.TOPIC_MOTOR = "dev/motor"
        self.TOPIC_LED = "dev/led"
        
        # MQTT Client setup
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # Status
        self.connected = False
        self.running = False
        
        print(f"[MQTT] Device controller initialized for {broker_host}:{broker_port}")
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[MQTT] Connected to broker successfully")
            self.connected = True
            
            # Subscribe to command topics
            topics = [
                self.TOPIC_COMMANDS,
                self.TOPIC_MOTOR,
                self.TOPIC_LED
            ]
            
            for topic in topics:
                client.subscribe(topic)
                print(f"[MQTT] Subscribed to {topic}")
            
            # Send online status
            self.send_status("online", "Device connected and ready")
            
            # Turn on status LED to show connection
            self.led_controller.set_led('status', True)
            
        else:
            print(f"[MQTT] Connection failed with code {rc}")
            self.connected = False
    
    def on_disconnect(self, client, userdata, rc):
        print(f"[MQTT] Disconnected from broker (code: {rc})")
        self.connected = False
        
        # Turn off status LED
        try:
            self.led_controller.set_led('status', False)
        except:
            pass
    
    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = msg.payload.decode()
            
            print(f"[MQTT] Received message on {topic}: {payload}")
            
            # Parse JSON payload
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                # Handle simple string commands
                data = {"command": payload}
            
            # Route message based on topic
            if topic == self.TOPIC_MOTOR:
                self.handle_motor_command(data)
            elif topic == self.TOPIC_LED:
                self.handle_led_command(data)
            elif topic == self.TOPIC_COMMANDS:
                self.handle_general_command(data)
            
        except Exception as e:
            print(f"[MQTT] Error processing message: {e}")
            self.send_status("error", f"Message processing error: {str(e)}")
    
    def handle_motor_command(self, data):
        """Handle motor control commands"""
        try:
            if "direction" in data:
                direction = data["direction"]
                speed = data.get("speed", 50)
                
                # Validate direction
                valid_directions = ["forward", "backward", "left", "right", "stop"]
                if direction not in valid_directions:
                    self.send_status("error", f"Invalid direction: {direction}")
                    return
                
                # Validate speed
                if not (0 <= speed <= 100):
                    self.send_status("error", f"Invalid speed: {speed}")
                    return
                
                # Execute motor command
                self.motor_controller.move(direction, speed)
                
                # Send confirmation
                self.send_status("motor_moved", {
                    "direction": direction,
                    "speed": speed,
                    "timestamp": time.time()
                })
                
                # Visual feedback with LEDs
                if direction == "forward":
                    self.led_controller.set_color("green")
                elif direction == "backward":
                    self.led_controller.set_color("red")
                elif direction in ["left", "right"]:
                    self.led_controller.set_color("yellow")
                else:  # stop
                    self.led_controller.set_color("off")
            
            else:
                self.send_status("error", "Motor command missing 'direction' field")
                
        except Exception as e:
            print(f"[MQTT] Motor command error: {e}")
            self.send_status("error", f"Motor command failed: {str(e)}")
    
    def handle_led_command(self, data):
        """Handle LED control commands"""
        try:
            if "action" in data:
                action = data["action"]
                
                if action == "set_led":
                    led_name = data.get("led", "status")
                    state = data.get("state", False)
                    self.led_controller.set_led(led_name, state)
                
                elif action == "set_color":
                    color = data.get("color", "off")
                    self.led_controller.set_color(color)
                
                elif action == "set_rgb":
                    red = data.get("red", 0)
                    green = data.get("green", 0)
                    blue = data.get("blue", 0)
                    self.led_controller.set_rgb(red, green, blue)
                
                elif action == "blink":
                    led_name = data.get("led", "status")
                    interval = data.get("interval", 0.5)
                    duration = data.get("duration", None)
                    self.led_controller.blink_led(led_name, interval, duration)
                
                elif action == "stop_blink":
                    self.led_controller.stop_blink()
                
                elif action == "all_off":
                    self.led_controller.all_off()
                
                elif action == "test":
                    threading.Thread(target=self.led_controller.test_sequence, daemon=True).start()
                
                else:
                    self.send_status("error", f"Unknown LED action: {action}")
                    return
                
                # Send confirmation
                self.send_status("led_controlled", {
                    "action": action,
                    "data": data,
                    "timestamp": time.time()
                })
            
            else:
                self.send_status("error", "LED command missing 'action' field")
                
        except Exception as e:
            print(f"[MQTT] LED command error: {e}")
            self.send_status("error", f"LED command failed: {str(e)}")
    
    def handle_general_command(self, data):
        """Handle general system commands"""
        try:
            command = data.get("command", "")
            
            if command == "status":
                self.send_device_status()
            
            elif command == "stop_all":
                self.motor_controller.move("stop")
                self.led_controller.all_off()
                self.send_status("stopped", "All devices stopped")
            
            elif command == "test_motors":
                threading.Thread(target=self.test_motors, daemon=True).start()
            
            elif command == "test_leds":
                threading.Thread(target=self.led_controller.test_sequence, daemon=True).start()
            
            elif command == "emergency_stop":
                self.emergency_stop()
            
            else:
                self.send_status("error", f"Unknown command: {command}")
                
        except Exception as e:
            print(f"[MQTT] General command error: {e}")
            self.send_status("error", f"Command failed: {str(e)}")
    
    def test_motors(self):
        """Test motor sequence"""
        print("[TEST] Starting motor test sequence...")
        directions = ["forward", "backward", "left", "right", "stop"]
        
        for direction in directions:
            self.motor_controller.move(direction, 50)
            time.sleep(1)
        
        self.send_status("test_complete", "Motor test sequence finished")
    
    def emergency_stop(self):
        """Emergency stop all devices"""
        print("[EMERGENCY] Emergency stop activated!")
        
        # Stop motors
        self.motor_controller.move("stop")
        
        # Flash red LED
        self.led_controller.blink_led("red", 0.1, 3)
        
        self.send_status("emergency_stop", "Emergency stop activated")
    
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
            print(f"[MQTT] Status sent: {status_type} - {message}")
    
    def send_device_status(self):
        """Send comprehensive device status"""
        status = {
            "device": "raspberry_pi_controller",
            "connected": self.connected,
            "running": self.running,
            "timestamp": time.time(),
            "uptime": time.time() - self.start_time if hasattr(self, 'start_time') else 0
        }
        
        payload = json.dumps(status)
        self.client.publish(self.TOPIC_STATUS, payload)
    
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
        if self.connect():
            self.running = True
            self.start_time = time.time()
            
            print("[MQTT] Starting MQTT loop...")
            self.client.loop_forever()
        else:
            print("[MQTT] Failed to connect to broker")
    
    def stop(self):
        """Stop the device controller"""
        print("[MQTT] Stopping device controller...")
        self.running = False
        
        try:
            # Stop all devices first
            self.motor_controller.move("stop")
        except Exception as e:
            print(f"[MQTT] Motor stop warning: {e}")
        
        try:
            self.led_controller.all_off()
        except Exception as e:
            print(f"[MQTT] LED stop warning: {e}")
        
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
        
        # Cleanup hardware with error handling
        try:
            self.motor_controller.cleanup()
        except Exception as e:
            print(f"[MQTT] Motor cleanup warning: {e}")
        
        try:
            self.led_controller.cleanup()
        except Exception as e:
            print(f"[MQTT] LED cleanup warning: {e}")
        
        print("[MQTT] Device controller stopped")

def main():
    # Configuration - change these for your setup
    BROKER_HOST = "localhost"  # Change to your MQTT broker IP
    BROKER_PORT = 1883
    
    print("=== MQTT Device Controller ===")
    print(f"Broker: {BROKER_HOST}:{BROKER_PORT}")
    print("Topics:")
    print("  - dev/motor    (motor commands)")
    print("  - dev/led      (LED commands)")
    print("  - dev/commands (general commands)")
    print("  - dev/status   (status messages)")
    print("\nPress Ctrl+C to stop")
    print("=" * 40)
    
    controller = MQTTDeviceController(BROKER_HOST, BROKER_PORT)
    
    try:
        controller.start()
    except KeyboardInterrupt:
        print("\n[SYSTEM] Shutting down...")
    finally:
        controller.stop()

if __name__ == "__main__":
    main()