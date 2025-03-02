#!/bin/bash

set -e  # Stop script on errors

# Variables
CURRENT_USER=$(whoami)
HOME_DIR="/home/$CURRENT_USER"
MONITORING_DIR="$HOME_DIR/linux-monitoring"
LOGROTATE_CONF="/etc/logrotate.d/linux-monitoring"
ENV_FILE="$MONITORING_DIR/.env"
ENV_DIST_FILE="$MONITORING_DIR/.env.dist"
REPO_URL="https://github.com/webbestek/linux-monitoring.git"

# Step 1: Install required packages
echo "[+] Installing required packages..."
sudo apt update -qq || { echo "[!] Failed to update package lists"; exit 1; }
sudo apt install -y python3-pip git python3-psutil python3-dotenv logrotate >/dev/null 2>&1 || { echo "[!] Failed to install required packages"; exit 1; }

# Step 2: Ensure the linux-monitoring directory exists
echo "[+] Ensuring linux-monitoring directory exists..."
if [ ! -d "$MONITORING_DIR" ]; then
    echo "[+] Directory $MONITORING_DIR does not exist. Cloning the repository..."
    git clone "$REPO_URL" "$MONITORING_DIR" || { echo "[!] Failed to clone the repository"; exit 1; }
fi

# Step 3: Copy .env.dist to .env
echo "[+] Copying .env.dist to .env..."
if [ -f "$ENV_DIST_FILE" ]; then
    cp "$ENV_DIST_FILE" "$ENV_FILE"
else
    echo "[!] .env.dist file not found! Please ensure the file is present in $MONITORING_DIR."
    exit 1
fi

# Step 4: Update .env file with correct directory path
echo "[+] Updating .env file with correct directory path..."
sed -i "s|^DIRECTORY=.*|DIRECTORY=$MONITORING_DIR|" "$ENV_FILE"

echo "[!] Please update the .env file with the correct details using nano or vim:"
echo "nano $ENV_FILE"
echo "[!] Press SPACE when you're done to continue."
read -n 1 -s -r -p ""

# Step 5: Set up monitoring script
echo "cd $MONITORING_DIR && /usr/bin/python3 monitor.py" > "$MONITORING_DIR/monitoring.sh"
chmod +x "$MONITORING_DIR/monitoring.sh"

# Step 6: Add cronjob
echo "[+] Adding cronjob..."
(crontab -l 2>/dev/null; echo "*/5 * * * * $MONITORING_DIR/monitoring.sh") | crontab -

# Step 7: Configure logrotate
echo "[+] Setting up logrotate..."
sudo bash -c "cat > $LOGROTATE_CONF" <<EOL
$MONITORING_DIR/monitoring.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    size 10M
    dateext
    maxage 7
}
EOL

echo "[✓] Installation complete!"
