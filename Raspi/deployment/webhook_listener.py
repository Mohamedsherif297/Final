#!/usr/bin/env python3
"""
GitHub/GitLab Webhook Listener for Raspberry Pi
Listens for push events and triggers automatic deployment
"""

from flask import Flask, request, jsonify
import hmac
import hashlib
import subprocess
import logging
from pathlib import Path
import os

# Configuration
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "your-secret-key-here")
DEPLOY_SCRIPT = Path.home() / "surveillance-car" / "Raspi" / "deployment" / "git_auto_deploy.py"
LOG_FILE = Path.home() / "surveillance-car" / "Raspi" / "logs" / "webhook.log"
PORT = 8080

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

app = Flask(__name__)


def verify_github_signature(payload_body, signature_header):
    """Verify GitHub webhook signature"""
    if not signature_header:
        return False
    
    hash_algorithm, github_signature = signature_header.split('=')
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(WEBHOOK_SECRET, 'latin-1')
    mac = hmac.new(encoded_key, msg=payload_body, digestmod=algorithm)
    
    return hmac.compare_digest(mac.hexdigest(), github_signature)


def verify_gitlab_token(token_header):
    """Verify GitLab webhook token"""
    return token_header == WEBHOOK_SECRET


def trigger_deployment():
    """Trigger the deployment script"""
    try:
        logger.info("Triggering deployment...")
        result = subprocess.run(
            ["python3", str(DEPLOY_SCRIPT)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            logger.info("Deployment completed successfully")
            return True, result.stdout
        else:
            logger.error(f"Deployment failed: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        logger.error("Deployment timed out")
        return False, "Deployment timed out after 5 minutes"
    except Exception as e:
        logger.error(f"Deployment error: {e}")
        return False, str(e)


@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    """Handle GitHub webhook"""
    
    # Verify signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_github_signature(request.data, signature):
        logger.warning("Invalid GitHub signature")
        return jsonify({"error": "Invalid signature"}), 401
    
    # Parse payload
    payload = request.json
    
    # Check if it's a push event
    event_type = request.headers.get('X-GitHub-Event')
    if event_type != 'push':
        logger.info(f"Ignoring {event_type} event")
        return jsonify({"message": f"Ignoring {event_type} event"}), 200
    
    # Get branch info
    ref = payload.get('ref', '')
    branch = ref.split('/')[-1] if '/' in ref else ref
    
    logger.info(f"Received push event for branch: {branch}")
    logger.info(f"Commits: {len(payload.get('commits', []))}")
    
    # Trigger deployment
    success, output = trigger_deployment()
    
    if success:
        return jsonify({
            "message": "Deployment triggered successfully",
            "branch": branch,
            "output": output
        }), 200
    else:
        return jsonify({
            "error": "Deployment failed",
            "output": output
        }), 500


@app.route('/webhook/gitlab', methods=['POST'])
def gitlab_webhook():
    """Handle GitLab webhook"""
    
    # Verify token
    token = request.headers.get('X-Gitlab-Token')
    if not verify_gitlab_token(token):
        logger.warning("Invalid GitLab token")
        return jsonify({"error": "Invalid token"}), 401
    
    # Parse payload
    payload = request.json
    
    # Check if it's a push event
    event_type = payload.get('object_kind')
    if event_type != 'push':
        logger.info(f"Ignoring {event_type} event")
        return jsonify({"message": f"Ignoring {event_type} event"}), 200
    
    # Get branch info
    ref = payload.get('ref', '')
    branch = ref.split('/')[-1] if '/' in ref else ref
    
    logger.info(f"Received push event for branch: {branch}")
    logger.info(f"Commits: {payload.get('total_commits_count', 0)}")
    
    # Trigger deployment
    success, output = trigger_deployment()
    
    if success:
        return jsonify({
            "message": "Deployment triggered successfully",
            "branch": branch,
            "output": output
        }), 200
    else:
        return jsonify({
            "error": "Deployment failed",
            "output": output
        }), 500


@app.route('/webhook/manual', methods=['POST'])
def manual_webhook():
    """Manual deployment trigger (no authentication required for local use)"""
    
    # Only allow from localhost for security
    if request.remote_addr not in ['127.0.0.1', 'localhost', '::1']:
        logger.warning(f"Manual trigger attempted from {request.remote_addr}")
        return jsonify({"error": "Only localhost allowed"}), 403
    
    logger.info("Manual deployment triggered")
    
    success, output = trigger_deployment()
    
    if success:
        return jsonify({
            "message": "Deployment completed successfully",
            "output": output
        }), 200
    else:
        return jsonify({
            "error": "Deployment failed",
            "output": output
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "git-webhook-listener"
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        "service": "Git Webhook Listener",
        "endpoints": {
            "github": "/webhook/github",
            "gitlab": "/webhook/gitlab",
            "manual": "/webhook/manual (localhost only)",
            "health": "/health"
        }
    }), 200


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Starting Git Webhook Listener")
    logger.info(f"Port: {PORT}")
    logger.info(f"Deploy script: {DEPLOY_SCRIPT}")
    logger.info("=" * 60)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=PORT, debug=False)
