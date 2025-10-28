#!/usr/bin/env bash
set -euo pipefail

# Deploy rpi-control-panel as a local systemd service.
# Usage:
#   ./deploy_local.sh [--port PORT] [--password PWD] [--user USER] [--remove]
# Examples:
#   ./deploy_local.sh --port 5000 --password changeme
#   sudo ./deploy_local.sh --user pi  # run as root to allow service install

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_DIR="$REPO_ROOT/rpi-control-panel"
SERVICE_NAME="rpi-control-panel.service"

PORT=""
PASSWORD=""
RUN_USER="$(whoami)"
REMOVE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --port)
      PORT="$2"; shift 2;;
    --password)
      PASSWORD="$2"; shift 2;;
    --user)
      RUN_USER="$2"; shift 2;;
    --remove)
      REMOVE=1; shift;;
    *)
      echo "Unknown arg: $1"; exit 1;;
  esac
done

if [ "$REMOVE" -eq 1 ]; then
  echo "Removing service $SERVICE_NAME"
  sudo systemctl disable --now "$SERVICE_NAME" || true
  sudo rm -f "/etc/systemd/system/$SERVICE_NAME"
  sudo systemctl daemon-reload
  echo "Service removed"
  exit 0
fi

if [ ! -d "$LOCAL_DIR" ]; then
  echo "Directory $LOCAL_DIR not found. Run this from the project root." >&2
  exit 1
fi

echo "Setting up virtualenv and installing requirements in $LOCAL_DIR"
python3 -m venv "$LOCAL_DIR/venv" || true
. "$LOCAL_DIR/venv/bin/activate"
python3 -m pip install --upgrade pip
python3 -m pip install -r "$LOCAL_DIR/requirements.txt"

if [ -n "$PASSWORD" ]; then
  echo "Updating PASSWORD in control-panel.py"
  esc_pwd=$(printf '%s' "$PASSWORD" | sed "s/'/'\\''/g")
  sed -i.bak "s/^PASSWORD = .*/PASSWORD = '$esc_pwd'/" "$LOCAL_DIR/control-panel.py" || true
fi

if [ -n "$PORT" ]; then
  echo "Updating INTERFACE_PORT in control-panel.py"
  sed -i.bak "s/^INTERFACE_PORT = .*/INTERFACE_PORT = $PORT/" "$LOCAL_DIR/control-panel.py" || true
fi

SERVICE_CONTENT=$(cat <<EOF
[Unit]
Description=RPi Control Panel
After=network.target

[Service]
Type=simple
User=$RUN_USER
WorkingDirectory=$LOCAL_DIR
Environment=PYTHONUNBUFFERED=1
ExecStart=/bin/bash -lc 'source $LOCAL_DIR/venv/bin/activate && exec python3 $LOCAL_DIR/control-panel.py'
Restart=always

[Install]
WantedBy=multi-user.target
EOF
)

echo "Writing systemd unit to /etc/systemd/system/$SERVICE_NAME (requires sudo)"
echo "$SERVICE_CONTENT" | sudo tee "/etc/systemd/system/$SERVICE_NAME" > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE_NAME"

echo "Service $SERVICE_NAME installed and started. Check logs with: sudo journalctl -u $SERVICE_NAME -f"
