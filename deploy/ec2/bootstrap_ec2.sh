#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/ubuntu/thedaily"
ENV_FILE="/etc/thedaily.env"
REPO_URL="${1:-}"

if [ -z "$REPO_URL" ]; then
  echo "Usage: $0 <git_repo_url>"
  exit 1
fi

sudo apt-get update -y
sudo apt-get install -y git curl python3 python3-venv python3-pip nginx

if [ ! -d "$APP_DIR" ]; then
  git clone "$REPO_URL" "$APP_DIR"
else
  git -C "$APP_DIR" pull --ff-only
fi

python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install --upgrade pip
"$APP_DIR/.venv/bin/pip" install -e "$APP_DIR"

sudo install -m 0640 -o root -g root "$APP_DIR/deploy/ec2/thedaily.env.example" "$ENV_FILE"

sudo install -m 0644 "$APP_DIR/deploy/ec2/thedaily-streamlit.service" /etc/systemd/system/thedaily-streamlit.service
sudo install -m 0644 "$APP_DIR/deploy/ec2/thedaily-pipeline.service" /etc/systemd/system/thedaily-pipeline.service
sudo install -m 0644 "$APP_DIR/deploy/ec2/thedaily-pipeline.timer" /etc/systemd/system/thedaily-pipeline.timer
sudo install -m 0644 "$APP_DIR/deploy/ec2/nginx-thedaily.conf" /etc/nginx/sites-available/thedaily

sudo ln -sf /etc/nginx/sites-available/thedaily /etc/nginx/sites-enabled/thedaily
sudo rm -f /etc/nginx/sites-enabled/default

sudo systemctl daemon-reload
sudo systemctl enable --now thedaily-streamlit.service
sudo systemctl enable --now thedaily-pipeline.timer
sudo systemctl restart nginx

cat <<MSG
Bootstrap complete.
Next steps:
1. Edit $ENV_FILE with your API keys.
2. Run: sudo systemctl restart thedaily-streamlit.service
3. Run once now: sudo systemctl start thedaily-pipeline.service
MSG
