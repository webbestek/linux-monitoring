#!/bin/bash

# Set environment variables (ensure Python and PATH are available)
export PATH=$PATH:/usr/bin:/bin
export HOME="/home/$(whoami)"

# Define the directory paths
MONITORING_DIR="$HOME/linux-monitoring"
LOG_DIR="$MONITORING_DIR/logs"
SCRIPT_PATH="$MONITORING_DIR/bin/monitor.py"
LOG_FILE="$LOG_DIR/monitoring.log"

# Check if the monitoring directory exists
if [[ ! -d "$MONITORING_DIR" ]]; then
    echo "[!] Monitoring directory not found: $MONITORING_DIR" >> "$LOG_FILE"
    exit 1
fi

# Check if the Python script exists
if [[ ! -f "$SCRIPT_PATH" ]]; then
    echo "[!] Python script not found: $SCRIPT_PATH" >> "$LOG_FILE"
    exit 1
fi

# Run the Python script with the correct Python binary and log output
/usr/bin/python3 "$SCRIPT_PATH" || { echo "[!] Python script execution failed" >> "$LOG_FILE"; exit 1; }
