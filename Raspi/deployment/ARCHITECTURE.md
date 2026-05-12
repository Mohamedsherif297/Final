# Git Auto-Deploy Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Your Development Computer                    │
│                                                                   │
│  ┌──────────────┐         ┌──────────────┐                      │
│  │  Edit Code   │────────►│  Git Commit  │                      │
│  └──────────────┘         └──────┬───────┘                      │
│                                   │                              │
│                                   ▼                              │
│                          ┌──────────────┐                        │
│                          │  Git Push    │                        │
│                          └──────┬───────┘                        │
└─────────────────────────────────┼─────────────────────────────────┘
                                  │
                                  │ Push to GitHub/GitLab
                                  │
                    ┌─────────────▼──────────────┐
                    │   GitHub / GitLab          │
                    │   (Remote Repository)      │
                    └─────────────┬──────────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
                │ Webhook         │                 │ Git Pull
                │ (instant)       │                 │ (periodic)
                │                 │                 │
                ▼                 ▼                 ▼
┌───────────────────────────────────────────────────────────────────┐
│                        Raspberry Pi                               │
│                                                                   │
│  ┌──────────────────┐              ┌──────────────────┐          │
│  │ Webhook Listener │              │  Git Auto-Pull   │          │
│  │   (Port 8080)    │              │  (Every 5 min)   │          │
│  └────────┬─────────┘              └────────┬─────────┘          │
│           │                                 │                    │
│           │ Trigger                         │ Trigger            │
│           │                                 │                    │
│           └────────────┬────────────────────┘                    │
│                        │                                         │
│                        ▼                                         │
│              ┌──────────────────┐                                │
│              │ git_auto_deploy  │                                │
│              │      .py         │                                │
│              └────────┬─────────┘                                │
│                       │                                          │
│         ┌─────────────┼─────────────┐                            │
│         │             │             │                            │
│         ▼             ▼             ▼                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                       │
│  │Git Fetch │  │Git Pull  │  │ Install  │                       │
│  │& Check   │  │          │  │   Deps   │                       │
│  └──────────┘  └──────────┘  └──────────┘                       │
│         │             │             │                            │
│         └─────────────┼─────────────┘                            │
│                       │                                          │
│                       ▼                                          │
│              ┌──────────────────┐                                │
│              │  post_deploy.sh  │                                │
│              │ (Custom Actions) │                                │
│              └────────┬─────────┘                                │
│                       │                                          │
│                       ▼                                          │
│              ┌──────────────────┐                                │
│              │ Restart Services │                                │
│              │  (if configured) │                                │
│              └────────┬─────────┘                                │
│                       │                                          │
│                       ▼                                          │
│              ┌──────────────────┐                                │
│              │  Code Deployed!  │                                │
│              └──────────────────┘                                │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## Deployment Flow

### Method 1: Webhook (Instant)

```
1. Developer pushes code
   ↓
2. GitHub/GitLab sends webhook to Pi
   ↓
3. Webhook listener receives POST request
   ↓
4. Verifies webhook signature
   ↓
5. Triggers git_auto_deploy.py
   ↓
6. Deployment process runs
   ↓
7. Code deployed in seconds!
```

### Method 2: Periodic Check

```
1. Service runs in background
   ↓
2. Every 5 minutes: Check Git remote
   ↓
3. Compare local vs remote commits
   ↓
4. If changes exist:
   ├─► Trigger git_auto_deploy.py
   └─► Deployment process runs
   ↓
5. If no changes: Wait for next check
```

## Component Details

### git_auto_deploy.py

**Purpose**: Main deployment orchestrator

**Functions**:
- Fetch updates from Git remote
- Check for new commits
- Pull changes
- Install Python dependencies
- Run post-deployment script
- Restart services
- Log everything

**Usage**:
```bash
# Single run
python3 git_auto_deploy.py

# Watch mode (continuous)
python3 git_auto_deploy.py --watch --interval 300

# Custom branch
python3 git_auto_deploy.py --branch develop
```

### webhook_listener.py

**Purpose**: HTTP server for webhooks

**Endpoints**:
- `/webhook/github` - GitHub webhooks
- `/webhook/gitlab` - GitLab webhooks
- `/webhook/manual` - Manual trigger (localhost only)
- `/health` - Health check

**Security**:
- Verifies webhook signatures
- Validates secret tokens
- Restricts manual endpoint to localhost

**Usage**:
```bash
# Start server
python3 webhook_listener.py

# Or via systemd
sudo systemctl start webhook-listener
```

### post_deploy.sh

**Purpose**: Custom post-deployment actions

**Examples**:
```bash
# Restart MQTT broker
sudo systemctl restart mosquitto

# Clear cache
rm -rf __pycache__

# Run tests
python3 -m pytest tests/

# Send notification
mosquitto_pub -h localhost -t system/notifications -m "Deployed"
```

### Systemd Services

**git-deploy.service**:
- Runs git_auto_deploy.py in watch mode
- Checks every 5 minutes
- Auto-starts on boot
- Restarts on failure

**webhook-listener.service**:
- Runs webhook_listener.py
- Listens on port 8080
- Auto-starts on boot
- Restarts on failure

## Data Flow

```
┌─────────────┐
│ Git Remote  │
└──────┬──────┘
       │
       │ git fetch
       ▼
┌─────────────┐
│ Local Repo  │
└──────┬──────┘
       │
       │ git pull
       ▼
┌─────────────┐
│ Working Dir │
└──────┬──────┘
       │
       │ pip install
       ▼
┌─────────────┐
│Dependencies │
└──────┬──────┘
       │
       │ bash script
       ▼
┌─────────────┐
│Post-Deploy  │
└──────┬──────┘
       │
       │ systemctl restart
       ▼
┌─────────────┐
│Running Code │
└─────────────┘
```

## File Structure

```
surveillance-car/
├── deployment/
│   ├── git_auto_deploy.py          # Main deployment script
│   ├── webhook_listener.py         # Webhook server
│   ├── post_deploy.sh              # Post-deployment actions
│   ├── setup_git_deploy.sh         # Setup wizard
│   ├── test_deployment.sh          # Test script
│   ├── git-deploy.service          # Systemd service (periodic)
│   ├── webhook-listener.service    # Systemd service (webhook)
│   ├── requirements.txt            # Python dependencies
│   ├── README.md                   # Overview
│   ├── GIT_AUTO_DEPLOY_GUIDE.md   # Complete guide
│   ├── QUICK_REFERENCE.md         # Command reference
│   └── ARCHITECTURE.md            # This file
├── logs/
│   ├── git_deploy.log             # Deployment logs
│   └── webhook.log                # Webhook logs
├── Drivers/                        # Your code
├── Network/                        # Your code
└── main.py                        # Your code
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
│                                                             │
│  1. Webhook Signature Verification                         │
│     ├─► HMAC-SHA256 signature                              │
│     └─► Secret token validation                            │
│                                                             │
│  2. Network Security                                        │
│     ├─► Firewall rules (ufw)                               │
│     ├─► Port restrictions                                  │
│     └─► Localhost-only for manual triggers                 │
│                                                             │
│  3. Git Authentication                                      │
│     ├─► SSH keys (recommended)                             │
│     └─► HTTPS with tokens                                  │
│                                                             │
│  4. File Permissions                                        │
│     ├─► Scripts executable by owner only                   │
│     ├─► Logs readable by owner only                        │
│     └─► Service files owned by root                        │
│                                                             │
│  5. Process Isolation                                       │
│     ├─► Runs as 'pi' user (not root)                       │
│     ├─► Systemd service isolation                          │
│     └─► Limited sudo access                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Deployment States

```
┌──────────────┐
│   IDLE       │  No deployment in progress
└──────┬───────┘
       │
       │ Trigger (webhook or periodic check)
       ▼
┌──────────────┐
│  FETCHING    │  Fetching updates from remote
└──────┬───────┘
       │
       │ Updates available?
       ▼
┌──────────────┐
│  PULLING     │  Pulling changes
└──────┬───────┘
       │
       │ Pull successful?
       ▼
┌──────────────┐
│  INSTALLING  │  Installing dependencies
└──────┬───────┘
       │
       │ Dependencies installed?
       ▼
┌──────────────┐
│POST-DEPLOYING│  Running post-deploy script
└──────┬───────┘
       │
       │ Script completed?
       ▼
┌──────────────┐
│  RESTARTING  │  Restarting services
└──────┬───────┘
       │
       │ Services restarted?
       ▼
┌──────────────┐
│  COMPLETED   │  Deployment successful
└──────┬───────┘
       │
       │ Return to IDLE
       ▼
┌──────────────┐
│   IDLE       │
└──────────────┘

       │ If any step fails
       ▼
┌──────────────┐
│   FAILED     │  Deployment failed (logged)
└──────┬───────┘
       │
       │ Return to IDLE
       ▼
┌──────────────┐
│   IDLE       │
└──────────────┘
```

## Monitoring & Logging

```
┌─────────────────────────────────────────────────────────────┐
│                    Logging Architecture                     │
│                                                             │
│  ┌──────────────────┐                                       │
│  │ git_auto_deploy  │                                       │
│  └────────┬─────────┘                                       │
│           │                                                 │
│           ├─► logs/git_deploy.log (file)                    │
│           ├─► stdout (console)                              │
│           └─► journalctl (systemd)                          │
│                                                             │
│  ┌──────────────────┐                                       │
│  │webhook_listener  │                                       │
│  └────────┬─────────┘                                       │
│           │                                                 │
│           ├─► logs/webhook.log (file)                       │
│           ├─► stdout (console)                              │
│           └─► journalctl (systemd)                          │
│                                                             │
│  ┌──────────────────┐                                       │
│  │  post_deploy.sh  │                                       │
│  └────────┬─────────┘                                       │
│           │                                                 │
│           └─► Captured by git_auto_deploy                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Network Topology

### Local Network (No Port Forwarding)

```
┌──────────────┐         ┌──────────────┐
│  Computer    │         │ Raspberry Pi │
│              │         │              │
│ 192.168.1.10 │◄───────►│192.168.1.100 │
│              │  LAN    │              │
└──────────────┘         └──────────────┘
       │
       │ Internet
       ▼
┌──────────────┐
│ GitHub/GitLab│
│              │
└──────────────┘

Note: Webhook won't work without port forwarding
      Use periodic auto-pull instead
```

### With Port Forwarding

```
┌──────────────┐
│  Computer    │
└──────┬───────┘
       │
       │ Internet
       ▼
┌──────────────┐
│ GitHub/GitLab│
└──────┬───────┘
       │
       │ Webhook
       ▼
┌──────────────┐
│   Router     │
│ Port Forward │
│ 8080 → Pi    │
└──────┬───────┘
       │
       │ LAN
       ▼
┌──────────────┐
│ Raspberry Pi │
│192.168.1.100 │
│  Port 8080   │
└──────────────┘
```

### With VPN (Recommended)

```
┌──────────────┐         ┌──────────────┐
│  Computer    │         │ Raspberry Pi │
│              │         │              │
│  Tailscale   │◄───────►│  Tailscale   │
│100.64.0.1    │  VPN    │100.64.0.2    │
└──────┬───────┘         └──────────────┘
       │
       │ Internet
       ▼
┌──────────────┐
│ GitHub/GitLab│
│              │
└──────┬───────┘
       │
       │ Webhook via VPN
       └──────────────────►100.64.0.2:8080

Note: Secure, no port forwarding needed
```

## Performance Characteristics

### Periodic Auto-Pull

- **Check Interval**: 5 minutes (configurable)
- **Network Usage**: Minimal (only git fetch)
- **Deployment Time**: 5-30 seconds (after detection)
- **Total Latency**: 0-5 minutes + deployment time
- **CPU Usage**: Negligible
- **Memory Usage**: ~20MB

### Webhook Listener

- **Response Time**: < 1 second
- **Deployment Time**: 5-30 seconds
- **Total Latency**: 5-30 seconds
- **CPU Usage**: Negligible when idle
- **Memory Usage**: ~50MB (Flask server)
- **Network**: Persistent listener on port 8080

## Scalability

### Single Raspberry Pi

```
One deployment system per Pi
├─► Handles unlimited pushes
├─► Sequential deployments
└─► ~30 seconds per deployment
```

### Multiple Raspberry Pis

```
Same webhook URL for all Pis
├─► Each Pi deploys independently
├─► Parallel deployments
└─► No coordination needed
```

### Multiple Branches

```
Configure different Pis for different branches
├─► Pi 1: main branch (production)
├─► Pi 2: develop branch (testing)
└─► Pi 3: feature branches (development)
```

## Failure Handling

```
┌─────────────────────────────────────────────────────────────┐
│                    Failure Recovery                         │
│                                                             │
│  Git Fetch Fails                                            │
│  ├─► Log error                                              │
│  ├─► Return to idle                                         │
│  └─► Retry on next trigger                                  │
│                                                             │
│  Git Pull Fails                                             │
│  ├─► Log error                                              │
│  ├─► Stash local changes                                    │
│  └─► Retry pull                                             │
│                                                             │
│  Dependency Install Fails                                   │
│  ├─► Log warning                                            │
│  ├─► Continue deployment                                    │
│  └─► May need manual fix                                    │
│                                                             │
│  Post-Deploy Script Fails                                   │
│  ├─► Log warning                                            │
│  ├─► Continue deployment                                    │
│  └─► Code still deployed                                    │
│                                                             │
│  Service Restart Fails                                      │
│  ├─► Log warning                                            │
│  ├─► Deployment complete                                    │
│  └─► Manual restart may be needed                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

**This architecture provides a robust, secure, and efficient deployment system for your Raspberry Pi!**
