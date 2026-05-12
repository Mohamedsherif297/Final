#!/bin/bash
# Setup script for Surveillance Car System
# Run this on your Raspberry Pi to set up the system

set -e  # Exit on error

echo "=========================================="
echo "Surveillance Car System - Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo -e "${YELLOW}Warning: This doesn't appear to be a Raspberry Pi${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo -e "${GREEN}[1/7] Updating system...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo -e "${GREEN}[2/7] Installing system dependencies...${NC}"
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    python3-rpi.gpio \
    python3-opencv \
    mosquitto \
    mosquitto-clients \
    git

# Install Python dependencies
echo -e "${GREEN}[3/7] Installing Python dependencies...${NC}"
pip3 install -r requirements.txt

# Setup GPIO permissions
echo -e "${GREEN}[4/7] Setting up GPIO permissions...${NC}"
sudo usermod -a -G gpio $USER
sudo usermod -a -G video $USER

# Enable camera (if available)
echo -e "${GREEN}[5/7] Checking camera...${NC}"
if vcgencmd get_camera &>/dev/null; then
    echo "Camera interface detected"
else
    echo -e "${YELLOW}Camera not detected - you may need to enable it in raspi-config${NC}"
fi

# Setup Mosquitto MQTT broker
echo -e "${GREEN}[6/7] Configuring MQTT broker...${NC}"
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

# Allow MQTT port through firewall (if ufw is installed)
if command -v ufw &> /dev/null; then
    sudo ufw allow 1883
fi

# Make scripts executable
echo -e "${GREEN}[7/7] Making scripts executable...${NC}"
chmod +x main.py
chmod +x Network/MQTT/mqtt_device_controller_integrated.py

echo ""
echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Reboot your Raspberry Pi: sudo reboot"
echo "2. Connect your hardware according to config/hardware/gpio_config.yaml"
echo "3. Run the system: python3 main.py"
echo ""
echo "For more information, see README.md"
echo ""
