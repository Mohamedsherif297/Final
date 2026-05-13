# Ngrok Setup for WAN Video Streaming

## Quick Start (You Already Have Ngrok Account)

### Step 1: Install Ngrok on Raspberry Pi

```bash
# Download and install
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update
sudo apt install ngrok
```

### Step 2: Configure with Your Authtoken

```bash
# Replace YOUR_AUTHTOKEN with your actual token from ngrok dashboard
ngrok config add-authtoken YOUR_AUTHTOKEN
```

### Step 3: Start the System

**Terminal 1** - Start the car system:
```bash
cd ~/surveillance-car/last_try
sudo python3 run_all.py
```

**Terminal 2** - Start ngrok tunnel:
```bash
ngrok tcp 8765
```

### Step 4: Get Your Public URL

Ngrok will show something like:
```
Forwarding    tcp://0.tcp.ngrok.io:12345 -> localhost:8765
```

**Copy this URL**: `0.tcp.ngrok.io:12345`

### Step 5: Connect from Anywhere

1. Open dashboard from **any device, any network**
2. Enter the ngrok URL: `0.tcp.ngrok.io:12345`
3. Click Connect
4. ✅ Video streaming + motor control from anywhere!

---

## How It Works

```
Your Phone (4G/5G)
        ↓
    Internet
        ↓
   Ngrok Cloud
        ↓
  Ngrok Tunnel (tcp://0.tcp.ngrok.io:12345)
        ↓
Raspberry Pi (localhost:8765)
        ↓
   WebSocket Server
        ↓
    Video Stream
```

- **MQTT (HiveMQ)**: Already works over WAN ✅
- **WebSocket (Ngrok)**: Now works over WAN ✅

---

## Important Notes

### Free Plan Limitations:
- ⚠️ **URL changes every restart** (e.g., `0.tcp.ngrok.io:12345` → `1.tcp.ngrok.io:54321`)
- ⚠️ **1 tunnel at a time** (can't run multiple ngrok instances)
- ⚠️ **Session timeout after 8 hours** (need to restart)
- ✅ **Unlimited bandwidth** (free!)

### Paid Plan Benefits ($8/month):
- ✅ **Fixed URL** (e.g., `mycar.tcp.ngrok.io:8765`)
- ✅ **Multiple tunnels**
- ✅ **No session timeout**
- ✅ **Custom domains**

---

## Troubleshooting

### "ngrok: command not found"
```bash
# Install ngrok first (see Step 1)
```

### "authentication failed"
```bash
# Add your authtoken (see Step 2)
ngrok config add-authtoken YOUR_TOKEN
```

### "tunnel session failed"
```bash
# Check if another ngrok is running
pkill ngrok

# Try again
ngrok tcp 8765
```

### Dashboard can't connect
1. **Check ngrok is running** - should show "Session Status: online"
2. **Copy exact URL** - including port number (e.g., `:12345`)
3. **Use TCP URL** - not HTTP (should be `0.tcp.ngrok.io:12345`)
4. **Check firewall** - ngrok should handle this automatically

---

## Alternative: Auto-Start Script

Make the script executable:
```bash
chmod +x start_with_ngrok.sh
```

Run everything at once:
```bash
./start_with_ngrok.sh
```

This starts both `run_all.py` and `ngrok` together!

---

## Getting Ngrok URL Programmatically

```bash
# Get public URL from ngrok API
curl http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'
```

Or visit: http://localhost:4040 (ngrok web interface)

---

## Security Recommendations

1. **Don't share your ngrok URL publicly** - anyone with the URL can access your car
2. **Change ngrok URL regularly** - restart ngrok to get a new URL
3. **Add authentication** - consider adding password protection to dashboard
4. **Monitor connections** - check ngrok web interface at http://localhost:4040
5. **Use paid plan for production** - get fixed URL and better security

---

## Next Steps

1. ✅ Install ngrok on Pi
2. ✅ Configure with your authtoken
3. ✅ Start `run_all.py`
4. ✅ Start `ngrok tcp 8765`
5. ✅ Copy ngrok URL
6. ✅ Connect from anywhere!

**Your car is now accessible from anywhere in the world!** 🌍🚗📹
