#!/bin/bash

# ============================================================
# Raspberry Pi Cleanup Script
# Removes unnecessary files to save space on Pi
# ============================================================

echo "============================================================"
echo "Raspberry Pi Space Cleanup"
echo "============================================================"
echo ""
echo "This will remove files NOT needed on Raspberry Pi:"
echo "  ❌ Documentation files"
echo "  ❌ Laptop controller"
echo "  ❌ ESP32 files"
echo "  ❌ Old/backup files"
echo "  ❌ Development files"
echo ""
echo "Will KEEP:"
echo "  ✅ last_try/ (main application)"
echo "  ✅ .git/ (for updates)"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 1
fi

# ============================================================
# Calculate space before cleanup
# ============================================================
echo ""
echo "Calculating current space usage..."
BEFORE=$(du -sh . | cut -f1)
echo "Current size: $BEFORE"

# ============================================================
# Remove documentation files
# ============================================================
echo ""
echo "Removing documentation files..."
rm -f ALL_FIXES_SUMMARY.md
rm -f CTRL_C_FIX.md
rm -f DASHBOARD_DISCOVERY.md
rm -f ESP32_IMPLEMENTATION_OVERVIEW.md
rm -f ESP32_README.md
rm -f FIXES_APPLIED.md
rm -f GIT_DEPLOYMENT_SUMMARY.md
rm -f PROJECT_STATUS.md
rm -f QUICK_FIX_SUMMARY.md
rm -f RASPBERRY_PI_MASTER_GUIDE.md
rm -f SUGGESTIONS_AND_NEXT_STEPS.md
rm -f TESTING_GUIDE.md
rm -f presentation.html
rm -f project_analysis.html
rm -f ToDO
echo "✅ Documentation removed"

# ============================================================
# Remove Docs folder
# ============================================================
echo ""
echo "Removing Docs/ folder..."
rm -rf Docs/
echo "✅ Docs/ removed"

# ============================================================
# Remove Laptop controller
# ============================================================
echo ""
echo "Removing Laptop/ controller..."
rm -rf Laptop/
echo "✅ Laptop/ removed"

# ============================================================
# Remove Dashboard (only needed on laptop)
# ============================================================
echo ""
echo "Removing Dashboard/ (only needed on laptop)..."
rm -rf Dashboard/
echo "✅ Dashboard/ removed"

# ============================================================
# Remove ESP32 files
# ============================================================
echo ""
echo "Removing ESP32/ files..."
rm -rf ESP32/
echo "✅ ESP32/ removed"

# ============================================================
# Remove old/backup files
# ============================================================
echo ""
echo "Removing old/backup files..."
rm -rf last_try/
rm -f *.zip
rm -f *.tar.gz
rm -f transfer_test_to_pi.sh
echo "✅ Old files removed"

# ============================================================
# Remove system files
# ============================================================
echo ""
echo "Removing system files..."
find . -name ".DS_Store" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
echo "✅ System files removed"

# ============================================================
# Remove test files
# ============================================================
echo ""
echo "Removing test files..."
rm -rf Raspi/tests/
echo "✅ Test files removed"

# ============================================================
# Remove Raspi folder (not used, using last_try instead)
# ============================================================
echo ""
echo "Removing Raspi/ folder (using last_try/ instead)..."
rm -rf Raspi/
echo "✅ Raspi/ removed"

# ============================================================
# Clean last_try documentation (keep only code)
# ============================================================
echo ""
echo "Cleaning last_try/ documentation..."
if [ -d "last_try" ]; then
    cd last_try
    # Remove markdown documentation files
    rm -f *.md 2>/dev/null
    rm -f *.txt 2>/dev/null
    rm -f *.sh 2>/dev/null
    # Keep only Python files and hardware folder
    cd ..
fi
echo "✅ last_try/ docs cleaned"

# ============================================================
# Clean logs
# ============================================================
echo ""
echo "Cleaning logs..."
if [ -d "last_try/logs" ]; then
    rm -f last_try/logs/*.log
    rm -f last_try/logs/*.txt
fi
echo "✅ Logs cleaned"

# ============================================================
# Remove .vscode
# ============================================================
echo ""
echo "Removing .vscode/..."
rm -rf .vscode/
echo "✅ .vscode/ removed"

# ============================================================
# Remove .kiro (if exists)
# ============================================================
echo ""
echo "Removing .kiro/..."
rm -rf .kiro/
echo "✅ .kiro/ removed"

# ============================================================
# Calculate space after cleanup
# ============================================================
echo ""
echo "============================================================"
echo "Cleanup Complete!"
echo "============================================================"
AFTER=$(du -sh . | cut -f1)
echo "Before: $BEFORE"
echo "After:  $AFTER"
echo ""
echo "Remaining structure:"
echo "  ✅ last_try/       - Main application"
echo "  ✅ .git/           - Git repository"
echo "  ✅ .gitignore      - Git ignore rules"
echo ""
echo "To update code from Git:"
echo "  git pull origin main"
echo ""
echo "To run the system:"
echo "  cd last_try"
echo "  sudo python3 run_all_integrated.py"
echo "============================================================"
