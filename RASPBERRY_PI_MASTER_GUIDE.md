# 🍓 Raspberry Pi Master Guide

**Your complete reference for working with Raspberry Pi in any project**

---

## 📋 Table of Contents

1. [Initial Setup & Configuration](#initial-setup--configuration)
2. [SSH & Remote Access](#ssh--remote-access)
3. [File Transfer Methods](#file-transfer-methods)
4. [Git Workflow (Best Practice)](#git-workflow-best-practice)
5. [Python & Package Management](#python--package-management)
6. [When to Use sudo](#when-to-use-sudo)
7. [GPIO & Hardware Access](#gpio--hardware-access)
8. [Network Configuration](#network-configuration)
9. [System Monitoring & Debugging](#system-monitoring--debugging)
10. [Common Issues & Solutions](#common-issues--solutions)
11. [Essential Commands Cheat Sheet](#essential-commands-cheat-sheet)

---

## 1. Initial Setup & Configuration

### First Boot Setup

```bash
# Update system (ALWAYS do this first!)
sudo apt-get update
sudo apt-get upgrade -y

# Install essential tools
sudo apt-get install -y git vim nano htop curl wget

# Set timezone
sudo raspi-config
# Navigate to: Localisation Options → Timezone

# Enable interfaces (I2C, SPI, Camera, etc.)
sudo raspi-config
# Navigate to: Interface Options → Enable what you need
```

### Configure Hostname (Optional but Recommended)

```bash
# Change hostname from 'raspberrypi' to something unique
sudo raspi-config
# Navigate to: System Options → Hostname
# Example: surveillance-car, robot-pi, sensor-hub

# Or edit directly:
sudo nano /etc/hostname
sudo nano /etc/hosts  # Change 127.0.1.1 line too
sudo reboot
```

### Set Static IP (Recommended for Projects)

```bash
# Edit dhcpcd.conf
sudo nano /etc/dhcpcd.conf

# Add at the end:
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8

# Save and reboot
sudo reboot
```

---

## 2. SSH & Remote Access

### Enable SSH

```bash
# Method 1: Using raspi-config
sudo raspi-config
# Navigate to: Interface Options → SSH → Enable

# Method 2: Create empty file (headless setup)
sudo touch /boot/ssh
```

### Connect from Your Computer

```bash
# Basic connection
ssh pi@raspberrypi.local
# Or with IP
ssh pi@192.168.1.100

# Default password: raspberry (CHANGE THIS!)
```

### Change Default Password (IMPORTANT!)

```bash
passwd
# Enter current password: raspberry
# Enter new password twice
```

### Setup SSH Keys (No Password Login)

**On your computer:**
```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy key to Pi
ssh-copy-id pi@raspberrypi.local

# Now you can login without password!
ssh pi@raspberrypi.local
```

### Keep SSH Session Alive

```bash
# On your computer, edit SSH config
nano ~/.ssh/config

# Add:
Host raspberrypi.local
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

---

## 3. File Transfer Methods

### Method 1: SCP (Simple File Copy)

```bash
# Copy file TO Pi
scp file.txt pi@raspberrypi.local:~/

# Copy file FROM Pi
scp pi@raspberrypi.local:~/file.txt ./

# Copy entire folder TO Pi
scp -r my_folder/ pi@raspberrypi.local:~/

# Copy entire folder FROM Pi
scp -r pi@raspberrypi.local:~/my_folder ./
```

### Method 2: SFTP (Interactive)

```bash
# Connect
sftp pi@raspberrypi.local

# Commands:
put file.txt          # Upload file
get file.txt          # Download file
put -r folder/        # Upload folder
get -r folder/        # Download folder
ls                    # List remote files
lls                   # List local files
cd /path              # Change remote directory
lcd /path             # Change local directory
exit                  # Quit
```

### Method 3: Git (BEST for Projects!)

**See section 4 below** ⬇️

---

## 4. Git Workflow (Best Practice)

### Initial Setup on Pi

```bash
# Install git
sudo apt-get install git -y

# Configure git
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"

# Generate SSH key for GitHub
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub
# Copy this key and add to GitHub: Settings → SSH Keys
```

### Clone Repository

```bash
# Clone your project
cd ~
git clone git@github.com:username/repository.git
cd repository
```

### Typical Workflow

**On your computer (development):**
```bash
# Make changes
nano file.py

# Commit and push
git add .
git commit -m "Updated motor control"
git push origin main
```

**On Raspberry Pi (deployment):**
```bash
# Pull latest changes
cd ~/your-project
git pull origin main

# Run updated code
sudo python3 main.py
```

### Auto-Deploy Setup (Advanced)

```bash
# Create a script to pull and restart
nano ~/update.sh

#!/bin/bash
cd ~/your-project
git pull origin main
sudo systemctl restart your-service

# Make executable
chmod +x ~/update.sh

# Run whenever you want to update
./update.sh
```

### Handling Conflicts

```bash
# If you have local changes that conflict
git stash              # Save local changes
git pull origin main   # Pull updates
git stash pop          # Restore local changes

# Or discard local changes
git reset --hard origin/main
```

---

## 5. Python & Package Management

### Python Versions

```bash
# Check Python version
python3 --version

# Raspberry Pi OS uses Python 3.11+ (externally managed)
```

### Installing Packages

```bash
# Standard method (will fail on newer Pi OS)
pip3 install package_name
# Error: "externally-managed-environment"

# CORRECT method for Raspberry Pi OS
pip3 install package_name --break-system-packages

# Or use virtual environment (recommended for complex projects)
python3 -m venv myenv
source myenv/bin/activate
pip install package_name
```

### Requirements File

```bash
# Create requirements.txt
pip3 freeze > requirements.txt

# Install from requirements.txt
pip3 install -r requirements.txt --break-system-packages
```

### System Packages (apt)

```bash
# Some packages need system libraries first
sudo apt-get install python3-opencv
sudo apt-get install python3-numpy
sudo apt-get install python3-pil

# Then install Python packages
pip3 install opencv-python --break-system-packages
```

---

## 6. When to Use sudo

### ✅ ALWAYS Use sudo For:

**1. GPIO Access:**
```bash
sudo python3 motor_control.py
```

**2. System Configuration:**
```bash
sudo raspi-config
sudo nano /etc/dhcpcd.conf
sudo systemctl start myservice
```

**3. Installing System Packages:**
```bash
sudo apt-get install package
```

**4. Hardware Access:**
```bash
sudo python3 camera_test.py  # If using camera
sudo python3 i2c_test.py     # If using I2C
```

**5. Port < 1024:**
```bash
sudo python3 webserver.py  # If using port 80 or 443
```

### ❌ DON'T Use sudo For:

**1. Regular Python Scripts (no hardware):**
```bash
python3 calculator.py  # No sudo needed
```

**2. Git Operations:**
```bash
git pull origin main  # No sudo!
git commit -m "update"
```

**3. Installing Python Packages:**
```bash
pip3 install requests --break-system-packages  # No sudo!
```

**4. Editing Your Own Files:**
```bash
nano ~/my_script.py  # No sudo needed
```

### 🤔 How to Know?

**Rule of thumb:**
- Accessing hardware (GPIO, I2C, SPI, Camera) → **Use sudo**
- System files in `/etc/`, `/boot/`, `/sys/` → **Use sudo**
- Your own files in `/home/pi/` → **No sudo**
- Installing with `apt-get` → **Use sudo**
- Installing with `pip3` → **No sudo**

---

## 7. GPIO & Hardware Access

### GPIO Pin Numbering

```python
import RPi.GPIO as GPIO

# Two numbering systems:
GPIO.setmode(GPIO.BCM)   # Use GPIO numbers (recommended)
GPIO.setmode(GPIO.BOARD) # Use physical pin numbers
```

**BCM vs BOARD:**
- **BCM**: GPIO 17, GPIO 18, GPIO 27 (chip numbering)
- **BOARD**: Pin 11, Pin 12, Pin 13 (physical position)
- **Use BCM** - it's more standard

### Check GPIO Status

```bash
# Install gpio tool
sudo apt-get install wiringpi

# Show all GPIO pins
gpio readall

# Or use Python
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); print('GPIO OK')"
```

### I2C Setup

```bash
# Enable I2C
sudo raspi-config
# Interface Options → I2C → Enable

# Install tools
sudo apt-get install i2c-tools

# Scan I2C bus
sudo i2cdetect -y 1

# Test in Python
python3 -c "import smbus; bus = smbus.SMBus(1); print('I2C OK')"
```

### Camera Setup

```bash
# Enable camera
sudo raspi-config
# Interface Options → Camera → Enable

# Test camera
vcgencmd get_camera
# Should show: supported=1 detected=1

# Test with Python
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera FAIL')"
```

---

## 8. Network Configuration

### Find Your IP Address

```bash
# Show all network info
ifconfig

# Just show IP
hostname -I

# Or
ip addr show wlan0
```

### WiFi Configuration

```bash
# Edit WiFi config
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf

# Add network:
network={
    ssid="YourWiFiName"
    psk="YourPassword"
    key_mgmt=WPA-PSK
}

# Restart WiFi
sudo systemctl restart dhcpcd
```

### Check Network Speed

```bash
# Install speedtest
sudo apt-get install speedtest-cli

# Run test
speedtest-cli
```

### Port Forwarding (Access from Internet)

**On your router:**
1. Find Pi's IP: `hostname -I`
2. Login to router (usually 192.168.1.1)
3. Find "Port Forwarding" or "Virtual Server"
4. Forward external port → Pi IP:internal port
5. Example: External 8080 → 192.168.1.100:8765

---

## 9. System Monitoring & Debugging

### Check System Resources

```bash
# CPU, Memory, Processes
htop

# Or simpler
top

# Disk usage
df -h

# Memory usage
free -h

# Temperature
vcgencmd measure_temp

# CPU frequency
vcgencmd measure_clock arm
```

### Monitor Logs

```bash
# System log
sudo tail -f /var/log/syslog

# Kernel messages
dmesg | tail

# Service logs
sudo journalctl -u your-service -f
```

### Check Running Processes

```bash
# Find Python processes
ps aux | grep python

# Kill a process
kill PID
# Or force kill
kill -9 PID

# Kill by name
pkill -f "python3 main.py"
```

### Network Debugging

```bash
# Check if port is open
sudo netstat -tulpn | grep 8765

# Test connection
ping google.com

# Check DNS
nslookup google.com

# Trace route
traceroute google.com
```

---

## 10. Common Issues & Solutions

### Issue: "Permission denied" when accessing GPIO

**Solution:**
```bash
# Use sudo
sudo python3 your_script.py

# Or add user to gpio group
sudo usermod -a -G gpio pi
# Logout and login again
```

### Issue: "externally-managed-environment" when using pip

**Solution:**
```bash
# Use --break-system-packages flag
pip3 install package --break-system-packages

# Or use virtual environment
python3 -m venv myenv
source myenv/bin/activate
pip install package
```

### Issue: Camera not detected

**Solution:**
```bash
# Enable camera
sudo raspi-config
# Interface Options → Camera → Enable

# Check camera
vcgencmd get_camera

# Check cable connection
# Reboot
sudo reboot
```

### Issue: I2C device not found

**Solution:**
```bash
# Enable I2C
sudo raspi-config

# Install tools
sudo apt-get install i2c-tools

# Scan bus
sudo i2cdetect -y 1

# Check wiring (SDA, SCL, VCC, GND)
```

### Issue: WiFi keeps disconnecting

**Solution:**
```bash
# Disable power management
sudo nano /etc/rc.local

# Add before 'exit 0':
/sbin/iwconfig wlan0 power off

# Or edit NetworkManager
sudo nano /etc/NetworkManager/conf.d/default-wifi-powersave-on.conf

# Change to:
wifi.powersave = 2
```

### Issue: SD card full

**Solution:**
```bash
# Check disk usage
df -h

# Find large files
sudo du -h / | sort -rh | head -20

# Clean apt cache
sudo apt-get clean

# Remove old logs
sudo journalctl --vacuum-time=7d
```

### Issue: Pi running slow/hot

**Solution:**
```bash
# Check temperature
vcgencmd measure_temp

# Check CPU usage
htop

# Add heatsink or fan
# Reduce overclock if enabled
# Check for runaway processes
```

---

## 11. Essential Commands Cheat Sheet

### File Operations
```bash
ls -la              # List files (detailed)
cd /path            # Change directory
pwd                 # Show current directory
cp file1 file2      # Copy file
mv file1 file2      # Move/rename file
rm file             # Delete file
rm -rf folder/      # Delete folder
mkdir folder        # Create folder
nano file.txt       # Edit file
cat file.txt        # View file
```

### System
```bash
sudo reboot         # Restart Pi
sudo shutdown -h now # Shutdown Pi
sudo raspi-config   # Configuration tool
vcgencmd measure_temp # Check temperature
hostname -I         # Show IP address
ifconfig            # Network info
```

### Processes
```bash
ps aux              # List all processes
ps aux | grep python # Find Python processes
kill PID            # Kill process
pkill -f "name"     # Kill by name
htop                # Interactive process viewer
```

### Packages
```bash
sudo apt-get update # Update package list
sudo apt-get upgrade # Upgrade packages
sudo apt-get install pkg # Install package
sudo apt-get remove pkg # Remove package
pip3 install pkg --break-system-packages # Install Python package
```

### Git
```bash
git clone URL       # Clone repository
git pull            # Pull updates
git add .           # Stage changes
git commit -m "msg" # Commit changes
git push            # Push to remote
git status          # Check status
git log             # View history
```

### Network
```bash
ping google.com     # Test connection
ifconfig            # Network interfaces
hostname -I         # Show IP
sudo systemctl restart dhcpcd # Restart network
```

### GPIO
```bash
gpio readall        # Show GPIO status
sudo i2cdetect -y 1 # Scan I2C bus
vcgencmd get_camera # Check camera
```

---

## 🎯 Quick Start Template for New Projects

```bash
# 1. Setup Pi
sudo apt-get update && sudo apt-get upgrade -y
sudo raspi-config  # Enable interfaces you need

# 2. Setup Git
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
ssh-keygen -t ed25519 -C "your@email.com"
cat ~/.ssh/id_ed25519.pub  # Add to GitHub

# 3. Clone project
cd ~
git clone git@github.com:username/project.git
cd project

# 4. Install dependencies
pip3 install -r requirements.txt --break-system-packages

# 5. Test
sudo python3 main.py

# 6. Update workflow
# On computer: git push
# On Pi: git pull && sudo python3 main.py
```

---

## 📚 Additional Resources

**Official Documentation:**
- https://www.raspberrypi.com/documentation/

**GPIO Pinout:**
- https://pinout.xyz/

**Python GPIO Library:**
- https://sourceforge.net/p/raspberry-gpio-python/wiki/Home/

**Community:**
- https://forums.raspberrypi.com/

---

## 💡 Pro Tips

1. **Always use Git** for project management - it's the cleanest way
2. **Use SSH keys** - no more typing passwords
3. **Set static IP** - easier to find your Pi
4. **Monitor temperature** - add cooling if needed
5. **Backup SD card** - use `dd` or Win32DiskImager
6. **Use screen/tmux** - keep processes running after disconnect
7. **Document your wiring** - take photos of GPIO connections
8. **Test incrementally** - don't build everything at once
9. **Use virtual environments** - for complex Python projects
10. **Keep it updated** - `sudo apt-get update && upgrade` regularly

---

**This guide covers 90% of what you'll need for any Raspberry Pi project!** 🚀

Bookmark this file and refer to it whenever you start a new project.
