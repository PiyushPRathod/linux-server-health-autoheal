# Linux Server Health Auto-Healing Monitor

## Overview
This project is a Linux-based SRE automation script that monitors server health and performs basic auto-healing actions when issues are detected.

## Features
- Monitors CPU usage
- Monitors memory usage
- Monitors disk usage
- Checks service health using systemctl
- Restarts failed services automatically
- Logs health checks and incidents
- Supports log rotation
- Can be scheduled with cron

## Tech Stack
- Python
- Linux
- Bash / systemctl
- Cron
- Nginx
- Log-based monitoring

## Architecture
Cron Job → Python Monitoring Script → Linux Metrics Check → Service Health Check → Auto-Restart → Logs / Alerts

## Install Test Services

```bash
sudo apt update
sudo apt install nginx -y
sudo systemctl start nginx
```

## Run Script

```bash
python3 scripts/health_autoheal.py
```

## Test Auto-Healing

```bash
sudo systemctl stop nginx
python3 scripts/health_autoheal.py
systemctl status nginx
```

- Expected Output
```bash
Service nginx is DOWN
Attempting to restart service: nginx
Successfully restarted service: nginx
```

## Automate with Cron

```bash
crontab -e

*/5 * * * * cd /home/YOUR_USER/linux-server-health-autoheal && /usr/bin/python3 scripts/health_autoheal.py
```

- This runs every 5 minutes
