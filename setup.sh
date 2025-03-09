#!/bin/bash

# Log function for setup actions
log_msg() {
    local msg="$1"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $msg"
}

# Define the installation directory and repository URL
INSTALL_DIR="/opt/linux-monitoring"
REPO_URL="https://github.com/webbestek/linux-monitoring"

log_msg "[+] Cloning repository from $REPO_URL to $INSTALL_DIR..."

# Clone the repository into the /opt directory
sudo git clone "$REPO_URL" "$INSTALL_DIR"

if [ $? -eq 0 ]; then
    log_msg "[+] Repository cloned successfully."
else
    log_msg "[!] Failed to clone repository. Exiting."
    exit 1
fi

# Change to the installation directory
cd "$INSTALL_DIR" || exit 1

# Make sure install.sh is executable
sudo chmod +x install.sh

# Execute install.sh
log_msg "[+] Running install.sh..."
sudo ./install.sh