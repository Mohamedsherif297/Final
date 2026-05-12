#!/usr/bin/env python3
"""
Simple WebSocket Test - Verify WebSocket server works
"""
import asyncio
import websockets
import json

WS_HOST = "0.0.0.0"
WS_PORT = 8765

clients = set()

async def handle_client(websocket, path):
    client_addr = websocket.remote_address
    print(f"✅ Client connected: {client_addr}")
    clients.add(websocket)
    
    try:
        # Send welcome message
        welcome = json.dumps({"event": "connected", "server": "test-server"})
        await websocket.send(welcome)
        print(f"   Sent welcome to {client_addr}")
        
        # Keep connection alive
        async for message in websocket:
            print(f"   Received from {client_addr}: {message}")
            await websocket.send(f"Echo: {message}")
            
    except websockets.exceptions.ConnectionClosed:
        print(f"❌ Client disconnected: {client_addr}")
    finally:
        clients.discard(websocket)

async def main():
    print("=" * 60)
    print("WebSocket Test Server")
    print("=" * 60)
    print(f"Host: {WS_HOST}")
    print(f"Port: {WS_PORT}")
    print("=" * 60)
    print("\nStarting server...")
    print(f"Connect from dashboard using: ws://YOUR_PI_IP:{WS_PORT}")
    print("\nWaiting for connections...\n")
    
    async with websockets.serve(handle_client, WS_HOST, WS_PORT):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        print(f"Total clients connected: {len(clients)}")
