#!/bin/bash
# Start AI Lite System (No face recognition - faster!)

echo "=========================================="
echo "  Surveillance Car - AI Lite"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run with sudo:"
    echo "   sudo ./start_ai_lite.sh"
    exit 1
fi

# Check MediaPipe only (no face_recognition needed!)
echo "Checking dependencies..."

python3 -c "import mediapipe" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  MediaPipe not installed"
    echo "   Install: pip3 install mediapipe --break-system-packages"
    echo ""
    read -p "Install now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip3 install mediapipe --break-system-packages
    else
        exit 1
    fi
fi

echo "✓ Dependencies OK"
echo ""

echo "Starting AI Lite system..."
echo "Press Ctrl+C to stop"
echo ""
echo "💡 AI Lite Mode:"
echo "   • Follows ANY person (no recognition)"
echo "   • Much faster and lighter"
echo "   • Only needs MediaPipe"
echo ""
echo "🌐 Dashboard: Open Dashboard/index.html"
echo "   Enter Pi IP: $(hostname -I | awk '{print $1}')"
echo ""
echo "=========================================="
echo ""

# Run lite version
python3 run_all_integrated_lite.py
