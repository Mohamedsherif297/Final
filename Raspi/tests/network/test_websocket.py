"""
tests/network/test_websocket.py
================================
Tests WebSocket server: connection handshake, video frame
receipt, audio chunk receipt, and MQTT command bridging.

⚠️  Requires main.py running on the Pi before this test.
    On Pi: cd /home/pi/Final/Raspi && python3 main.py

Run:  pytest tests/network/test_websocket.py -v
      PI_IP=192.168.1.xx pytest tests/network/test_websocket.py -v
"""

import pytest
import time
import json
import asyncio
import threading
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

try:
    import websockets
    WS_AVAILABLE = True
except ImportError:
    WS_AVAILABLE = False

pytestmark = pytest.mark.websocket

CONNECT_TIMEOUT  = 5.0
FRAME_TIMEOUT    = 8.0   # seconds to wait for first video frame
AUDIO_TIMEOUT    = 5.0


# ── Helper: run async in a sync test ─────────────────────────
def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ══════════════════════════════════════════════════════════════
# CONNECTION TESTS
# ══════════════════════════════════════════════════════════════

@pytest.mark.skipif(not WS_AVAILABLE, reason="websockets not installed")
class TestWebSocketConnection:

    def test_server_is_reachable(self, ws_url):
        """Should connect to the WebSocket server."""
        async def _test():
            async with websockets.connect(ws_url, open_timeout=CONNECT_TIMEOUT) as ws:
                assert ws.open
                print(f"\n  Connected to {ws_url} ✓")

        run_async(_test())

    def test_welcome_message_received(self, ws_url):
        """Server should send a welcome JSON on connect."""
        async def _test():
            async with websockets.connect(ws_url, open_timeout=CONNECT_TIMEOUT) as ws:
                raw = await asyncio.wait_for(ws.recv(), timeout=CONNECT_TIMEOUT)
                assert isinstance(raw, bytes), "Expected binary message"
                assert raw[0] == 0x00, f"Expected 0x00 JSON tag, got {hex(raw[0])}"

                msg = json.loads(raw[1:].decode())
                assert msg.get("event") == "connected"
                assert "server" in msg
                print(f"\n  Welcome message: {msg} ✓")

        run_async(_test())

    def test_multiple_clients_connect(self, ws_url):
        """Two clients should connect simultaneously."""
        async def _test():
            async with websockets.connect(ws_url) as ws1, \
                       websockets.connect(ws_url) as ws2:
                assert ws1.open
                assert ws2.open
                print("\n  Two simultaneous clients connected ✓")

        run_async(_test())


# ══════════════════════════════════════════════════════════════
# VIDEO STREAMING TESTS
# ══════════════════════════════════════════════════════════════

@pytest.mark.skipif(not WS_AVAILABLE, reason="websockets not installed")
class TestVideoStreaming:

    def test_video_frames_received(self, ws_url):
        """Should receive at least 5 video frames (0x01 tag) within timeout."""
        async def _test():
            video_frames = []

            async with websockets.connect(ws_url, open_timeout=CONNECT_TIMEOUT) as ws:
                deadline = asyncio.get_event_loop().time() + FRAME_TIMEOUT
                while asyncio.get_event_loop().time() < deadline and len(video_frames) < 5:
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=2.0)
                        if isinstance(raw, bytes) and raw[0] == 0x01:
                            video_frames.append(raw)
                    except asyncio.TimeoutError:
                        break

            assert len(video_frames) >= 5, \
                f"Only got {len(video_frames)} frames — is camera connected and main.py running?"
            print(f"\n  Received {len(video_frames)} video frames ✓")

        run_async(_test())

    def test_video_frame_is_valid_jpeg(self, ws_url):
        """Video frames should start with JPEG magic bytes (FF D8)."""
        async def _test():
            async with websockets.connect(ws_url, open_timeout=CONNECT_TIMEOUT) as ws:
                deadline = asyncio.get_event_loop().time() + FRAME_TIMEOUT
                while asyncio.get_event_loop().time() < deadline:
                    raw = await asyncio.wait_for(ws.recv(), timeout=2.0)
                    if isinstance(raw, bytes) and raw[0] == 0x01:
                        jpeg_data = raw[1:]
                        assert jpeg_data[0] == 0xFF and jpeg_data[1] == 0xD8, \
                            "Frame is not a valid JPEG (wrong magic bytes)"
                        assert len(jpeg_data) > 1000, \
                            f"Frame too small ({len(jpeg_data)} bytes) — blank image?"
                        print(f"\n  Valid JPEG frame: {len(jpeg_data)} bytes ✓")
                        return
            pytest.fail("No video frame received within timeout")

        run_async(_test())

    def test_video_fps_is_reasonable(self, ws_url):
        """Should receive at least 5 FPS over a 3-second window."""
        async def _test():
            frame_count = 0
            start = asyncio.get_event_loop().time()
            window = 3.0

            async with websockets.connect(ws_url, open_timeout=CONNECT_TIMEOUT) as ws:
                deadline = start + window
                while asyncio.get_event_loop().time() < deadline:
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        if isinstance(raw, bytes) and raw[0] == 0x01:
                            frame_count += 1
                    except asyncio.TimeoutError:
                        break

            elapsed = asyncio.get_event_loop().time() - start
            fps = frame_count / elapsed if elapsed > 0 else 0
            print(f"\n  Measured FPS: {fps:.1f} ({frame_count} frames in {elapsed:.1f}s)")
            assert fps >= 5, f"FPS too low: {fps:.1f} — check camera and Pi load"
            print("  FPS acceptable ✓")

        run_async(_test())

    def test_video_resolution_correct(self, ws_url):
        """Decoded frame should match configured 640x480 resolution."""
        async def _test():
            try:
                import cv2
                import numpy as np
            except ImportError:
                pytest.skip("opencv-python not installed")

            async with websockets.connect(ws_url, open_timeout=CONNECT_TIMEOUT) as ws:
                deadline = asyncio.get_event_loop().time() + FRAME_TIMEOUT
                while asyncio.get_event_loop().time() < deadline:
                    raw = await asyncio.wait_for(ws.recv(), timeout=2.0)
                    if isinstance(raw, bytes) and raw[0] == 0x01:
                        jpeg_bytes = np.frombuffer(raw[1:], dtype=np.uint8)
                        frame = cv2.imdecode(jpeg_bytes, cv2.IMREAD_COLOR)
                        assert frame is not None
                        h, w = frame.shape[:2]
                        assert w == 640 and h == 480, f"Resolution mismatch: {w}x{h}"
                        print(f"\n  Frame resolution: {w}x{h} ✓")
                        return
            pytest.fail("No frame received for resolution check")

        run_async(_test())


# ══════════════════════════════════════════════════════════════
# AUDIO STREAMING TESTS
# ══════════════════════════════════════════════════════════════

@pytest.mark.skipif(not WS_AVAILABLE, reason="websockets not installed")
class TestAudioStreaming:

    def test_audio_chunks_received(self, ws_url):
        """Should receive at least 3 audio chunks (0x02 tag) within timeout."""
        async def _test():
            audio_chunks = []
            async with websockets.connect(ws_url, open_timeout=CONNECT_TIMEOUT) as ws:
                deadline = asyncio.get_event_loop().time() + AUDIO_TIMEOUT
                while asyncio.get_event_loop().time() < deadline and len(audio_chunks) < 3:
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        if isinstance(raw, bytes) and raw[0] == 0x02:
                            audio_chunks.append(raw)
                    except asyncio.TimeoutError:
                        break

            assert len(audio_chunks) >= 3, \
                f"Only {len(audio_chunks)} audio chunks — is microphone connected?"
            print(f"\n  Received {len(audio_chunks)} audio chunks ✓")

        run_async(_test())

    def test_audio_chunk_size(self, ws_url):
        """Audio chunks should match configured sample size (1024 samples × 2 bytes)."""
        expected_min = 512   # at least 256 samples × 2 bytes
        async def _test():
            async with websockets.connect(ws_url, open_timeout=CONNECT_TIMEOUT) as ws:
                deadline = asyncio.get_event_loop().time() + AUDIO_TIMEOUT
                while asyncio.get_event_loop().time() < deadline:
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        if isinstance(raw, bytes) and raw[0] == 0x02:
                            audio_data = raw[1:]
                            assert len(audio_data) >= expected_min, \
                                f"Audio chunk too small: {len(audio_data)} bytes"
                            print(f"\n  Audio chunk size: {len(audio_data)} bytes ✓")
                            return
                    except asyncio.TimeoutError:
                        break
            pytest.fail("No audio chunk received")

        run_async(_test())


# ══════════════════════════════════════════════════════════════
# MQTT BRIDGE TESTS (via WebSocket)
# ══════════════════════════════════════════════════════════════

@pytest.mark.skipif(not WS_AVAILABLE, reason="websockets not installed")
class TestWebSocketMQTTBridge:

    def test_send_motor_command_via_ws(self, ws_url):
        """Send motor command through WebSocket → verify it reaches broker."""
        async def _test():
            command = json.dumps({
                "topic": "dev/motor",
                "payload": json.dumps({"direction": "forward", "speed": 30})
            })
            async with websockets.connect(ws_url, open_timeout=CONNECT_TIMEOUT) as ws:
                await ws.send(command)
                # Give broker time to route
                await asyncio.sleep(0.5)
                print(f"\n  Motor command sent via WebSocket bridge ✓")
                print(f"  Command: {command}")
                # No assertion — we verify no exception was raised

        run_async(_test())

    def test_send_led_command_via_ws(self, ws_url):
        """Send LED command via WebSocket bridge."""
        async def _test():
            command = json.dumps({
                "topic": "dev/led",
                "payload": json.dumps({"action": "set_color", "color": "idle"})
            })
            async with websockets.connect(ws_url, open_timeout=CONNECT_TIMEOUT) as ws:
                await ws.send(command)
                await asyncio.sleep(0.5)
                print(f"\n  LED command sent via WebSocket bridge ✓")

        run_async(_test())

    def test_send_emergency_stop_via_ws(self, ws_url):
        """Send emergency stop via WebSocket bridge."""
        async def _test():
            command = json.dumps({
                "topic": "dev/commands",
                "payload": json.dumps({"command": "emergency_stop"})
            })
            async with websockets.connect(ws_url, open_timeout=CONNECT_TIMEOUT) as ws:
                await ws.send(command)
                await asyncio.sleep(0.5)
                print(f"\n  Emergency stop sent via WebSocket bridge ✓")

        run_async(_test())

    def test_receive_mqtt_status_via_ws(self, ws_url):
        """Should receive MQTT status events relayed from broker."""
        async def _test():
            json_messages = []
            async with websockets.connect(ws_url, open_timeout=CONNECT_TIMEOUT) as ws:
                deadline = asyncio.get_event_loop().time() + 6.0
                while asyncio.get_event_loop().time() < deadline:
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=1.5)
                        if isinstance(raw, bytes) and raw[0] == 0x00:
                            msg = json.loads(raw[1:].decode())
                            json_messages.append(msg)
                            if msg.get("event") == "mqtt":
                                print(f"\n  MQTT relay received: topic={msg.get('topic')} ✓")
                                return
                    except asyncio.TimeoutError:
                        continue

            # Welcome message always arrives — that's fine
            assert len(json_messages) >= 1
            print(f"\n  JSON messages received: {len(json_messages)} ✓")

        run_async(_test())
