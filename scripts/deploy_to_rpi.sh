#!/usr/bin/env bash
set -euo pipefail

# Usage:
# ./deploy_to_rpi.sh <user@host> [remote_dir] [--password PWD] [--port PORT] [--autostart]
# Deploys only the screen-controller component

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <user@host> [remote_dir] [--password PWD] [--port PORT] [--autostart]"
  exit 1
fi

USER_HOST="$1"
COMPONENT="screen-controller"
REMOTE_DIR=""
PASSWORD=""
PORT=""
AUTOSTART=0

shift 1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --password)
      PASSWORD="$2"; shift 2;;
    --port)
      PORT="$2"; shift 2;;
    --autostart)
      AUTOSTART=1; shift;;
    *)
      if [ -z "$REMOTE_DIR" ]; then REMOTE_DIR="$1"; else echo "Unknown arg: $1"; exit 1; fi
      shift;;
  esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

LOCAL_DIR="$REPO_ROOT/screen-controller"
DEFAULT_REMOTE_DIR="~/screen-controller"
SERVICE_NAME="screen-controller.service"

REMOTE_DIR="${REMOTE_DIR:-$DEFAULT_REMOTE_DIR}"

# Resolve remote absolute path (create dir if necessary) and use it for all subsequent operations.
echo "Resolving remote absolute path for $REMOTE_DIR on $USER_HOST..."
ABS_REMOTE_DIR=$(ssh "$USER_HOST" "bash -lc 'mkdir -p $REMOTE_DIR && cd $REMOTE_DIR && pwd'") || { echo "Failed to resolve remote directory on $USER_HOST"; exit 1; }

echo "Deploying $COMPONENT -> $USER_HOST:$ABS_REMOTE_DIR"

# Copy files to the resolved absolute path on the remote
rsync -avz --delete --exclude __pycache__/ "$LOCAL_DIR/" "$USER_HOST:$ABS_REMOTE_DIR/"

echo "Files copied. Running remote setup..."

# Prepare remote commands
SSH_CMD="bash -s"
ssh $USER_HOST $SSH_CMD <<EOF
set -e
cd $ABS_REMOTE_DIR
# Create venv if not exists
python3 -m venv venv || true
. venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt || true
EOF

if [ "$AUTOSTART" -eq 1 ]; then
  echo "Installing autostart launcher for user on remote"
  # Create a small launcher script in the deployed directory that activates the venv and runs server.py
  ssh $USER_HOST $SSH_CMD <<SSH_EOF
set -e
cat > "$ABS_REMOTE_DIR/start_on_login.sh" <<'SH'
#!/usr/bin/env bash
cd "$ABS_REMOTE_DIR"
. venv/bin/activate
exec python3 "$ABS_REMOTE_DIR/server.py"
SH
chmod +x "$ABS_REMOTE_DIR/start_on_login.sh"
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/screen-controller.desktop <<'DESK'
[Desktop Entry]
Type=Application
Name=Screen Controller
Exec=$ABS_REMOTE_DIR/start_on_login.sh
X-GNOME-Autostart-enabled=true
DESK
SSH_EOF
  echo "Autostart entry written to ~/.config/autostart/screen-controller.desktop"
fi

if [ -n "$PASSWORD" ]; then
  echo "Updating PASSWORD on remote"
  # Use sed on remote to replace the PASSWORD line (creates a .bak backup)
  ssh $USER_HOST "sed -i.bak 's/^PASSWORD = .*/PASSWORD = \"$PASSWORD\"/' \"$ABS_REMOTE_DIR/server.py\" || true"
fi

if [ -n "$PORT" ]; then
  echo "Updating PORT on remote"
  # Use sed on remote to replace the PORT line (creates a .bak backup)
  ssh $USER_HOST "sed -i.bak 's/^PORT = .*/PORT = $PORT/' \"$ABS_REMOTE_DIR/server.py\" || true"
fi

# service deployment removed; use --autostart for session autostart instead

echo "Deployment finished."
