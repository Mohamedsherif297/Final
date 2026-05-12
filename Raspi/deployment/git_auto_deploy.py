#!/usr/bin/env python3
"""
Git Auto-Deploy Service for Raspberry Pi
Automatically pulls changes from Git repository and restarts services
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime
import json
import time

# Configuration
PROJECT_DIR = Path.home() / "surveillance-car"
GIT_BRANCH = "main"  # Change to your branch name
LOG_FILE = PROJECT_DIR / "logs" / "git_deploy.log"
SERVICE_NAME = "surveillance-car"  # Systemd service name if you create one

# Setup logging
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GitAutoDeployer:
    """Handles automatic Git pull and service restart"""
    
    def __init__(self, project_dir: Path, branch: str = "main"):
        self.project_dir = project_dir
        self.branch = branch
        self.last_commit = None
        
    def check_git_repo(self) -> bool:
        """Verify this is a valid Git repository"""
        git_dir = self.project_dir / ".git"
        if not git_dir.exists():
            logger.error(f"Not a Git repository: {self.project_dir}")
            return False
        return True
    
    def get_current_commit(self) -> str:
        """Get current commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get current commit: {e}")
            return ""
    
    def fetch_updates(self) -> bool:
        """Fetch updates from remote"""
        try:
            logger.info("Fetching updates from remote...")
            subprocess.run(
                ["git", "fetch", "origin", self.branch],
                cwd=self.project_dir,
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to fetch updates: {e}")
            return False
    
    def check_for_updates(self) -> bool:
        """Check if there are new commits to pull"""
        try:
            local_commit = subprocess.run(
                ["git", "rev-parse", self.branch],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()
            
            remote_commit = subprocess.run(
                ["git", "rev-parse", f"origin/{self.branch}"],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()
            
            if local_commit != remote_commit:
                logger.info(f"Updates available: {local_commit[:7]} -> {remote_commit[:7]}")
                return True
            else:
                logger.info("Already up to date")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to check for updates: {e}")
            return False
    
    def pull_changes(self) -> bool:
        """Pull changes from remote repository"""
        try:
            logger.info(f"Pulling changes from origin/{self.branch}...")
            
            # Stash any local changes
            subprocess.run(
                ["git", "stash"],
                cwd=self.project_dir,
                capture_output=True
            )
            
            # Pull changes
            result = subprocess.run(
                ["git", "pull", "origin", self.branch],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("Successfully pulled changes")
            logger.info(result.stdout)
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to pull changes: {e}")
            logger.error(e.stderr)
            return False
    
    def install_dependencies(self) -> bool:
        """Install/update Python dependencies"""
        requirements_file = self.project_dir / "requirements.txt"
        
        if not requirements_file.exists():
            logger.info("No requirements.txt found, skipping dependency installation")
            return True
        
        try:
            logger.info("Installing/updating dependencies...")
            subprocess.run(
                ["pip3", "install", "-r", str(requirements_file)],
                cwd=self.project_dir,
                check=True,
                capture_output=True
            )
            logger.info("Dependencies updated successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
    
    def restart_service(self) -> bool:
        """Restart the surveillance car service"""
        try:
            logger.info(f"Restarting {SERVICE_NAME} service...")
            
            # Check if systemd service exists
            check_service = subprocess.run(
                ["systemctl", "is-active", SERVICE_NAME],
                capture_output=True
            )
            
            if check_service.returncode == 0:
                # Service exists and is running, restart it
                subprocess.run(
                    ["sudo", "systemctl", "restart", SERVICE_NAME],
                    check=True
                )
                logger.info(f"Service {SERVICE_NAME} restarted successfully")
            else:
                logger.info(f"Service {SERVICE_NAME} not running, skipping restart")
                logger.info("You may need to manually start the application")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to restart service: {e}")
            return False
    
    def run_post_deploy_script(self) -> bool:
        """Run custom post-deployment script if it exists"""
        post_deploy_script = self.project_dir / "deployment" / "post_deploy.sh"
        
        if not post_deploy_script.exists():
            logger.info("No post-deployment script found")
            return True
        
        try:
            logger.info("Running post-deployment script...")
            subprocess.run(
                ["bash", str(post_deploy_script)],
                cwd=self.project_dir,
                check=True
            )
            logger.info("Post-deployment script completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Post-deployment script failed: {e}")
            return False
    
    def deploy(self) -> bool:
        """Execute full deployment process"""
        logger.info("=" * 60)
        logger.info("Starting deployment process")
        logger.info("=" * 60)
        
        if not self.check_git_repo():
            return False
        
        # Store current commit
        old_commit = self.get_current_commit()
        
        # Fetch and check for updates
        if not self.fetch_updates():
            return False
        
        if not self.check_for_updates():
            logger.info("No updates to deploy")
            return True
        
        # Pull changes
        if not self.pull_changes():
            return False
        
        # Get new commit
        new_commit = self.get_current_commit()
        logger.info(f"Deployed: {old_commit[:7]} -> {new_commit[:7]}")
        
        # Install dependencies
        if not self.install_dependencies():
            logger.warning("Dependency installation failed, continuing anyway...")
        
        # Run post-deploy script
        if not self.run_post_deploy_script():
            logger.warning("Post-deploy script failed, continuing anyway...")
        
        # Restart service
        if not self.restart_service():
            logger.warning("Service restart failed, you may need to restart manually")
        
        logger.info("=" * 60)
        logger.info("Deployment completed successfully!")
        logger.info("=" * 60)
        
        return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Git Auto-Deploy for Raspberry Pi")
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=PROJECT_DIR,
        help="Project directory path"
    )
    parser.add_argument(
        "--branch",
        type=str,
        default=GIT_BRANCH,
        help="Git branch to track"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch for changes continuously"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Check interval in seconds (for watch mode)"
    )
    
    args = parser.parse_args()
    
    deployer = GitAutoDeployer(args.project_dir, args.branch)
    
    if args.watch:
        logger.info(f"Starting watch mode (checking every {args.interval} seconds)")
        logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                deployer.deploy()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("Watch mode stopped")
    else:
        # Single deployment run
        success = deployer.deploy()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
