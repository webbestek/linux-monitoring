# Linux Monitoring Setup

This guide will help you set up a monitoring system for your Linux machine (Raspberry Pi or any other Debian-based system). The system will track CPU temperature, CPU usage, memory usage, and disk usage. It will automatically shut down the system if the temperature exceeds a defined threshold and send email alerts for high CPU, memory, or disk usage.

### Features:
- **Monitor system temperature, CPU usage, memory usage, and disk usage.**
- **Shutdown the system if the temperature exceeds a defined threshold.**
- **Send email alerts for high CPU, memory, or disk usage.**
- **Logging to track the system's health.**
- **Runs every 5 minutes using a cron job.**

## Install Automatically

The easiest way to install the monitoring system is by using the provided installation shell script. This script will automatically install all dependencies, set up the necessary files, and configure the system to run the monitoring script every 5 minutes via a cron job.

### Step 1: Download and Run the Install Script

1. **Open a terminal** on your Linux machine.
2. **Run the following command to download the installation script:**

```bash
curl -sSL https://github.com/webbestek/linux-monitoring/raw/main/setup.sh | sudo bash
```

3. The script will automatically perform the following tasks:
   - Install required packages like `git`, `python3`, and `python3-pip`.
   - Clone the repository containing the monitoring files.
   - Set up the necessary environment variables and files.
   - Add the cron job to run the monitoring script every 5 minutes.

4. **Once the script completes**, the system will be set up, and the monitoring system will run every 5 minutes.

## Contributing

If you'd like to contribute to this project, feel free to open a **pull request**! You can also report issues by opening an **issue** in the repository.

## Troubleshooting

- If the emails aren't sending, ensure that your email credentials are correct and that your SMTP server settings match your email provider's configuration.
- Check the logs (`/home/user/linux-monitoring/monitoring.log`) for any error messages related to system resource usage or script issues.

## Conclusion

You now have a fully automated monitoring system for your Linux machine that checks key system parameters (temperature, CPU, memory, and disk) every 5 minutes via a cron job, and will send email alerts or shut down the system if necessary. This ensures that the system is monitored and any issues are dealt with in a timely manner.
