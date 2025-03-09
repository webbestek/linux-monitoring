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

# Check if git is installed, and install it if necessary
if ! command -v git &> /dev/null; then
    log_msg "[+] Git is not installed. Installing..."
    sudo apt update && sudo apt install -y git
    if [ $? -eq 0 ]; then
        log_msg "[+] Git installed successfully."
    else
        log_msg "[!] Failed to install Git. Exiting."
        exit 1
    fi
else
    log_msg "[+] Git is already installed."
fi

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

# Clean up the temporary files (cloned repo)
log_msg "[+] Temporary files have been removed."
sudo rm -rf "$INSTALL_DIR"

# Ask the user if they want to reboot
read -p "Do you want to reboot now? (y/n): " reboot_choice

if [[ "$reboot_choice" == "y" || "$reboot_choice" == "Y" ]]; then
    log_msg "[+] Rebooting the system..."
    sudo reboot
else
    log_msg "[+] Installation complete. No reboot will be performed."
fi
