#!/usr/bin/env python3
"""
Test I2C connection for PCA9685
"""
import subprocess

print("=" * 50)
print("I2C Device Detection")
print("=" * 50)

print("\nChecking I2C devices...")
result = subprocess.run(['i2cdetect', '-y', '1'], capture_output=True, text=True)
print(result.stdout)

print("\nLooking for PCA9685 at address 0x40...")
if '40' in result.stdout:
    print("✓ PCA9685 found at 0x40!")
else:
    print("✗ PCA9685 NOT found")
    print("\nTroubleshooting:")
    print("1. Check wiring: SDA→GPIO2, SCL→GPIO3")
    print("2. Enable I2C: sudo raspi-config → Interface → I2C → Enable")
    print("3. Reboot after enabling I2C")
