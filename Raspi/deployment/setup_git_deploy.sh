#!/bin/bash
# Setup script for Git auto-deployment on Raspberry Pi

set -e  # Exit on error

echo "============================================================"
echo "Git Auto-Deploy Setup for Surveillance Car"
echo "============================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$HOME/surveillance-car"
DEPLOYMENT_DIR="$PROJECT_DIR/Raspi/deployment"

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo -e "${YELLOW}Warning: This doesn't appear to be a Raspberry Pi${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}Error: Project directory not found: $PROJECT_DIR${NC}"
    exit 1
fi

cd "$PROJECT_DIR"

# Check if it's a Git repository
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}Not a Git repository. Initializing...${NC}"
    read -p "Enter Git repository URL: " REPO_URL
    
    if [ -z "$REPO_URL" ]; then
        echo -e "${RED}Error: Repository URL required${NC}"
        exit 1
    fi
    
    git init
    git remote add origin "$REPO_URL"
    git fetch origin
    git checkout -b main origin/main || git checkout -b master origin/master
    
    echo -e "${GREEN}Git repository initialized${NC}"
fi

# Install required Python packages
echo ""
echo "Installing Python dependencies..."
pip3 install flask paho-mqtt --user

# Make scripts executable
echo ""
echo "Setting permissions..."
chmod +x "$DEPLOYMENT_DIR/git_auto_deploy.py"
chmod +x "$DEPLOYMENT_DIR/webhook_listener.py"
chmod +x "$DEPLOYMENT_DIR/post_deploy.sh"

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

echo ""
echo "============================================================"
echo "Choose deployment method:"
echo "============================================================"
echo "1. Periodic auto-pull (checks every 5 minutes)"
echo "2. Webhook listener (GitHub/GitLab push events)"
echo "3. Both (recommended)"
echo "4. Manual only (no automation)"
echo ""
read -p "Enter choice (1-4): " DEPLOY_METHOD

case $DEPLOY_METHOD in
    1|3)
        echo ""
        echo "Setting up periodic auto-pull service..."
        
        # Copy systemd service file
        sudo cp "$DEPLOYMENT_DIR/git-deploy.service" /etc/systemd/system/
        
        # Reload systemd
        sudo systemctl daemon-reload
        
        # Enable and start service
        sudo systemctl enable git-deploy.service
        sudo systemctl start git-deploy.service
        
        echo -e "${GREEN}✓ Periodic auto-pull service installed${NC}"
        echo "  Status: sudo systemctl status git-deploy"
        echo "  Logs: journalctl -u git-deploy -f"
        ;;
esac

case $DEPLOY_METHOD in
    2|3)
        echo ""
        echo "Setting up webhook listener..."
        
        # Get webhook secret
        read -p "Enter webhook secret (or press Enter for default): " WEBHOOK_SECRET
        if [ -z "$WEBHOOK_SECRET" ]; then
            WEBHOOK_SECRET="your-secret-key-here"
        fi
        
        # Update service file with secret
        sudo sed -i "s/your-secret-key-here/$WEBHOOK_SECRET/" "$DEPLOYMENT_DIR/webhook-listener.service"
        
        # Copy systemd service file
        sudo cp "$DEPLOYMENT_DIR/webhook-listener.service" /etc/systemd/system/
        
        # Reload systemd
        sudo systemctl daemon-reload
        
        # Enable and start service
        sudo systemctl enable webhook-listener.service
        sudo systemctl start webhook-listener.service
        
        # Get Raspberry Pi IP
        PI_IP=$(hostname -I | awk '{print $1}')
        
        echo -e "${GREEN}✓ Webhook listener installed${NC}"
        echo "  Status: sudo systemctl status webhook-listener"
        echo "  Logs: journalctl -u webhook-listener -f"
        echo ""
        echo "Configure your Git provider webhook:"
        echo "  URL: http://$PI_IP:8080/webhook/github (for GitHub)"
        echo "  URL: http://$PI_IP:8080/webhook/gitlab (for GitLab)"
        echo "  Secret: $WEBHOOK_SECRET"
        echo "  Content type: application/json"
        echo "  Events: Just the push event"
        ;;
esac

# Setup cron job as alternative
if [ "$DEPLOY_METHOD" == "4" ]; then
    echo ""
    read -p "Setup cron job for periodic checks? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Add cron job (every 5 minutes)
        (crontab -l 2>/dev/null; echo "*/5 * * * * cd $PROJECT_DIR && python3 $DEPLOYMENT_DIR/git_auto_deploy.py >> $PROJECT_DIR/logs/git_deploy.log 2>&1") | crontab -
        echo -e "${GREEN}✓ Cron job installed (runs every 5 minutes)${NC}"
        echo "  View: crontab -l"
        echo "  Logs: $PROJECT_DIR/logs/git_deploy.log"
    fi
fi

# Test deployment
echo ""
echo "============================================================"
read -p "Test deployment now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Running test deployment..."
    python3 "$DEPLOYMENT_DIR/git_auto_deploy.py"
fi

echo ""
echo "============================================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "============================================================"
echo ""
echo "Your Raspberry Pi will now automatically deploy changes when you:"
echo "  • Push to your Git repository"
echo ""
echo "Manual deployment:"
echo "  python3 $DEPLOYMENT_DIR/git_auto_deploy.py"
echo ""
echo "Check status:"
if [ "$DEPLOY_METHOD" == "1" ] || [ "$DEPLOY_METHOD" == "3" ]; then
    echo "  sudo systemctl status git-deploy"
fi
if [ "$DEPLOY_METHOD" == "2" ] || [ "$DEPLOY_METHOD" == "3" ]; then
    echo "  sudo systemctl status webhook-listener"
fi
echo ""
echo "View logs:"
echo "  tail -f $PROJECT_DIR/logs/git_deploy.log"
if [ "$DEPLOY_METHOD" == "2" ] || [ "$DEPLOY_METHOD" == "3" ]; then
    echo "  tail -f $PROJECT_DIR/logs/webhook.log"
fi
echo ""
echo "============================================================"
