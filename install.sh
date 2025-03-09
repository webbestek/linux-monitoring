#!/bin/bash

CURRENT_USER=$(whoami)
HOME_DIR="/home/$CURRENT_USER"

MONITORING_DIR="$HOME_DIR/linux-monitoring"
LOG_DIRECTORY="$MONITORING_DIR/logs"

LOGROTATE_CONF="/etc/logrotate.d/linux-monitoring"

MONITORING_ENV_FILE="$MONITORING_DIR/.env"
ENV_DIST_FILE="templates/.env.template"

INSTALL_LOG_FILE="$LOG_DIRECTORY/linux-monitoring-install.log"

# Define monitoring script path for substitution.
# Adjust the filename if your script name differs.
MONITORING_SCRIPT="$MONITORING_DIR/bin/monitor.py"

# Log messages (prints with timestamp and appends to log file)
log_msg() {
    local msg="$1"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Ensure the directory for the log file exists
    local log_dir
    log_dir=$(dirname "$INSTALL_LOG_FILE")
    mkdir -p "$log_dir"
    
    echo "[$timestamp] $msg" | tee -a "$INSTALL_LOG_FILE"
}

# Spinner function to show activity while a command is running
spinner() {
    local pid=$1
    local delay=0.1
    local spin_chars=('|' '/' '-' '\\')
    local i=0
    while kill -0 "$pid" 2>/dev/null; do
        printf "\r[%s]" "${spin_chars[i]}"
        i=$(( (i + 1) % 4 ))
        sleep "$delay"
    done
    printf "\r"
}

# Process a template file by replacing placeholders and writing the result.
process_template() {
    local template_file="$1"
    local destination_file="$2"
    sed -e "s|\[LOG_DIRECTORY\]|$LOG_DIRECTORY|g" \
        -e "s|\[MONITORING_SCRIPT_PATH\]|$MONITORING_SCRIPT|g" \
        "$template_file" | sudo tee "$destination_file" > /dev/null
}

# Install required packages
install_packages() {
    local missing_packages=""
    local pkg

    # Lijst met alle benodigde pakketten
    for pkg in python3-pip git python3-psutil python3-dotenv lm-sensors python3-smbus logrotate; do
        if ! dpkg -s "$pkg" >/dev/null 2>&1; then
            missing_packages="$missing_packages $pkg"
        fi
    done

    if [ -n "$missing_packages" ]; then
        log_msg "[+] Installing missing packages: $missing_packages"
        sudo apt install -y $missing_packages
        log_msg "[+] Missing packages installed."
    else
        log_msg "[+] All required packages are already installed. Skipping."
    fi
}

# Initial installation
install() {
    log_msg "[+] Starting installation..."
    mkdir -p "$MONITORING_DIR"
    mkdir -p "$LOG_DIRECTORY"
    cp -r "src/." "$MONITORING_DIR/bin" & spinner $!

    if [ ! -f "$MONITORING_ENV_FILE" ] && [ -f "$ENV_DIST_FILE" ]; then
        cp "$ENV_DIST_FILE" "$MONITORING_ENV_FILE" & spinner $!
        log_msg "[+] .env file created from .env.dist."
        env_edit_prompt
    else
        log_msg "[+] .env already exists. Skipping."
    fi
    
    log_msg "[+] Required files installed."
}

# Prompt the user to edit the .env file
env_edit_prompt() {
    log_msg "[!] Please update the .env file with correct details (e.g., nano $ENV_FILE)."
}

# Set up a cronjob to run the monitoring script every 5 minutes.
setup_cronjob() {
    log_msg "[+] Configuring cronjob..."
    # Check if the cron entry already exists by searching for the monitoring script path.
    if ! crontab -l 2>/dev/null | grep -q "$MONITORING_SCRIPT"; then
         # Append the new cron entry. Adjust the schedule if needed.
         (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/bin/python3 $MONITORING_SCRIPT") | crontab -
         log_msg "[+] Cronjob added. To edit, run: crontab -e"
    else
         log_msg "[+] Cronjob already exists. Skipping."
    fi
}

# Configure logrotate using the template file
setup_logrotate() {
    log_msg "[+] Setting up logrotate..."
    if [ ! -f "$LOGROTATE_CONF" ]; then
        process_template "templates/logrotate.template" "$LOGROTATE_CONF"
        log_msg "[+] Logrotate configuration created."
    else
        log_msg "[+] Logrotate configuration already exists. Skipping."
    fi
}

# Run all steps
install_packages
install
setup_cronjob
setup_logrotate

log_msg "[✓] Installation complete!"
