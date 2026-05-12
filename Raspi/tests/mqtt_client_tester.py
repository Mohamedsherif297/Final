#!/usr/bin/env python3
"""
MQTT Client Tester
This script sends commands to the Raspberry Pi device controller
Run this on your laptop/computer to control the Pi remotely
"""

import paho.mqtt.client as mqtt
import json
import time
import threading
import sys

class MQTTClientTester:
    def __init__(self, broker_host="localhost", broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        
        # MQTT Topics (same as device controller)
        self.TOPIC_COMMANDS = "dev/commands"
        self.TOPIC_STATUS = "dev/status"
        self.TOPIC_MOTOR = "dev/motor"
        self.TOPIC_LED = "dev/led"
        
        # MQTT Client setup
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        self.connected = False
        
        print(f"[CLIENT] MQTT Client Tester initialized for {broker_host}:{broker_port}")
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[CLIENT] Connected to MQTT broker successfully")
            self.connected = True
            
            # Subscribe to status messages
            client.subscribe(self.TOPIC_STATUS)
            print(f"[CLIENT] Subscribed to {self.TOPIC_STATUS}")
            
        else:
            print(f"[CLIENT] Connection failed with code {rc}")
            self.connected = False
    
    def on_disconnect(self, client, userdata, rc):
        print(f"[CLIENT] Disconnected from broker (code: {rc})")
        self.connected = False
    
    def on_message(self, client, userdata, msg):
        """Handle incoming status messages"""
        try:
            topic = msg.topic
            payload = msg.payload.decode()
            
            if topic == self.TOPIC_STATUS:
                try:
                    data = json.loads(payload)
                    status_type = data.get("type", "unknown")
                    message = data.get("message", payload)
                    timestamp = data.get("timestamp", time.time())
                    
                    print(f"[STATUS] {status_type.upper()}: {message}")
                    
                except json.JSONDecodeError:
                    print(f"[STATUS] {payload}")
            
        except Exception as e:
            print(f"[CLIENT] Error processing message: {e}")
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            print(f"[CLIENT] Connecting to {self.broker_host}:{self.broker_port}...")
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()  # Start background loop
            
            # Wait for connection
            timeout = 5
            while not self.connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1
            
            return self.connected
            
        except Exception as e:
            print(f"[CLIENT] Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
    
    def send_motor_command(self, direction, speed=50):
        """Send motor control command"""
        if not self.connected:
            print("[CLIENT] Not connected to broker")
            return False
        
        command = {
            "direction": direction,
            "speed": speed
        }
        
        payload = json.dumps(command)
        result = self.client.publish(self.TOPIC_MOTOR, payload)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"[CLIENT] Motor command sent: {direction} at speed {speed}")
            return True
        else:
            print(f"[CLIENT] Failed to send motor command")
            return False
    
    def send_led_command(self, action, **kwargs):
        """Send LED control command"""
        if not self.connected:
            print("[CLIENT] Not connected to broker")
            return False
        
        command = {
            "action": action,
            **kwargs
        }
        
        payload = json.dumps(command)
        result = self.client.publish(self.TOPIC_LED, payload)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"[CLIENT] LED command sent: {action}")
            return True
        else:
            print(f"[CLIENT] Failed to send LED command")
            return False
    
    def send_general_command(self, command):
        """Send general system command"""
        if not self.connected:
            print("[CLIENT] Not connected to broker")
            return False
        
        command_data = {"command": command}
        payload = json.dumps(command_data)
        result = self.client.publish(self.TOPIC_COMMANDS, payload)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"[CLIENT] General command sent: {command}")
            return True
        else:
            print(f"[CLIENT] Failed to send command")
            return False
    
    def interactive_mode(self):
        """Interactive command mode"""
        print("\n" + "="*50)
        print("INTERACTIVE MQTT CONTROL MODE")
        print("="*50)
        print("Motor Commands:")
        print("  f, forward    - Move forward")
        print("  b, backward   - Move backward")
        print("  l, left       - Turn left")
        print("  r, right      - Turn right")
        print("  s, stop       - Stop motors")
        print("\nLED Commands:")
        print("  led red       - Turn on red LED")
        print("  led green     - Turn on green LED")
        print("  led blue      - Turn on blue LED")
        print("  led off       - Turn off all LEDs")
        print("  led blink     - Blink status LED")
        print("  led test      - Run LED test sequence")
        print("\nGeneral Commands:")
        print("  status        - Get device status")
        print("  test          - Test all systems")
        print("  emergency     - Emergency stop")
        print("  quit, exit    - Exit program")
        print("="*50)
        
        while True:
            try:
                command = input("\nEnter command: ").strip().lower()
                
                if command in ['quit', 'exit', 'q']:
                    break
                
                elif command in ['f', 'forward']:
                    self.send_motor_command("forward", 60)
                
                elif command in ['b', 'backward']:
                    self.send_motor_command("backward", 60)
                
                elif command in ['l', 'left']:
                    self.send_motor_command("left", 60)
                
                elif command in ['r', 'right']:
                    self.send_motor_command("right", 60)
                
                elif command in ['s', 'stop']:
                    self.send_motor_command("stop", 0)
                
                elif command.startswith('led '):
                    led_cmd = command.split(' ', 1)[1]
                    if led_cmd == 'red':
                        self.send_led_command("set_color", color="red")
                    elif led_cmd == 'green':
                        self.send_led_command("set_color", color="green")
                    elif led_cmd == 'blue':
                        self.send_led_command("set_color", color="blue")
                    elif led_cmd == 'off':
                        self.send_led_command("all_off")
                    elif led_cmd == 'blink':
                        self.send_led_command("blink", led="status", interval=0.5)
                    elif led_cmd == 'test':
                        self.send_led_command("test")
                    else:
                        print("Unknown LED command")
                
                elif command == 'status':
                    self.send_general_command("status")
                
                elif command == 'test':
                    self.send_general_command("test_motors")
                    time.sleep(0.5)
                    self.send_general_command("test_leds")
                
                elif command == 'emergency':
                    self.send_general_command("emergency_stop")
                
                else:
                    print("Unknown command. Type 'quit' to exit.")
            
            except KeyboardInterrupt:
                break
            except EOFError:
                break
        
        print("\n[CLIENT] Exiting interactive mode...")
    
    def demo_sequence(self):
        """Run a demonstration sequence"""
        print("\n[DEMO] Starting demonstration sequence...")
        
        # Test LEDs first
        print("[DEMO] Testing LEDs...")
        self.send_led_command("set_color", color="red")
        time.sleep(1)
        self.send_led_command("set_color", color="green")
        time.sleep(1)
        self.send_led_command("set_color", color="blue")
        time.sleep(1)
        self.send_led_command("all_off")
        time.sleep(1)
        
        # Test motors
        print("[DEMO] Testing motors...")
        movements = [
            ("forward", 50),
            ("backward", 50),
            ("left", 60),
            ("right", 60),
            ("stop", 0)
        ]
        
        for direction, speed in movements:
            print(f"[DEMO] Moving {direction}...")
            self.send_motor_command(direction, speed)
            time.sleep(2)
        
        # Final LED indication
        self.send_led_command("blink", led="green", interval=0.2, duration=2)
        
        print("[DEMO] Demonstration complete!")

def main():
    if len(sys.argv) > 1:
        broker_host = sys.argv[1]
    else:
        broker_host = input("Enter MQTT broker IP (or press Enter for localhost): ").strip()
        if not broker_host:
            broker_host = "localhost"
    
    print(f"\n=== MQTT Client Tester ===")
    print(f"Connecting to broker: {broker_host}")
    
    client = MQTTClientTester(broker_host)
    
    if not client.connect():
        print("[ERROR] Could not connect to MQTT broker")
        print("Make sure:")
        print("1. MQTT broker is running")
        print("2. Broker IP address is correct")
        print("3. Network connectivity is working")
        return
    
    try:
        print("\nChoose mode:")
        print("1. Interactive mode (manual control)")
        print("2. Demo sequence (automated test)")
        print("3. Exit")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            client.interactive_mode()
        elif choice == "2":
            client.demo_sequence()
        elif choice == "3":
            print("Exiting...")
        else:
            print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\n[CLIENT] Interrupted by user")
    
    finally:
        client.disconnect()
        print("[CLIENT] Disconnected")

if __name__ == "__main__":
    main()