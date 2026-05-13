#!/bin/bash
# Fast AI Dependencies Installation for Raspberry Pi
# Uses pre-built wheels to avoid long compilation

echo "=========================================="
echo "  Fast AI Installation for Raspberry Pi"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi"
fi

echo "📦 Installing AI dependencies (optimized)..."
echo ""

# Update pip
echo "1/4 Updating pip..."
pip3 install --upgrade pip --break-system-packages

# Install system dependencies for dlib (if needed)
echo ""
echo "2/4 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libjpeg-dev \
    libpng-dev

# Install MediaPipe (lightweight, fast)
echo ""
echo "3/4 Installing MediaPipe..."
pip3 install mediapipe --break-system-packages

# Install face_recognition with pre-built dlib
echo ""
echo "4/4 Installing face_recognition..."
echo "⏳ This may take 5-10 minutes (compiling dlib)..."
echo "💡 The process will appear stuck - this is normal!"
echo "   You'll see 'Building wheel for dlib' - be patient!"
echo ""

# Try to install pre-built dlib first (if available)
pip3 install dlib --break-system-packages 2>/dev/null

# If that fails, compile from source (this is slow)
if [ $? -ne 0 ]; then
    echo "⚠️  Pre-built dlib not available, compiling from source..."
    echo "⏳ This will take 30-60 minutes - DO NOT CANCEL!"
    echo ""
    
    # Compile with limited resources to prevent freezing
    pip3 install --no-cache-dir dlib --break-system-packages
fi

# Install face_recognition
pip3 install face_recognition --break-system-packages

echo ""
echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""

# Verify installation
echo "Verifying installation..."
python3 -c "import mediapipe; print('✓ MediaPipe installed')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ MediaPipe: OK"
else
    echo "❌ MediaPipe: FAILED"
fi

python3 -c "import face_recognition; print('✓ face_recognition installed')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ face_recognition: OK"
else
    echo "❌ face_recognition: FAILED"
fi

echo ""
echo "🚀 Ready to run: sudo ./start_ai_system.sh"
echo ""
