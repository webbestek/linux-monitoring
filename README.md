
# Linux Monitoring Setup

This guide will help you set up a monitoring system for your Linux machine (Raspberry Pi or any other Debian-based system). The system will track CPU temperature, CPU usage, memory usage, and disk usage. It will automatically shut down the system if the temperature exceeds a defined threshold and send email alerts for high CPU, memory, or disk usage.

### Features:
- **Monitor system temperature, CPU usage, memory usage, and disk usage.**
- **Shutdown the system if the temperature exceeds a defined threshold.**
- **Send email alerts for high CPU, memory, or disk usage.**
- **Logging to track the system's health.**
- **Runs every 5 minutes using a cron job.**

---

## Install Automatically (Using Install-Shell)

The easiest way to install the monitoring system is by using the provided installation shell script. This script will automatically install all dependencies, set up the necessary files, and configure the system to run the monitoring script every 5 minutes via a cron job.

### Step 1: Download and Run the Install Script

1. **Open a terminal** on your Linux machine.
2. **Run the following command to download the installation script:**

```bash
curl -sSL https://github.com/webbestek/linux-monitoring/raw/main/install.sh | bash
```

3. The script will automatically perform the following tasks:
   - Install required packages like `git`, `python3`, and `python3-pip`.
   - Clone the repository containing the monitoring files.
   - Set up the necessary environment variables and files.
   - Add the cron job to run the monitoring script every 5 minutes.

4. **Once the script completes**, the system will be set up, and the monitoring system will run every 5 minutes.

---

## Install Manually

If you'd like more control over the installation process, you can follow these manual steps.

### Step 1: Install Required Packages

To install Git, Python 3, and the necessary Python libraries:

```bash
sudo apt update
sudo apt install python3-pip git
sudo apt install python3-psutil
sudo apt install python3-dotenv
```

### Step 2: Clone the Repository

Clone the project from the GitHub repository:

```bash
git clone https://github.com/webbestek/linux-monitoring.git
cd linux-monitoring
```

This will download the project files, including the monitoring script (`monitor.py`).

### Step 3: Prepare the Python Script

1. The Python script for monitoring is located in the `linux-monitoring/monitor.py` file. This script will handle system resource monitoring and email alerts.

### Step 4: Set Up Environment Variables

You need to create a `.env` file to store your sensitive data, such as email credentials.

1. **Create the `.env` file inside the project folder**:

```bash
nano /home/user/linux-monitoring/.env
```

2. **Add the following environment variables** to the `.env file:

```bash
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_email_password
RECEIVER_EMAIL=receiver_email@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
TEMP_THRESHOLD=80
CPU_THRESHOLD=90
MEMORY_THRESHOLD=90
DISK_THRESHOLD=90
LOG_FILE=/home/user/linux-monitoring/monitoring.log
```

Make sure to replace the placeholders with your actual values.

### Step 5: Create the Monitoring Script

1. Create a new shell script to run the Python monitoring script (`monitoring.sh`):

```bash
nano /home/user/linux-monitoring/monitoring.sh
```

2. **Add the following content** to the `monitoring.sh` file:

```bash
#!/bin/bash

# Load environment variables
source /home/user/linux-monitoring/.env

# Run the monitoring Python script
/usr/bin/python3 /home/user/linux-monitoring/monitor.py
```

Make the script executable:

```bash
chmod +x /home/user/linux-monitoring/monitoring.sh
```

### Step 6: Set Up the Cron Job

1. **Add the following cron job** to run the monitoring script every 5 minutes. Run the command below:

```bash
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/user/linux-monitoring/monitoring.sh") | crontab -
```

This will add an entry to your crontab to run the `monitoring.sh` script every 5 minutes.

### Step 7: Test the Monitoring System

To manually test the script, run the following command:

```bash
/home/user/linux-monitoring/monitoring.sh
```

Check the logs for activity in `/home/user/linux-monitoring/monitoring.log`:

```bash
tail -f /home/user/linux-monitoring/monitoring.log
```

You should see entries about the system's temperature, CPU usage, memory usage, and disk usage.

---

## Logrotation

To prevent your logs from growing too large, set up log rotation.

1. **Install logrotate**:

```bash
sudo apt install logrotate -y
```

2. **Create the logrotate configuration** for your monitoring logs:

```bash
sudo nano /etc/logrotate.d/linux-monitoring
```

3. **Add the following configuration**:

```ini
/home/user/linux-monitoring/monitoring.log {
    daily                # Rotate logs daily
    rotate 7             # Keep 7 days of logs
    compress             # Compress old log files
    missingok            # Don't throw an error if the log file is missing
    notifempty           # Don't rotate if the log file is empty
    size 10M             # Rotate the log file when it reaches 10MB
    dateext              # Add a date extension to rotated files (e.g. monitoring.log-2023-02-15.gz)
    maxage 7             # Delete rotated log files older than 7 days
}
```

---

## Contributing

If you'd like to contribute to this project, feel free to open a **pull request**! You can also report issues by opening an **issue** in the repository.

---

## Troubleshooting

- If the emails aren't sending, ensure that your email credentials are correct and that your SMTP server settings match your email provider's configuration.
- Check the logs (`/home/user/linux-monitoring/monitoring.log`) for any error messages related to system resource usage or script issues.

---

## Conclusion

You now have a fully automated monitoring system for your Linux machine that checks key system parameters (temperature, CPU, memory, and disk) every 5 minutes via a cron job, and will send email alerts or shut down the system if necessary. This ensures that the system is monitored and any issues are dealt with in a timely manner.
