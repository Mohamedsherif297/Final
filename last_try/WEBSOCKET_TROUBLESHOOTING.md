# WebSocket Connection Troubleshooting

## Problem: Dashboard connects to MQTT but not WebSocket (no video)

### Step 1: Find Your Pi's IP Address
```bash
hostname -I
```
**Example output:** `192.168.1.100 172.17.0.1`
- Use the **first IP** (192.168.1.100)
- This is your LOCAL network IP

### Step 2: Test WebSocket Server Alone
```bash
cd ~/surveillance-car/last_try
python3 test_websocket.py
```

**Expected output:**
```
============================================================
WebSocket Test Server
============================================================
Host: 0.0.0.0
Port: 8765
============================================================

Starting server...
Connect from dashboard using: ws://YOUR_PI_IP:8765

Waiting for connections...
```

### Step 3: Connect from Dashboard
1. Open dashboard in browser
2. Enter Pi IP: `192.168.1.100` (use YOUR actual IP)
3. Click "Connect"

**If WebSocket works, you'll see on Pi:**
```
✅ Client connected: ('192.168.1.50', 54321)
   Sent welcome to ('192.168.1.50', 54321)
```

**If nothing appears** → WebSocket connection is blocked

### Step 4: Check Common Issues

#### Issue A: Wrong IP Address
❌ **WRONG**: Entering HiveMQ Cloud address
❌ **WRONG**: Entering `localhost` or `127.0.0.1`
✅ **CORRECT**: Your Pi's LOCAL IP (e.g., `192.168.1.100`)

**How to verify:**
```bash
# On Pi, run:
hostname -I

# On your computer, ping the Pi:
ping 192.168.1.100
```

#### Issue B: Port 8765 Already in Use
```bash
# Check if port is in use
sudo netstat -tulpn | grep 8765

# If something is using it, kill it:
sudo kill -9 <PID>
```

#### Issue C: Firewall Blocking
```bash
# Check firewall status
sudo ufw status

# If active, allow port 8765
sudo ufw allow 8765
```

#### Issue D: Camera Not Opening (Causes run_all.py to fail)
```bash
# Test camera
python3 -c "import cv2; cam = cv2.VideoCapture(0); print('✅ Camera OK' if cam.isOpened() else '❌ Camera FAILED'); cam.release()"

# Check camera device
ls -l /dev/video*
```

### Step 5: Check Browser Console
1. Open dashboard
2. Press **F12** (or Cmd+Option+I on Mac)
3. Go to **Console** tab
4. Try to connect
5. Look for errors

**Common errors:**
- `WebSocket connection failed` → Can't reach Pi
- `Connection refused` → Server not running
- `Connection timeout` → Wrong IP or firewall

### Step 6: Run Full System with Verbose Output

If test_websocket.py works, try run_all.py:

```bash
cd ~/surveillance-car/last_try
sudo python3 run_all.py
```

**Watch for these messages:**
```
[Camera] Opening camera...          ← Should appear
[Camera] Streaming 640x480 @ 20fps  ← Should appear
[WebSocket] Starting server...      ← Should appear
[WebSocket] Client connected: ...   ← Should appear when dashboard connects
```

**If camera fails:**
```
[Camera] Failed to open
```
→ Camera issue, WebSocket won't work

### Step 7: Network Connectivity Test

**On Raspberry Pi:**
```bash
# Get Pi IP
hostname -I
# Example: 192.168.1.100

# Check if WebSocket port is listening
sudo netstat -tulpn | grep 8765
# Should show: tcp 0.0.0.0:8765 LISTEN
```

**On your computer (same network):**
```bash
# Ping Pi
ping 192.168.1.100

# Test WebSocket port (if you have netcat)
nc -zv 192.168.1.100 8765
```

### Quick Diagnostic Commands

Run these on Raspberry Pi:

```bash
# 1. Check IP
echo "Pi IP: $(hostname -I | awk '{print $1}')"

# 2. Check camera
python3 -c "import cv2; print('Camera:', 'OK' if cv2.VideoCapture(0).isOpened() else 'FAILED')"

# 3. Check if websockets library is installed
python3 -c "import websockets; print('websockets:', websockets.__version__)"

# 4. Check if port 8765 is available
sudo netstat -tulpn | grep 8765 || echo "Port 8765 is available"
```

### Solution Checklist

- [ ] Pi IP address is correct (use `hostname -I`)
- [ ] Dashboard is using Pi's LOCAL IP (not HiveMQ address)
- [ ] WebSocket test server works (`python3 test_websocket.py`)
- [ ] Camera opens successfully
- [ ] Port 8765 is not blocked by firewall
- [ ] Browser console shows no errors
- [ ] Pi and computer are on same network

### Still Not Working?

**Try this minimal test:**

1. **On Pi:**
   ```bash
   python3 test_websocket.py
   ```

2. **In browser console (F12):**
   ```javascript
   ws = new WebSocket('ws://192.168.1.100:8765');
   ws.onopen = () => console.log('✅ Connected!');
   ws.onerror = (e) => console.log('❌ Error:', e);
   ```

If this works → Problem is in run_all.py
If this fails → Network/firewall issue
