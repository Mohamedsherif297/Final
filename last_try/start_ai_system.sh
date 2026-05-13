#!/bin/bash
# Start Integrated AI Surveillance Car System

echo "=========================================="
echo "  Surveillance Car - AI Integrated"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run with sudo:"
    echo "   sudo ./start_ai_system.sh"
    exit 1
fi

# Check dependencies
echo "Checking dependencies..."

python3 -c "import mediapipe" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  MediaPipe not installed"
    echo "   Install: pip3 install mediapipe --break-system-packages"
    exit 1
fi

python3 -c "import face_recognition" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  face_recognition not installed"
    echo "   Install: pip3 install face_recognition --break-system-packages"
    exit 1
fi

echo "✓ Dependencies OK"
echo ""

# Check known faces
if [ ! -d "pi_minimal/known_faces" ]; then
    echo "⚠️  Known faces directory not found"
    echo "   Creating: pi_minimal/known_faces/"
    mkdir -p pi_minimal/known_faces
    echo "   Add face photos to this directory before using AI mode"
fi

FACE_COUNT=$(find pi_minimal/known_faces -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) 2>/dev/null | wc -l)
echo "📸 Known faces: $FACE_COUNT photos loaded"
echo ""

# Start system
echo "Starting integrated system..."
echo "Press Ctrl+C to stop"
echo ""
echo "💡 Control Modes:"
echo "   • Manual: MQTT/Dashboard control"
echo "   • AI Follow: Autonomous face tracking"
echo ""
echo "🌐 Dashboard: Open Dashboard/index.html"
echo "   Enter Pi IP: $(hostname -I | awk '{print $1}')"
echo ""
echo "=========================================="
echo ""

# Run with Python 3
python3 run_all_integrated.py
