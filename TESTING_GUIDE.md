# Testing Guide - After Fixes

## Quick Test Checklist

### ✅ Test 1: Clean Startup
```bash
cd "/Users/user/IOT /Final/Raspi"
python3 main.py
```

**Expected**: 
- No GPIO warnings
- No ALSA errors  
- No OpenCV warnings
- Clean initialization messages

**Pass Criteria**: Console shows only INFO messages, no warnings or errors

---

### ✅ Test 2: Obstacle Detection
**Action**: Place an object in front of the ultrasonic sensor (< 15cm)

**Expected**:
```
[OBSTACLE] Emergency! Detected at 10.05cm
```

**Action**: Remove the object (> 30cm)

**Expected**:
```
[OBSTACLE] Clear - 45.23cm
```

**Pass Criteria**: 
- Only ONE message when entering emergency state
- Only ONE message when clearing
- NO repeated spam

---

### ✅ Test 3: Ctrl+C Shutdown
**Action**: Press Ctrl+C once

**Expected**:
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
[SYSTEM] Cleaning up hardware...
[SYSTEM] Shutdown complete
============================================================
```

**Pass Criteria**:
- Program exits within 1-2 seconds
- All components stop cleanly
- Returns to command prompt

---

### ✅ Test 4: MQTT Commands
**Setup**: In another terminal, install mosquitto clients:
```bash
sudo apt-get install mosquitto-clients
```

**Test Motor Command**:
```bash
mosquitto_pub -h localhost -t "dev/motor" -m '{"direction":"forward","speed":50}'
```

**Expected**: 
- Motor moves forward
- No errors in main program console

**Test Stop**:
```bash
mosquitto_pub -h localhost -t "dev/motor" -m '{"direction":"stop"}'
```

**Pass Criteria**: Commands work without errors

---

### ✅ Test 5: WebSocket Connection
**Action**: Open the dashboard in a browser or use a WebSocket client

**Expected**:
- WebSocket connects successfully
- Video stream appears (if camera available)
- No connection errors

**Pass Criteria**: WebSocket connection established

---

## Troubleshooting

### Issue: Program still shows warnings

**Check**:
```bash
# Verify you're running the correct file
which python3
python3 --version

# Check if changes were saved
grep "OPENCV_LOG_LEVEL" /Users/user/IOT\ /Final/Raspi/main.py
```

---

### Issue: Ctrl+C still doesn't work

**Try**:
1. Wait 5 seconds (force exit timer)
2. Press Ctrl+C twice quickly
3. From another terminal:
   ```bash
   pkill -9 -f main.py
   ```

---

### Issue: Camera not working

**Check**:
```bash
# List cameras
ls -la /dev/video*

# Test camera
v4l2-ctl --list-devices

# Try capturing a test image
ffmpeg -f v4l2 -i /dev/video0 -frames 1 test.jpg
```

---

### Issue: MQTT not connecting

**Check**:
```bash
# Is mosquitto running?
sudo systemctl status mosquitto

# Start if needed
sudo systemctl start mosquitto

# Test connection
mosquitto_pub -h localhost -t "test" -m "hello"
```

---

## Performance Checks

### CPU Usage
```bash
# While program is running
top -p $(pgrep -f main.py)
```

**Expected**: 20-40% CPU usage (varies with camera/streaming)

---

### Memory Usage
```bash
# Check memory
ps aux | grep main.py
```

**Expected**: 50-150 MB RAM usage

---

### Thread Count
```bash
# Check threads
ps -T -p $(pgrep -f main.py) | wc -l
```

**Expected**: 8-12 threads

---

## Success Criteria Summary

| Test | Criteria | Status |
|------|----------|--------|
| Clean Startup | No warnings/errors | ⬜ |
| Obstacle Detection | Only logs on changes | ⬜ |
| Ctrl+C Shutdown | Exits in 1-2 seconds | ⬜ |
| MQTT Commands | Commands work | ⬜ |
| WebSocket | Connects successfully | ⬜ |

**All tests should pass** ✅

---

## What to Do If Tests Fail

### 1. Check the logs
Look for error messages in the console output

### 2. Verify hardware connections
- Ultrasonic sensor: Trigger=GPIO23, Echo=GPIO24
- Motors: Check pin definitions
- Camera: Check /dev/video0 exists

### 3. Check dependencies
```bash
pip3 list | grep -E "opencv|paho-mqtt|websockets|pyaudio|RPi.GPIO"
```

### 4. Review documentation
- `FIXES_APPLIED.md` - Console spam fixes
- `CTRL_C_FIX.md` - Shutdown fixes
- `ALL_FIXES_SUMMARY.md` - Complete summary

---

## After Testing

If all tests pass:
1. ✅ System is working correctly
2. ✅ All fixes are applied successfully
3. ✅ Ready for normal operation

If any test fails:
1. Check the specific troubleshooting section
2. Review the relevant documentation
3. Verify hardware connections
4. Check system logs

---

## Normal Operation

Once testing is complete, you can run the system normally:

```bash
cd "/Users/user/IOT /Final/Raspi"
python3 main.py
```

To stop:
- Press **Ctrl+C** once
- Wait for clean shutdown (1-2 seconds)
- If it hangs, wait 5 seconds for force exit

---

## Monitoring

### View logs in real-time:
```bash
python3 main.py 2>&1 | tee surveillance_car.log
```

### Check system health:
```bash
# CPU temperature (Raspberry Pi)
vcgencmd measure_temp

# System load
uptime

# Disk space
df -h
```

---

## Tips

1. **Always use Ctrl+C once** - Don't spam it
2. **Wait for shutdown messages** - Give it time to clean up
3. **Check hardware before starting** - Verify connections
4. **Monitor the first run** - Watch for any unexpected behavior
5. **Keep logs** - Use `tee` to save output for debugging

---

## Success! 🎉

If all tests pass, your surveillance car system is:
- ✅ Running cleanly without spam
- ✅ Responding to commands properly
- ✅ Shutting down gracefully
- ✅ Ready for production use

Enjoy your surveillance car! 🚗📹
