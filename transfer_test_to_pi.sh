#!/bin/bash

# Transfer test_hardware.py and required files to Raspberry Pi
# Pi IP: 192.168.1.9

PI_IP="192.168.1.9"
PI_USER="pi"  # Change if your username is different

echo "============================================================"
echo "  📡 Transferring Hardware Test Files to Raspberry Pi"
echo "============================================================"
echo "Pi IP: $PI_IP"
echo "User: $PI_USER"
echo ""
echo "⚠️  You will be prompted for the Pi password multiple times"
echo "   (This is normal - once for each file/folder transfer)"
echo ""

# Check if we're in the Final directory
if [ ! -f "test_hardware.py" ]; then
    echo "❌ Error: Please run this script from the Final folder"
    echo "Current directory: $(pwd)"
    exit 1
fi

# Check if Pi is reachable
echo "🔍 Checking if Pi is reachable..."
ping -c 1 -W 3 $PI_IP > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Cannot reach Raspberry Pi at $PI_IP"
    echo ""
    echo "Please check:"
    echo "1. Pi is powered on"
    echo "2. Pi is connected to network"
    echo "3. IP address is correct: $PI_IP"
    echo ""
    echo "To verify Pi's IP:"
    echo "- On Pi (via VNC): Open terminal and run: hostname -I"
    exit 1
fi

echo "✅ Pi is reachable at $PI_IP"
echo ""

# Create Final directory on Pi if it doesn't exist
echo "📁 Creating Final directory on Pi..."
echo "   (Enter Pi password when prompted)"
ssh $PI_USER@$PI_IP "mkdir -p ~/Final/Raspi"
if [ $? -eq 0 ]; then
    echo "✅ Directory created/verified"
else
    echo "❌ Failed to create directory. Check SSH password."
    echo ""
    echo "💡 Make sure:"
    echo "   1. SSH is enabled on Pi (sudo raspi-config → Interface → SSH)"
    echo "   2. You're using the correct password"
    echo "   3. Username is 'pi' (or change PI_USER in this script)"
    exit 1
fi

echo ""
echo "📤 Transferring files..."
echo ""

# Transfer test_hardware.py
echo "  [1/4] Transferring test_hardware.py..."
scp test_hardware.py $PI_USER@$PI_IP:~/Final/
if [ $? -eq 0 ]; then
    echo "  ✅ test_hardware.py transferred"
else
    echo "  ❌ Failed to transfer test_hardware.py"
    exit 1
fi

# Transfer Raspi/Drivers folder (all hardware modules)
echo ""
echo "  [2/4] Transferring Raspi/Drivers/ folder (36 hardware modules)..."
scp -r Raspi/Drivers $PI_USER@$PI_IP:~/Final/Raspi/
if [ $? -eq 0 ]; then
    echo "  ✅ Drivers folder transferred"
else
    echo "  ❌ Failed to transfer Drivers folder"
    exit 1
fi

# Transfer Raspi/config folder (YAML configs)
echo ""
echo "  [3/4] Transferring Raspi/config/ folder (YAML configs)..."
scp -r Raspi/config $PI_USER@$PI_IP:~/Final/Raspi/
if [ $? -eq 0 ]; then
    echo "  ✅ Config folder transferred"
else
    echo "  ❌ Failed to transfer config folder"
    exit 1
fi

# Transfer requirements.txt
echo ""
echo "  [4/4] Transferring Raspi/requirements.txt..."
scp Raspi/requirements.txt $PI_USER@$PI_IP:~/Final/Raspi/
if [ $? -eq 0 ]; then
    echo "  ✅ requirements.txt transferred"
else
    echo "  ❌ Failed to transfer requirements.txt"
    exit 1
fi

echo ""
echo "============================================================"
echo "  ✅ All files transferred successfully!"
echo "============================================================"
echo ""
echo "📊 Transferred files:"
echo "  ✅ test_hardware.py"
echo "  ✅ Raspi/Drivers/ (36 hardware modules)"
echo "  ✅ Raspi/config/ (4 YAML files)"
echo "  ✅ Raspi/requirements.txt"
echo ""
echo "🚀 Next steps on Raspberry Pi:"
echo ""
echo "1. SSH into Pi:"
echo "   ssh $PI_USER@$PI_IP"
echo ""
echo "2. Install dependencies:"
echo "   cd ~/Final/Raspi"
echo "   pip3 install -r requirements.txt"
echo ""
echo "3. Run the hardware test:"
echo "   cd ~/Final"
echo "   python3 test_hardware.py"
echo ""
echo "💡 Or use VNC to open terminal on Pi and run the commands above"
echo ""
echo "⚠️  Make sure hardware is connected before running test!"
echo ""
