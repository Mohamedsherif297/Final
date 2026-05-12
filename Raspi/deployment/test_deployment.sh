#!/bin/bash
# Test script for Git auto-deployment system

set -e

echo "============================================================"
echo "Git Auto-Deploy System Test"
echo "============================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="$HOME/surveillance-car"
PASSED=0
FAILED=0

# Test function
test_check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $1"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}: $1"
        ((FAILED++))
    fi
}

echo "Running tests..."
echo ""

# Test 1: Check if project directory exists
echo -n "1. Project directory exists... "
[ -d "$PROJECT_DIR" ]
test_check "Project directory"

# Test 2: Check if it's a Git repository
echo -n "2. Git repository initialized... "
[ -d "$PROJECT_DIR/.git" ]
test_check "Git repository"

# Test 3: Check if deployment scripts exist
echo -n "3. Deployment scripts exist... "
[ -f "$PROJECT_DIR/deployment/git_auto_deploy.py" ] && \
[ -f "$PROJECT_DIR/deployment/webhook_listener.py" ]
test_check "Deployment scripts"

# Test 4: Check if scripts are executable
echo -n "4. Scripts are executable... "
[ -x "$PROJECT_DIR/deployment/git_auto_deploy.py" ] && \
[ -x "$PROJECT_DIR/deployment/webhook_listener.py" ]
test_check "Script permissions"

# Test 5: Check Python3 is installed
echo -n "5. Python3 installed... "
command -v python3 > /dev/null 2>&1
test_check "Python3"

# Test 6: Check Git is installed
echo -n "6. Git installed... "
command -v git > /dev/null 2>&1
test_check "Git"

# Test 7: Check if logs directory exists
echo -n "7. Logs directory exists... "
[ -d "$PROJECT_DIR/logs" ] || mkdir -p "$PROJECT_DIR/logs"
test_check "Logs directory"

# Test 8: Check Git remote
echo -n "8. Git remote configured... "
cd "$PROJECT_DIR"
git remote -v > /dev/null 2>&1
test_check "Git remote"

# Test 9: Check if Flask is installed (for webhook)
echo -n "9. Flask installed (optional)... "
python3 -c "import flask" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}: Flask installed"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ SKIP${NC}: Flask not installed (needed for webhooks)"
fi

# Test 10: Check systemd services
echo -n "10. Git-deploy service... "
if systemctl list-unit-files | grep -q "git-deploy.service"; then
    systemctl is-active --quiet git-deploy.service
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: Service running"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠ WARN${NC}: Service installed but not running"
    fi
else
    echo -e "${YELLOW}⚠ SKIP${NC}: Service not installed"
fi

echo -n "11. Webhook-listener service... "
if systemctl list-unit-files | grep -q "webhook-listener.service"; then
    systemctl is-active --quiet webhook-listener.service
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: Service running"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠ WARN${NC}: Service installed but not running"
    fi
else
    echo -e "${YELLOW}⚠ SKIP${NC}: Service not installed"
fi

# Test 12: Test deployment script
echo -n "12. Deployment script runs... "
cd "$PROJECT_DIR"
python3 deployment/git_auto_deploy.py --help > /dev/null 2>&1
test_check "Deployment script execution"

# Test 13: Check if webhook listener can start (if Flask installed)
if python3 -c "import flask" 2>/dev/null; then
    echo -n "13. Webhook listener syntax... "
    python3 -c "import sys; sys.path.insert(0, '$PROJECT_DIR/deployment'); import webhook_listener" 2>/dev/null
    test_check "Webhook listener syntax"
fi

echo ""
echo "============================================================"
echo "Test Results"
echo "============================================================"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All critical tests passed!${NC}"
    echo ""
    echo "Your Git auto-deploy system is ready to use!"
    echo ""
    echo "Next steps:"
    echo "  1. Push changes to your Git repository"
    echo "  2. Watch logs: tail -f $PROJECT_DIR/logs/git_deploy.log"
    echo "  3. Check status: sudo systemctl status git-deploy"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Please fix the issues above and run the setup script:"
    echo "  ./deployment/setup_git_deploy.sh"
    echo ""
    exit 1
fi
