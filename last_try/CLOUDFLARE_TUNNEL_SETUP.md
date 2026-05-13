# Cloudflare Tunnel Setup for WAN Access (FREE)

## Why Cloudflare Tunnel?
- ✅ **100% Free** (no credit card needed)
- ✅ **Permanent URL** (doesn't change on restart)
- ✅ **Fast & Reliable** (Cloudflare's global network)
- ✅ **Secure** (encrypted tunnel)
- ✅ **No port forwarding** needed

---

## Step 1: Install Cloudflared on Raspberry Pi

```bash
# Download and install cloudflared
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb

# Install
sudo dpkg -i cloudflared.deb

# Verify installation
cloudflared --version
```

---

## Step 2: Login to Cloudflare

```bash
cloudflared tunnel login
```

This will:
1. Open a browser window (or give you a URL to open)
2. Ask you to login to Cloudflare (create free account if needed)
3. Select a domain (or use Cloudflare's free subdomain)
4. Authorize the tunnel

**Note**: If you don't have a domain, Cloudflare will give you a free `.trycloudflare.com` subdomain.

---

## Step 3: Create a Tunnel

```bash
# Create a named tunnel
cloudflared tunnel create surveillance-car
```

This creates a tunnel and saves credentials to:
`~/.cloudflared/<TUNNEL-ID>.json`

**Copy the Tunnel ID** shown in the output (e.g., `abc123-def456-ghi789`)

---

## Step 4: Create Configuration File

```bash
# Create config directory
mkdir -p ~/.cloudflared

# Create config file
nano ~/.cloudflared/config.yml
```

**Paste this configuration** (replace `TUNNEL-ID` with your actual tunnel ID):

```yaml
tunnel: TUNNEL-ID
credentials-file: /home/iot/.cloudflared/TUNNEL-ID.json

ingress:
  - hostname: car.yourdomain.com
    service: tcp://localhost:8765
  - service: http_status:404
```

**If you don't have a domain**, use this instead:

```yaml
tunnel: TUNNEL-ID
credentials-file: /home/iot/.cloudflared/TUNNEL-ID.json

ingress:
  - service: tcp://localhost:8765
```

Save and exit (Ctrl+X, Y, Enter)

---

## Step 5: Route the Tunnel (If Using Custom Domain)

**Only if you have a domain:**

```bash
# Route your domain to the tunnel
cloudflared tunnel route dns surveillance-car car.yourdomain.com
```

**If using free subdomain**, skip this step.

---

## Step 6: Start the Tunnel

```bash
cloudflared tunnel run surveillance-car
```

You should see:
```
INF Starting tunnel tunnelID=abc123-def456-ghi789
INF Connection registered connIndex=0 location=ATL
INF Connection registered connIndex=1 location=DFW
```

**Your tunnel is now running!**

---

## Step 7: Get Your Public URL

### If you used a custom domain:
Your URL is: `car.yourdomain.com`

### If you used free subdomain:
Run this to get the URL:
```bash
cloudflared tunnel info surveillance-car
```

Or check the Cloudflare dashboard at: https://one.dash.cloudflare.com/

---

## Step 8: Connect from Dashboard

1. **Start the car system** (Terminal 1):
   ```bash
   cd ~/surveillance-car/last_try
   sudo python3 run_all.py
   ```

2. **Start Cloudflare tunnel** (Terminal 2):
   ```bash
   cloudflared tunnel run surveillance-car
   ```

3. **Open dashboard** from any device
4. **Enter your Cloudflare URL**: `car.yourdomain.com` or `abc123.trycloudflare.com`
5. **Click Connect**

---

## Auto-Start on Boot (Optional)

### Install as a service:

```bash
# Install the service
sudo cloudflared service install

# Enable auto-start
sudo systemctl enable cloudflared

# Start the service
sudo systemctl start cloudflared

# Check status
sudo systemctl status cloudflared
```

Now the tunnel starts automatically when Pi boots!

---

## Quick Start Script

Create a script to start everything:

```bash
nano ~/start_car.sh
```

Paste:
```bash
#!/bin/bash
echo "Starting Surveillance Car with Cloudflare Tunnel..."

# Start car system in background
cd ~/surveillance-car/last_try
sudo python3 run_all.py &

# Wait for system to start
sleep 5

# Start Cloudflare tunnel
cloudflared tunnel run surveillance-car
```

Make executable:
```bash
chmod +x ~/start_car.sh
```

Run:
```bash
~/start_car.sh
```

---

## Troubleshooting

### "cloudflared: command not found"
```bash
# Check if installed
which cloudflared

# If not found, reinstall
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
sudo dpkg -i cloudflared.deb
```

### "tunnel credentials file not found"
```bash
# List your tunnels
cloudflared tunnel list

# Check credentials exist
ls ~/.cloudflared/
```

### "connection failed"
1. Check if `run_all.py` is running
2. Check if WebSocket is listening: `sudo netstat -tulpn | grep 8765`
3. Check Cloudflare tunnel logs: `cloudflared tunnel info surveillance-car`

### Dashboard can't connect
1. **Use the correct URL** (no `ws://` or `tcp://` prefix)
2. **Check tunnel is running**: `cloudflared tunnel info surveillance-car`
3. **Try from different network** to test WAN access

---

## Cloudflare Dashboard

View your tunnels at: https://one.dash.cloudflare.com/

You can:
- See tunnel status
- View traffic analytics
- Manage DNS records
- Configure access policies

---

## Comparison: Cloudflare vs Ngrok

| Feature | Cloudflare Tunnel | Ngrok (Free) | Ngrok (Paid) |
|---------|------------------|--------------|--------------|
| **Price** | Free | Free | $8/month |
| **TCP Support** | ✅ Yes | ❌ No | ✅ Yes |
| **Fixed URL** | ✅ Yes | ❌ No | ✅ Yes |
| **Custom Domain** | ✅ Yes | ❌ No | ✅ Yes |
| **Auto-restart** | ✅ Yes | ❌ No | ✅ Yes |
| **Bandwidth** | Unlimited | Unlimited | Unlimited |
| **Setup Complexity** | Medium | Easy | Easy |

---

## Security Tips

1. **Don't share your URL publicly** - anyone with the URL can access your car
2. **Use Cloudflare Access** - add authentication (free)
3. **Monitor traffic** - check Cloudflare dashboard regularly
4. **Rotate tunnel** - create new tunnel periodically
5. **Use strong passwords** - if adding authentication

---

## Next Steps

1. ✅ Install cloudflared
2. ✅ Login to Cloudflare
3. ✅ Create tunnel
4. ✅ Configure tunnel
5. ✅ Start tunnel
6. ✅ Connect from anywhere!

**Your car is now accessible from anywhere with a permanent URL!** 🌍🚗📹
