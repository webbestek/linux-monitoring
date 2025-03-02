#!/usr/bin/env python3
import os
import psutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from dotenv import load_dotenv

def setup_environment() -> None:
    """
    Load environment variables, configure global variables, and set up logging.
    """
    load_dotenv()

    global SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL, SMTP_SERVER, SMTP_PORT
    global TEMP_THRESHOLD, CPU_THRESHOLD, MEMORY_THRESHOLD, DISK_THRESHOLD
    global CURRENT_USER, HOME_DIR, MONITORING_DIR, LOG_FILE

    # Environment variables
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
    RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    TEMP_THRESHOLD = float(os.getenv("TEMP_THRESHOLD", 80))
    CPU_THRESHOLD = float(os.getenv("CPU_THRESHOLD", 90))
    MEMORY_THRESHOLD = float(os.getenv("MEMORY_THRESHOLD", 90))
    DISK_THRESHOLD = float(os.getenv("DISK_THRESHOLD", 90))

    # Set the monitoring directory to /home/<user>/linux-monitoring
    CURRENT_USER = os.getenv("USER", "user")
    HOME_DIR = f"/home/{CURRENT_USER}"
    MONITORING_DIR = os.path.join(HOME_DIR, "linux-monitoring")

    # Set up logging in MONITORING_DIR/logs/monitoring.log
    log_dir = os.path.join(MONITORING_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    LOG_FILE = os.path.join(log_dir, "monitoring.log")

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(module)s.%(funcName)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.info("Environment and logging configured.")

def get_cpu_temp() -> float:
    """
    Read the CPU temperature from the system file.
    Returns:
        Temperature in °C as a float, or None if an error occurs.
    """
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_milli = float(f.read().strip())
            return temp_milli / 1000
    except Exception as e:
        logging.error(f"Error reading CPU temperature: {e}")
        return None

def send_email(subject: str, body: str) -> None:
    """
    Send an email with the specified subject and body.
    """
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        logging.info("Alert email sent!")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

def log_or_send_email(subject: str, body: str) -> None:
    """
    Send an email if SENDER_EMAIL is set; otherwise, log the alert.
    """
    if SENDER_EMAIL:
        send_email(subject, body)
    else:
        logging.warning(f"[Email Alert] {subject}: {body}")

def shutdown_system(reason: str) -> None:
    """
    Log a critical error, send a shutdown alert, and initiate system shutdown.
    """
    logging.error(f"Shutting down due to: {reason}")
    log_or_send_email("System Shutdown Alert", f"Your system is shutting down because: {reason}")
    os.system("sudo shutdown now")

def monitor_system() -> None:
    """
    Monitor system metrics (temperature, CPU, memory, disk) and act if thresholds are exceeded.
    """
    temp = get_cpu_temp()
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent

    logging.info(f"Temperature: {temp}°C")
    logging.info(f"CPU Usage: {cpu_usage}%")
    logging.info(f"Memory Usage: {memory_usage}%")
    logging.info(f"Disk Usage: {disk_usage}%")

    if temp is not None and temp >= TEMP_THRESHOLD:
        shutdown_system("Temperature too high!")
    elif cpu_usage >= CPU_THRESHOLD:
        log_or_send_email("High CPU Usage Alert", f"CPU usage is too high! Current usage: {cpu_usage}%")
    elif memory_usage >= MEMORY_THRESHOLD:
        log_or_send_email("High Memory Usage Alert", f"Memory usage is too high! Current usage: {memory_usage}%")
    elif disk_usage >= DISK_THRESHOLD:
        log_or_send_email("High Disk Usage Alert", f"Disk usage is too high! Current usage: {disk_usage}%")

def main() -> None:
    """
    Main entry point: sets up the environment and starts system monitoring.
    """
    setup_environment()
    monitor_system()

if __name__ == "__main__":
    main()
