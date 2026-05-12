#!/bin/bash
# Post-deployment script
# Add any custom commands to run after deployment

echo "Running post-deployment tasks..."

# Example: Set permissions
# chmod +x /home/pi/surveillance-car/main.py

# Example: Clear cache
# rm -rf /home/pi/surveillance-car/__pycache__

# Example: Run database migrations
# python3 /home/pi/surveillance-car/migrate.py

# Example: Restart additional services
# sudo systemctl restart mosquitto

echo "Post-deployment tasks completed!"
