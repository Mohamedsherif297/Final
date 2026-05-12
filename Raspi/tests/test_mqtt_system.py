#!/usr/bin/env python3
"""
Comprehensive MQTT System Tester
Tests all components of the IoT surveillance car MQTT system
"""

import paho.mqtt.client as mqtt
import json
import time
import threading
import sys
from datetime import datetime

class MQTTSystemTester:
    def __init__(self, broker_host="localhost", broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        
        # MQTT Topics
        self.TOPIC_COMMANDS = "dev/commands"
        self.TOPIC_STATUS = "dev/status"
        self.TOPIC_MOTOR = "dev/motor"
        self.TOPIC_LED = "dev/led"
        
        # Test results
        self.test_results = []
        self.status_messages = []
        
        # MQTT Client setup
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        self.connected = False
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            client.subscribe(self.TOPIC_STATUS)
            self.log_result("✅ MQTT Connection", "Connected successfully")
        else:
            self.connected = False
            self.log_result("❌ MQTT Connection", f"Failed with code {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        self.log_result("⚠️ MQTT Disconnect", f"Disconnected (code: {rc})")
    
    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = msg.payload.decode()
            
            if topic == self.TOPIC_STATUS:
                try:
                    data = json.loads(payload)
                    status_type = data.get("type", "unknown")
                    message = data.get("message", payload)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    status_msg = f"[{timestamp}] {status_type}: {message}"
                    self.status_messages.append(status_msg)
                    print(f"📨 {status_msg}")
                    
                except json.JSONDecodeError:
                    print(f"📨 Status: {payload}")
                    
        except Exception as e:
            print(f"❌ Message error: {e}")
    
    def log_result(self, test_name, result):
        """Log test result"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.test_results.append(f"[{timestamp}] {test_name}: {result}")
        print(f"{test_name}: {result}")
    
    def connect_to_broker(self):
        """Test MQTT broker connection"""
        print(f"\n🔌 Testing MQTT Broker Connection...")
        print(f"Broker: {self.broker_host}:{self.broker_port}")
        
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            
            # Wait for connection
            timeout = 5
            while not self.connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1
            
            return self.connected
            
        except Exception as e:
            self.log_result("❌ MQTT Connection", f"Error: {e}")
            return False
    
    def test_motor_commands(self):
        """Test motor control commands"""
        print(f"\n🚗 Testing Motor Commands...")
        
        if not self.connected:
            self.log_result("❌ Motor Test", "Not connected to broker")
            return
        
        motor_tests = [
            {"direction": "forward", "speed": 60, "description": "Move forward"},
            {"direction": "backward", "speed": 50, "description": "Move backward"},
            {"direction": "left", "speed": 70, "description": "Turn left"},
            {"direction": "right", "speed": 70, "description": "Turn right"},
            {"direction": "stop", "speed": 0, "description": "Stop motors"}
        ]
        
        for test in motor_tests:
            try:
                payload = json.dumps({
                    "direction": test["direction"],
                    "speed": test["speed"]
                })
                
                result = self.client.publish(self.TOPIC_MOTOR, payload)
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    self.log_result("✅ Motor Command", f"{test['description']} (speed: {test['speed']})")
                else:
                    self.log_result("❌ Motor Command", f"Failed to send {test['description']}")
                
                time.sleep(0.5)  # Small delay between commands
                
            except Exception as e:
                self.log_result("❌ Motor Command", f"Error: {e}")
    
    def test_led_commands(self):
        """Test LED control commands"""
        print(f"\n💡 Testing LED Commands...")
        
        if not self.connected:
            self.log_result("❌ LED Test", "Not connected to broker")
            return
        
        led_tests = [
            {"action": "set_color", "color": "red", "description": "Set red color"},
            {"action": "set_color", "color": "green", "description": "Set green color"},
            {"action": "set_color", "color": "blue", "description": "Set blue color"},
            {"action": "set_rgb", "red": 255, "green": 128, "blue": 0, "description": "Set RGB orange"},
            {"action": "blink", "led": "status", "interval": 0.3, "description": "Blink status LED"},
            {"action": "all_off", "description": "Turn off all LEDs"}
        ]
        
        for test in led_tests:
            try:
                # Create command payload
                command = {"action": test["action"]}
                
                # Add additional parameters based on action
                if test["action"] == "set_color":
                    command["color"] = test["color"]
                elif test["action"] == "set_rgb":
                    command["red"] = test["red"]
                    command["green"] = test["green"]
                    command["blue"] = test["blue"]
                elif test["action"] == "blink":
                    command["led"] = test["led"]
                    command["interval"] = test["interval"]
                
                payload = json.dumps(command)
                result = self.client.publish(self.TOPIC_LED, payload)
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    self.log_result("✅ LED Command", test["description"])
                else:
                    self.log_result("❌ LED Command", f"Failed to send {test['description']}")
                
                time.sleep(0.5)
                
            except Exception as e:
                self.log_result("❌ LED Command", f"Error: {e}")
    
    def test_general_commands(self):
        """Test general system commands"""
        print(f"\n🎮 Testing General Commands...")
        
        if not self.connected:
            self.log_result("❌ General Test", "Not connected to broker")
            return
        
        general_tests = [
            {"command": "status", "description": "Get device status"},
            {"command": "emergency_stop", "description": "Emergency stop"},
            {"command": "test_hardware", "description": "Test hardware"}
        ]
        
        for test in general_tests:
            try:
                payload = json.dumps({"command": test["command"]})
                result = self.client.publish(self.TOPIC_COMMANDS, payload)
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    self.log_result("✅ General Command", test["description"])
                else:
                    self.log_result("❌ General Command", f"Failed to send {test['description']}")
                
                time.sleep(0.5)
                
            except Exception as e:
                self.log_result("❌ General Command", f"Error: {e}")
    
    def test_message_validation(self):
        """Test invalid message handling"""
        print(f"\n🔍 Testing Message Validation...")
        
        if not self.connected:
            self.log_result("❌ Validation Test", "Not connected to broker")
            return
        
        # Test invalid motor commands
        invalid_tests = [
            {"topic": self.TOPIC_MOTOR, "payload": '{"direction": "invalid", "speed": 50}', "description": "Invalid direction"},
            {"topic": self.TOPIC_MOTOR, "payload": '{"direction": "forward", "speed": 150}', "description": "Invalid speed (>100)"},
            {"topic": self.TOPIC_LED, "payload": '{"action": "invalid_action"}', "description": "Invalid LED action"},
            {"topic": self.TOPIC_COMMANDS, "payload": '{"command": "invalid_command"}', "description": "Invalid general command"}
        ]
        
        for test in invalid_tests:
            try:
                result = self.client.publish(test["topic"], test["payload"])
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    self.log_result("✅ Validation Test", f"Sent {test['description']}")
                else:
                    self.log_result("❌ Validation Test", f"Failed to send {test['description']}")
                
                time.sleep(0.3)
                
            except Exception as e:
                self.log_result("❌ Validation Test", f"Error: {e}")
    
    def run_performance_test(self):
        """Test system performance with rapid commands"""
        print(f"\n⚡ Testing Performance (Rapid Commands)...")
        
        if not self.connected:
            self.log_result("❌ Performance Test", "Not connected to broker")
            return
        
        start_time = time.time()
        command_count = 20
        
        for i in range(command_count):
            # Alternate between motor and LED commands
            if i % 2 == 0:
                payload = json.dumps({"direction": "forward", "speed": 50})
                self.client.publish(self.TOPIC_MOTOR, payload)
            else:
                payload = json.dumps({"action": "set_color", "color": "blue"})
                self.client.publish(self.TOPIC_LED, payload)
            
            time.sleep(0.1)  # 100ms between commands
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.log_result("✅ Performance Test", f"Sent {command_count} commands in {duration:.2f}s")
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n" + "="*60)
        print(f"📊 MQTT SYSTEM TEST SUMMARY")
        print(f"="*60)
        
        print(f"\n🔍 Test Results:")
        for result in self.test_results:
            print(f"  {result}")
        
        print(f"\n📨 Status Messages Received:")
        if self.status_messages:
            for msg in self.status_messages[-10:]:  # Show last 10 messages
                print(f"  {msg}")
        else:
            print("  No status messages received")
        
        # Count results
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅" in r])
        failed_tests = len([r for r in self.test_results if "❌" in r])
        
        print(f"\n📈 Statistics:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "  Success Rate: 0%")
        
        print(f"\n🎯 System Status:")
        if self.connected:
            print(f"  ✅ MQTT Broker: Connected")
        else:
            print(f"  ❌ MQTT Broker: Disconnected")
        
        print(f"  📡 Broker: {self.broker_host}:{self.broker_port}")
        print(f"  📊 Status Messages: {len(self.status_messages)} received")
        
        print(f"\n" + "="*60)
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except:
            pass
    
    def run_all_tests(self):
        """Run all MQTT system tests"""
        print(f"🧪 MQTT IoT System Comprehensive Test")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"="*60)
        
        # Connect to broker
        if not self.connect_to_broker():
            print(f"❌ Cannot connect to MQTT broker. Make sure:")
            print(f"   1. Mosquitto is running: brew services start mosquitto")
            print(f"   2. Broker is accessible at {self.broker_host}:{self.broker_port}")
            return False
        
        # Wait a moment for connection to stabilize
        time.sleep(1)
        
        try:
            # Run all tests
            self.test_motor_commands()
            time.sleep(1)
            
            self.test_led_commands()
            time.sleep(1)
            
            self.test_general_commands()
            time.sleep(1)
            
            self.test_message_validation()
            time.sleep(1)
            
            self.run_performance_test()
            time.sleep(2)  # Wait for final status messages
            
        except KeyboardInterrupt:
            print(f"\n⚠️ Test interrupted by user")
        
        finally:
            self.print_summary()
            self.disconnect()
        
        return True

def main():
    """Main function"""
    if len(sys.argv) > 1:
        broker_host = sys.argv[1]
    else:
        broker_host = "localhost"
    
    print(f"🚀 Starting MQTT System Test")
    print(f"Broker: {broker_host}")
    print(f"Make sure the debug controller is running!")
    print(f"Run: python3 debug_mqtt_controller.py")
    print()
    
    tester = MQTTSystemTester(broker_host)
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print(f"\n🎉 Test completed! Check the summary above.")
        else:
            print(f"\n❌ Test failed to start. Check broker connection.")
            
    except Exception as e:
        print(f"\n❌ Test error: {e}")
    
    finally:
        tester.disconnect()

if __name__ == "__main__":
    main()