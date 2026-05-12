#!/usr/bin/env python3
"""
WebSocket Video Streaming
Simple video streaming to dashboard
"""
import asyncio
import websockets
import cv2
import json
import time
from threading import Thread

# Configuration
WS_HOST = "0.0.0.0"
WS_PORT = 8765
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
VIDEO_FPS = 20
JPEG_QUALITY = 65

class WebSocketStreamer:
    def __init__(self):
        self.clients = set()
        self.camera = None
        self.running = False
        self.frame_count = 0
        self.last_stat_time = time.time()
        
    def setup_camera(self):
        """Initialize camera"""
        print("[Camera] Opening camera...")
        self.camera = cv2.VideoCapture(0)
        
        if not self.camera.isOpened():
            print("[Camera] Failed to open camera")
            return False
        
        # Set resolution
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
        self.camera.set(cv2.CAP_PROP_FPS, VIDEO_FPS)
        
        print(f"[Camera] Initialized: {VIDEO_WIDTH}x{VIDEO_HEIGHT} @ {VIDEO_FPS}fps")
        return True
    
    async def handle_client(self, websocket, path):
        """Handle new WebSocket client"""
        client_addr = websocket.remote_address
        print(f"[WebSocket] Client connected: {client_addr}")
        
        self.clients.add(websocket)
        
        try:
            # Send welcome message
            welcome = json.dumps({"event": "connected", "server": "surveillance-car"})
            await websocket.send(b'\x00' + welcome.encode())
            
            # Keep connection alive and handle incoming messages
            async for message in websocket:
                # Handle incoming commands if needed
                try:
                    data = json.loads(message)
                    print(f"[WebSocket] Received: {data}")
                except:
                    pass
                    
        except websockets.exceptions.ConnectionClosed:
            print(f"[WebSocket] Client disconnected: {client_addr}")
        finally:
            self.clients.discard(websocket)
    
    async def broadcast_frame(self, frame_data):
        """Broadcast frame to all connected clients"""
        if not self.clients:
            return
        
        # Prepend video tag (0x01)
        tagged_frame = b'\x01' + frame_data
        
        # Send to all clients
        disconnected = set()
        for client in self.clients:
            try:
                await client.send(tagged_frame)
            except:
                disconnected.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected
        
        # Stats
        self.frame_count += 1
        now = time.time()
        if now - self.last_stat_time >= 5:
            fps = self.frame_count / (now - self.last_stat_time)
            print(f"[Stream] {fps:.1f} fps | {len(self.clients)} client(s)")
            self.frame_count = 0
            self.last_stat_time = now
    
    def capture_loop(self):
        """Capture frames in background thread"""
        print("[Camera] Capture thread started")
        
        frame_interval = 1.0 / VIDEO_FPS
        next_frame_time = time.time()
        
        while self.running:
            ret, frame = self.camera.read()
            
            if not ret:
                print("[Camera] Failed to read frame")
                time.sleep(0.1)
                continue
            
            # Encode to JPEG
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
            ret, buffer = cv2.imencode('.jpg', frame, encode_params)
            
            if ret:
                frame_data = buffer.tobytes()
                
                # Schedule broadcast in async loop
                asyncio.run_coroutine_threadsafe(
                    self.broadcast_frame(frame_data),
                    self.loop
                )
            
            # Frame rate control
            next_frame_time += frame_interval
            sleep_time = next_frame_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                next_frame_time = time.time()
        
        print("[Camera] Capture thread stopped")
    
    async def start_server(self):
        """Start WebSocket server"""
        print("=" * 60)
        print("WebSocket Video Streaming Server")
        print("=" * 60)
        print(f"Host: {WS_HOST}:{WS_PORT}")
        print(f"Video: {VIDEO_WIDTH}x{VIDEO_HEIGHT} @ {VIDEO_FPS}fps")
        print("=" * 60)
        
        # Setup camera
        if not self.setup_camera():
            print("[Error] Camera initialization failed")
            return
        
        # Start capture thread
        self.running = True
        self.loop = asyncio.get_running_loop()
        
        capture_thread = Thread(target=self.capture_loop, daemon=True)
        capture_thread.start()
        
        # Start WebSocket server
        print(f"\n[WebSocket] Server starting on ws://{WS_HOST}:{WS_PORT}")
        print("[WebSocket] Waiting for clients...")
        
        async with websockets.serve(self.handle_client, WS_HOST, WS_PORT):
            await asyncio.Future()  # Run forever
    
    def cleanup(self):
        """Cleanup resources"""
        print("\n[System] Shutting down...")
        self.running = False
        
        if self.camera:
            self.camera.release()
        
        print("[System] Cleanup complete")

def main():
    streamer = WebSocketStreamer()
    
    try:
        asyncio.run(streamer.start_server())
    except KeyboardInterrupt:
        print("\n[System] Keyboard interrupt")
    finally:
        streamer.cleanup()

if __name__ == "__main__":
    main()
