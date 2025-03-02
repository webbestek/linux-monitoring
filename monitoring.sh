#!/bin/bash

# Get the current user and the directory paths
CURRENT_USER=$(whoami)
HOME_DIR="/home/$CURRENT_USER"
MONITORING_DIR="$HOME_DIR/linux-monitoring"

# Change to the monitoring directory
cd "$MONITORING_DIR" || { echo "[!] Failed to change directory to $MONITORING_DIR"; exit 1; }

# Run the Python script with the correct Python binary
/usr/bin/python3 monitor.py
