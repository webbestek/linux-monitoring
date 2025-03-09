import os
import logging
import smtplib
import psutil
import subprocess
import socket
import time
import platform

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass

@dataclass
class Config:
    sender_email: str
    sender_password: str
    receiver_email: str
    smtp_server: str
    smtp_port: int
    temp_threshold: float
    cpu_threshold: float
    memory_threshold: float
    disk_threshold: float
    log_level: str
    monitoring_dir: Path
    log_file: Path

def load_config() -> Config:
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent
    env_path = project_dir / ".env"
    
    if not env_path.exists():
        raise FileNotFoundError(".env file not found. Please create one with the necessary configuration.")
    
    load_dotenv(dotenv_path=env_path)
    
    return Config(
        sender_email=os.getenv("SENDER_EMAIL"),
        sender_password=os.getenv("SENDER_PASSWORD"),
        receiver_email=os.getenv("RECEIVER_EMAIL"),
        smtp_server=os.getenv("SMTP_SERVER"),
        smtp_port=int(os.getenv("SMTP_PORT", 587)),
        temp_threshold=float(os.getenv("TEMP_THRESHOLD", 80)),
        cpu_threshold=float(os.getenv("CPU_THRESHOLD", 90)),
        memory_threshold=float(os.getenv("MEMORY_THRESHOLD", 90)),
        disk_threshold=float(os.getenv("DISK_THRESHOLD", 90)),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        monitoring_dir=project_dir,
        log_file=project_dir / "logs" / "monitoring.log"
    )

def setup_logging(log_file: Path, log_level: str) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=log_file,
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(module)s.%(funcName)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.info("Logging configured.")

def get_hostname() -> str:
    return socket.gethostname()

def get_network_usage() -> dict:
    net_io = psutil.net_io_counters()
    return {
        "bytes_sent": net_io.bytes_sent,
        "bytes_received": net_io.bytes_recv,
    }

def get_system_uptime() -> float:
    return time.time() - psutil.boot_time()

def get_temperatures() -> dict:
    temperatures = {}
    if platform.system() == "Windows":
        try:
            import wmi
            sensor_info = wmi.WMI(namespace="root\\WMI").MSAcpi_ThermalZoneTemperature()
            for idx, sensor in enumerate(sensor_info):
                temperatures[f"Sensor_{idx}"] = round(sensor.CurrentTemperature / 10 - 273.15, 2)
        except Exception as e:
            logging.warning("Windows temperature monitoring is unavailable: %s", e)
    elif platform.system() == "Linux":
        try:
            output = subprocess.run(["sensors"], capture_output=True, text=True).stdout
            for line in output.split("\n"):
                if "temp" in line.lower():
                    parts = line.split(":")
                    if len(parts) == 2:
                        sensor_name = parts[0].strip()
                        temp_value = parts[1].split()[0].replace("°C", "").strip()
                        temperatures[sensor_name] = float(temp_value)
        except Exception as e:
            logging.warning("Linux temperature monitoring is unavailable: %s", e)
    return temperatures

def get_cpu_usage() -> float:
    return psutil.cpu_percent(interval=1)

def get_memory_usage() -> float:
    return psutil.virtual_memory().percent

def get_disk_usage() -> float:
    return psutil.disk_usage("/").percent

def send_email(config: Config, subject: str, body: str) -> None:
    msg = MIMEMultipart()
    msg['From'] = config.sender_email
    msg['To'] = config.receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        with smtplib.SMTP(config.smtp_server, config.smtp_port) as server:
            server.starttls()
            server.login(config.sender_email, config.sender_password)
            server.sendmail(config.sender_email, config.receiver_email, msg.as_string())
        logging.info("Alert email sent!")
    except Exception as e:
        logging.error("Failed to send email: %s", e)

def alert(config: Config, subject: str, body: str) -> None:
    if config.sender_email:
        send_email(config, subject, body)
    else:
        logging.warning("[Email Alert] %s: %s", subject, body)

def monitor_system(config: Config) -> None:
    hostname = get_hostname()
    network_usage = get_network_usage()
    uptime_hours = get_system_uptime() / 3600
    temperatures = get_temperatures()
    cpu_usage = get_cpu_usage()
    memory_usage = get_memory_usage()
    disk_usage = get_disk_usage()
    
    logging.info("Hostname: %s", hostname)
    logging.info("System Uptime: %.2f hours", uptime_hours)
    logging.info("Network Usage - Sent: %d bytes, Received: %d bytes",
                 network_usage['bytes_sent'], network_usage['bytes_received'])
    logging.info("CPU Usage: %.2f%%", cpu_usage)
    logging.info("Memory Usage: %.2f%%", memory_usage)
    logging.info("Disk Usage: %.2f%%", disk_usage)
    
    if temperatures:
        for sensor, temp in temperatures.items():
            if temp >= config.temp_threshold:
                logging.error("Temperature: Error - High Temperature Alert - %s: %.2f°C", sensor, temp)
                alert(config, f"High Temperature Alert - {sensor}", f"{sensor} temperature is too high: {temp:.2f}°C")
            else:
                logging.info("Temperature: Normal - %s: %.2f°C", sensor, temp)
    else:
        logging.info("Temperature: No temperature sensors found.")
    
    if cpu_usage >= config.cpu_threshold:
        alert(config, "High CPU Usage Alert", f"CPU usage is too high: {cpu_usage:.2f}%")
    if memory_usage >= config.memory_threshold:
        alert(config, "High Memory Usage Alert", f"Memory usage is too high: {memory_usage:.2f}%")
    if disk_usage >= config.disk_threshold:
        alert(config, "High Disk Usage Alert", f"Disk usage is too high: {disk_usage:.2f}%")

def main() -> None:
    try:
        config = load_config()
        setup_logging(config.log_file, config.log_level)
        monitor_system(config)
    except Exception as e:
        logging.error("Critical error occurred: %s", e)
        print("Error: ", e)

if __name__ == "__main__":
    main()
