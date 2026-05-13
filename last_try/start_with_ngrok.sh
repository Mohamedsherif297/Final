#!/bin/bash
# Start surveillance car with Ngrok WAN access

echo "=========================================="
echo "Surveillance Car - WAN Access via Ngrok"
echo "=========================================="

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ Ngrok not installed!"
    echo ""
    echo "Install with:"
    echo "  curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null"
    echo "  echo 'deb https://ngrok-agent.s3.amazonaws.com buster main' | sudo tee /etc/apt/sources.list.d/ngrok.list"
    echo "  sudo apt update && sudo apt install ngrok"
    echo ""
    echo "Then configure with your authtoken:"
    echo "  ngrok config add-authtoken YOUR_TOKEN"
    exit 1
fi

# Check if authtoken is configured
if ! ngrok config check &> /dev/null; then
    echo "❌ Ngrok not configured!"
    echo ""
    echo "Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "Then run: ngrok config add-authtoken YOUR_TOKEN"
    exit 1
fi

echo ""
echo "Starting services..."
echo ""

# Start run_all.py in background
echo "[1/2] Starting surveillance car system..."
sudo python3 run_all.py &
RUN_ALL_PID=$!

# Wait for WebSocket server to start
sleep 5

# Start ngrok tunnel
echo "[2/2] Starting Ngrok tunnel..."
ngrok tcp 8765 --log=stdout &
NGROK_PID=$!

# Wait a bit for ngrok to connect
sleep 3

# Get ngrok public URL
echo ""
echo "=========================================="
echo "✅ System Running!"
echo "=========================================="
echo ""
echo "🌐 Get your public URL:"
echo "   http://localhost:4040"
echo ""
echo "Or run in another terminal:"
echo "   curl http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'"
echo ""
echo "📱 Connect from dashboard:"
echo "   Enter the ngrok URL (e.g., 0.tcp.ngrok.io:12345)"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=========================================="

# Trap Ctrl+C to cleanup
trap "echo ''; echo 'Stopping services...'; kill $RUN_ALL_PID $NGROK_PID 2>/dev/null; exit" INT

# Wait for user to stop
wait
