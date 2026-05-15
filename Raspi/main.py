#!/usr/bin/env python3
"""
Main Entry Point for Surveillance Car System
Orchestrates hardware, network, and AI components
"""

import os
import sys
import signal
import time
import asyncio
from pathlib import Path

# Suppress verbose library warnings
os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
os.environ['OPENCV_VIDEOIO_DEBUG'] = '0'

# Add current directory and Drivers directory to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'Drivers'))

from Drivers.hardware.managers.hardware_manager import hardware_manager
from Network.MQTT.mqtt_device_controller_integrated import MQTTDeviceController

# WebSocket imports
try:
    from Network.WebSockets.websocket_server import WebSocketServer
    from Network.WebSockets.video_stream_handler import VideoStreamHandler
    from Network.WebSockets.audio_system import AudioSystem
    from Network.WebSockets import config as ws_config
    WEBSOCKET_AVAILABLE = True
except ImportError as e:
    print(f"[SYSTEM] WebSocket modules not available: {e}")
    WEBSOCKET_AVAILABLE = False


class SurveillanceCarSystem:
    """
    Main system orchestrator for the surveillance car
    
    Manages:
    - Hardware initialization and control
    - MQTT network communication
    - WebSocket video/audio streaming
    - System lifecycle and graceful shutdown
    """
    
    def __init__(self, broker_host="localhost", broker_port=1883, enable_websocket=True):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.enable_websocket = enable_websocket and WEBSOCKET_AVAILABLE
        self.running = False
        
        # Components
        self.mqtt_controller = None
        self.websocket_server = None
        self.video_handler = None
        self.audio_handler = None
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n[SYSTEM] Received signal {signum}, initiating shutdown...")
        self.running = False
    
    def initialize(self):
        """Initialize all system components"""
        print("=" * 60)
        print("Surveillance Car System - Initializing")
        print("=" * 60)
        
        try:
            # Initialize hardware manager
            print("[SYSTEM] Initializing hardware...")
            hardware_manager.initialize()
            print("[SYSTEM] Hardware initialized successfully")
            
            # Initialize MQTT controller
            print("[SYSTEM] Initializing MQTT controller...")
            self.mqtt_controller = MQTTDeviceController(
                self.broker_host,
                self.broker_port
            )
            print("[SYSTEM] MQTT controller initialized")
            
            # Initialize WebSocket components if enabled
            if self.enable_websocket:
                print("[SYSTEM] Initializing WebSocket streaming...")
                self._initialize_websocket()
                print("[SYSTEM] WebSocket streaming initialized")
            else:
                print("[SYSTEM] WebSocket streaming disabled")
            
            print("=" * 60)
            print("[SYSTEM] All components initialized successfully")
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"[SYSTEM] Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _initialize_websocket(self):
        """Initialize WebSocket server and streaming handlers"""
        # Create WebSocket server
        self.websocket_server = WebSocketServer(
            host=ws_config.WS_HOST,
            port=ws_config.WS_PORT,
            mqtt_broker=self.broker_host,
            mqtt_port=self.broker_port,
        )
        
        # Create video stream handler
        self.video_handler = VideoStreamHandler(
            self.websocket_server,
            camera_index=ws_config.VIDEO_CAMERA_INDEX
        )
        
        # Create audio system handler
        self.audio_handler = AudioSystem(
            self.websocket_server,
            device_index=ws_config.AUDIO_DEVICE_INDEX
        )
        
        print(f"[SYSTEM] WebSocket server configured on ws://{ws_config.WS_HOST}:{ws_config.WS_PORT}")
        print(f"[SYSTEM] Video: {ws_config.VIDEO_CAPTURE_WIDTH}x{ws_config.VIDEO_CAPTURE_HEIGHT} @ {ws_config.VIDEO_TARGET_FPS} FPS")
        print(f"[SYSTEM] Audio: {ws_config.AUDIO_SAMPLE_RATE} Hz, {ws_config.AUDIO_CHANNELS} channel(s)")
    
    def run(self):
        """Run the surveillance car system"""
        if not self.initialize():
            print("[SYSTEM] Failed to initialize - exiting")
            return 1
        
        try:
            self.running = True
            print("[SYSTEM] System running. Press Ctrl+C to exit.")
            print("=" * 60)
            
            # If WebSocket is enabled, run async event loop
            if self.enable_websocket:
                print("[SYSTEM] Starting with WebSocket streaming enabled")
                try:
                    return asyncio.run(self._run_async())
                except KeyboardInterrupt:
                    print("\n[SYSTEM] Keyboard interrupt received")
            else:
                # Run MQTT-only mode (blocking)
                print("[SYSTEM] Starting in MQTT-only mode")
                self.mqtt_controller.start()
            
        except KeyboardInterrupt:
            print("\n[SYSTEM] Keyboard interrupt received")
        
        except Exception as e:
            print(f"[SYSTEM] Critical error: {e}")
            import traceback
            traceback.print_exc()
            return 1
        
        finally:
            self.shutdown()
        
        return 0
    
    async def _run_async(self):
        """Run system with async WebSocket support"""
        tasks = []
        mqtt_thread = None
        
        try:
            # Start video and audio capture threads (non-blocking)
            self.video_handler.start_capture()
            self.audio_handler.start_capture()
            
            # Start MQTT in a separate thread (non-blocking)
            import threading
            mqtt_thread = threading.Thread(
                target=self.mqtt_controller.start,
                name="MQTT-Thread",
                daemon=True
            )
            mqtt_thread.start()
            
            # Create tasks for WebSocket server + streaming loops
            tasks = [
                asyncio.create_task(self.websocket_server.start()),
                asyncio.create_task(self.video_handler.stream_loop()),
                asyncio.create_task(self.audio_handler.stream_loop()),
            ]
            
            # Wait for tasks with proper cancellation handling
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except (KeyboardInterrupt, asyncio.CancelledError):
            print("\n[SYSTEM] Async tasks cancelled")
        
        finally:
            # Cancel all running tasks
            for task in tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete cancellation
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        
        return 0
    
    def shutdown(self):
        """Graceful shutdown of all components"""
        print("\n" + "=" * 60)
        print("[SYSTEM] Shutting down surveillance car system...")
        print("=" * 60)
        
        # Set running flag to false
        self.running = False
        
        # Stop WebSocket streaming
        if self.enable_websocket:
            try:
                if self.video_handler:
                    print("[SYSTEM] Stopping video capture...")
                    self.video_handler.stop_capture()
                if self.audio_handler:
                    print("[SYSTEM] Stopping audio capture...")
                    self.audio_handler.stop_capture()
                if self.websocket_server:
                    print("[SYSTEM] Stopping WebSocket server...")
                    self.websocket_server._request_shutdown()
                print("[SYSTEM] WebSocket streaming stopped")
            except Exception as e:
                print(f"[SYSTEM] WebSocket shutdown warning: {e}")
        
        # Stop MQTT controller
        if self.mqtt_controller:
            try:
                print("[SYSTEM] Stopping MQTT controller...")
                self.mqtt_controller.stop()
                print("[SYSTEM] MQTT controller stopped")
            except Exception as e:
                print(f"[SYSTEM] MQTT shutdown warning: {e}")
        
        # Cleanup hardware
        try:
            print("[SYSTEM] Cleaning up hardware...")
            hardware_manager.cleanup()
            print("[SYSTEM] Hardware cleanup complete")
        except Exception as e:
            print(f"[SYSTEM] Hardware cleanup warning: {e}")
        
        # Give threads time to finish
        time.sleep(0.5)
        
        print("[SYSTEM] Shutdown complete")
        print("=" * 60)


def main():
    """Application entry point"""
    # Configuration - can be loaded from config file or environment variables
    # Option 1: Local broker (same network only)
    # BROKER_HOST = "localhost"
    # BROKER_PORT = 1883
    
    # Option 2: HiveMQ Cloud (WAN access - works from anywhere)
    BROKER_HOST = "broker.hivemq.com"  # Free HiveMQ public broker
    BROKER_PORT = 1883
    
    # Option 3: Your ESP IP (if ESP is running MQTT broker)
    # BROKER_HOST = "YOUR_ESP_IP"  # e.g., "192.168.1.150"
    # BROKER_PORT = 1883
    
    ENABLE_WEBSOCKET = True    # Set to False to disable WebSocket streaming
    
    # Print startup banner
    print("\n" + "=" * 60)
    print("  SURVEILLANCE CAR SYSTEM")
    print("  Hardware + MQTT + WebSocket Streaming")
    print("=" * 60)
    print(f"  MQTT Broker: {BROKER_HOST}:{BROKER_PORT}")
    if ENABLE_WEBSOCKET and WEBSOCKET_AVAILABLE:
        print(f"  WebSocket: Enabled (port {ws_config.WS_PORT if WEBSOCKET_AVAILABLE else 'N/A'})")
    else:
        print(f"  WebSocket: Disabled")
    print("=" * 60 + "\n")
    
    # Create and run system
    system = SurveillanceCarSystem(BROKER_HOST, BROKER_PORT, ENABLE_WEBSOCKET)
    
    # Setup a timeout for forced exit
    import threading
    shutdown_timer = None
    
    def force_exit():
        """Force exit if graceful shutdown takes too long"""
        print("\n[SYSTEM] Force exit - graceful shutdown timeout")
        os._exit(1)
    
    try:
        return system.run()
    except KeyboardInterrupt:
        print("\n[SYSTEM] Ctrl+C pressed - shutting down...")
        # Start a timer for forced exit (5 seconds)
        shutdown_timer = threading.Timer(5.0, force_exit)
        shutdown_timer.daemon = True
        shutdown_timer.start()
        return 0
    finally:
        if shutdown_timer and shutdown_timer.is_alive():
            shutdown_timer.cancel()


if __name__ == "__main__":
    sys.exit(main())
