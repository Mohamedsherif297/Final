# Surveillance Car — Web Dashboard

A real-time browser dashboard for the IoT Surveillance Car.
No installation needed — just open `index.html` in any browser.

## Quick Start

1. Make sure the Pi is running `python3 main.py` (WebSocket enabled)
2. Open `Dashboard/index.html` in your browser
3. Type the Pi's IP address in the top-right input
4. Click **Connect**

## Controls

### Keyboard
| Key | Motor mode (default) | Servo mode |
|-----|----------------------|------------|
| `↑ ↓ ← →` | Move car | Move camera servo |
| `W A S D` | Move camera servo | Move car |
| `Space` | Stop motor | — |

Switch modes with the **Motor / Servo** tabs in the Movement panel.

### D-Pad Buttons
Click or tap the on-screen D-pad buttons. Motor mode moves the car;
Servo mode nudges the camera pan/tilt by 5° per press.

## Panels

| Panel | What it does |
|-------|-------------|
| **Live Feed** | 640×480 JPEG stream from Pi camera |
| **Movement** | D-pad + speed slider. Arrow key mode toggle |
| **Camera Servo** | Pan/Tilt sliders + crosshair position indicator |
| **LED** | Status presets, effects (rainbow/blink/pulse), RGB picker |
| **Emergency** | Big red stop button + reset |
| **Sensors** | Live ultrasonic distance gauge + system status badges |
| **Event Log** | Scrolling log of all commands and Pi events |

## Protocol

The dashboard uses a **single WebSocket connection** to `ws://PI_IP:8765`.

**Receiving:**
- `0x00` + JSON → status/MQTT events
- `0x01` + bytes → JPEG video frame
- `0x02` + bytes → PCM audio (unused in dashboard)

**Sending:**
```json
{ "topic": "dev/motor",   "payload": "{\"direction\":\"forward\",\"speed\":70}" }
{ "topic": "dev/servo",   "payload": "{\"action\":\"set_angle\",\"pan\":30,\"tilt\":-10}" }
{ "topic": "dev/led",     "payload": "{\"action\":\"set_color\",\"color\":\"moving\"}" }
{ "topic": "dev/commands","payload": "{\"command\":\"emergency_stop\"}" }
```

## File Structure

```
Dashboard/
├── index.html      ← Open this in browser
├── dashboard.css   ← Dark glassmorphism styles
├── dashboard.js    ← WebSocket + controls logic
└── README.md       ← This file
```
