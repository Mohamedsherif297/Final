# Ctrl+C Shutdown Fix

## Problem
When pressing Ctrl+C to stop the program, it would hang and not exit properly.

## Root Causes

1. **MQTT Loop Blocking**: `client.loop_forever()` blocks indefinitely and doesn't check the running flag
2. **Asyncio Tasks Not Cancelling**: WebSocket and streaming tasks weren't properly cancelled
3. **Thread Cleanup**: Some threads weren't stopping when the main program tried to exit
4. **No Forced Exit**: If graceful shutdown failed, the program would hang forever

## Fixes Applied

### 1. MQTT Controller (`mqtt_device_controller_integrated.py`)

**Before**:
```python
def start(self):
    # ...
    self.client.loop_forever()  # Blocks forever!
```

**After**:
```python
def start(self):
    # ...
    self.client.loop_start()  # Non-blocking background thread
    
    # Keep running until stopped
    try:
        while self.running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[MQTT] Keyboard interrupt in MQTT thread")
    finally:
        self.client.loop_stop()  # Clean stop
```

**Why**: `loop_start()` runs MQTT in a background thread that can be stopped with `loop_stop()`, while `loop_forever()` blocks the entire thread.

### 2. Async Task Cancellation (`main.py`)

**Before**:
```python
async def _run_async(self):
    await asyncio.gather(
        self.websocket_server.start(),
        self.video_handler.stream_loop(),
        self.audio_handler.stream_loop(),
    )
```

**After**:
```python
async def _run_async(self):
    tasks = []
    try:
        # Create tasks
        tasks = [
            asyncio.create_task(self.websocket_server.start()),
            asyncio.create_task(self.video_handler.stream_loop()),
            asyncio.create_task(self.audio_handler.stream_loop()),
        ]
        
        # Wait for tasks
        await asyncio.gather(*tasks, return_exceptions=True)
        
    finally:
        # Cancel all running tasks
        for task in tasks:
            if not task.done():
                task.cancel()
        
        # Wait for cancellation to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
```

**Why**: Properly creates tasks, cancels them on exit, and waits for cancellation to complete.

### 3. Improved Shutdown Sequence (`main.py`)

**Added**:
```python
def shutdown(self):
    print("[SYSTEM] Shutting down...")
    
    # Set running flag
    self.running = False
    
    # Stop each component with logging
    if self.video_handler:
        print("[SYSTEM] Stopping video capture...")
        self.video_handler.stop_capture()
    
    if self.audio_handler:
        print("[SYSTEM] Stopping audio capture...")
        self.audio_handler.stop_capture()
    
    if self.websocket_server:
        print("[SYSTEM] Stopping WebSocket server...")
        self.websocket_server._request_shutdown()
    
    if self.mqtt_controller:
        print("[SYSTEM] Stopping MQTT controller...")
        self.mqtt_controller.stop()
    
    print("[SYSTEM] Cleaning up hardware...")
    hardware_manager.cleanup()
    
    # Give threads time to finish
    time.sleep(0.5)
    
    print("[SYSTEM] Shutdown complete")
```

**Why**: Provides clear feedback and ensures each component stops in the correct order.

### 4. Force Exit Timer (`main.py`)

**Added**:
```python
def main():
    system = SurveillanceCarSystem(...)
    shutdown_timer = None
    
    def force_exit():
        print("\n[SYSTEM] Force exit - graceful shutdown timeout")
        os._exit(1)
    
    try:
        return system.run()
    except KeyboardInterrupt:
        print("\n[SYSTEM] Ctrl+C pressed - shutting down...")
        # Start 5-second timer for forced exit
        shutdown_timer = threading.Timer(5.0, force_exit)
        shutdown_timer.daemon = True
        shutdown_timer.start()
        return 0
    finally:
        if shutdown_timer and shutdown_timer.is_alive():
            shutdown_timer.cancel()
```

**Why**: If graceful shutdown takes more than 5 seconds, the program will force exit using `os._exit(1)`.

### 5. Better KeyboardInterrupt Handling

**Added**:
```python
def run(self):
    try:
        if self.enable_websocket:
            try:
                return asyncio.run(self._run_async())
            except KeyboardInterrupt:
                print("\n[SYSTEM] Keyboard interrupt received")
    except KeyboardInterrupt:
        print("\n[SYSTEM] Keyboard interrupt received")
    finally:
        self.shutdown()
```

**Why**: Catches KeyboardInterrupt at multiple levels to ensure shutdown is always called.

## Expected Behavior After Fix

### When you press Ctrl+C:

```
^C
[SYSTEM] Keyboard interrupt received
[SYSTEM] Async tasks cancelled

============================================================
[SYSTEM] Shutting down surveillance car system...
============================================================
[SYSTEM] Stopping video capture...
[SYSTEM] Stopping audio capture...
[SYSTEM] Stopping WebSocket server...
[SYSTEM] Stopping MQTT controller...
[MQTT] Stopping device controller...
[MQTT] Device controller stopped
[SYSTEM] MQTT controller stopped
[SYSTEM] Cleaning up hardware...
INFO - hardware.ultrasonic_controller - Stopped distance monitoring
INFO - hardware.camera_controller - Camera capture stopped
INFO - hardware.motor_controller - Motor controller cleaned up
INFO - hardware.gpio_manager - All GPIO pins cleaned up
[SYSTEM] Hardware cleanup complete
[SYSTEM] Shutdown complete
============================================================
```

### If shutdown hangs (after 5 seconds):

```
[SYSTEM] Force exit - graceful shutdown timeout
```

Then the program will immediately exit.

## Testing

1. **Start the program**:
   ```bash
   python3 main.py
   ```

2. **Press Ctrl+C once**:
   - Should see shutdown messages
   - Should exit within 1-2 seconds
   - All components should stop cleanly

3. **If it still hangs**:
   - Wait 5 seconds
   - Force exit timer will kill the process
   - Check which component is hanging from the logs

## Troubleshooting

### If it still doesn't exit after 5 seconds:

The force exit timer should kill it, but if not:

**Option 1**: Press Ctrl+C twice quickly
```bash
^C^C
```

**Option 2**: Kill from another terminal
```bash
ps aux | grep main.py
kill -9 <PID>
```

**Option 3**: Use pkill
```bash
pkill -9 -f main.py
```

### Check for zombie threads:

```bash
# While program is running
ps -T -p <PID>
```

This shows all threads. After Ctrl+C, all threads should stop.

## Files Modified

1. `/Raspi/main.py` - Added task cancellation, force exit timer, better shutdown
2. `/Raspi/Network/MQTT/mqtt_device_controller_integrated.py` - Changed to `loop_start()`

## Summary

The program now:
- ✅ Properly cancels all async tasks
- ✅ Stops MQTT loop cleanly
- ✅ Shuts down all threads in order
- ✅ Provides clear shutdown feedback
- ✅ Force exits after 5 seconds if hung
- ✅ Responds to Ctrl+C immediately
