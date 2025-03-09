import os
import logging
import smtplib
import psutil
import subprocess
import socket
import time
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

def get_gpu_temperature() -> float:
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            check=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        logging.warning("GPU monitoring is unavailable: %s", e)
        return None

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

def shutdown_system(config: Config, reason: str) -> None:
    logging.error("Shutting down due to: %s", reason)
    alert(config, "System Shutdown Alert", f"Your system is shutting down because: {reason}")
    subprocess.run(["sudo", "shutdown", "now"], check=False)

def monitor_system(config: Config) -> None:
    hostname = get_hostname()
    network_usage = get_network_usage()
    uptime_hours = get_system_uptime() / 3600
    gpu_temp = get_gpu_temperature()
    
    logging.info("Hostname: %s", hostname)
    logging.info("System Uptime: %.2f hours", uptime_hours)
    logging.info("Network Usage - Sent: %d bytes, Received: %d bytes", 
                 network_usage['bytes_sent'], network_usage['bytes_received'])
    
    if gpu_temp is not None:
        logging.info("GPU Temperature: %.2f°C", gpu_temp)
        if gpu_temp >= config.temp_threshold:
            alert(config, "High GPU Temperature Alert", f"GPU temperature is too high: {gpu_temp:.2f}°C")
    
    if uptime_hours > 168:  # 7 days
        alert(config, "High System Uptime Alert", f"System has been running for {uptime_hours:.2f} hours")
    
    if network_usage['bytes_received'] > 10**9 or network_usage['bytes_sent'] > 10**9:
        alert(config, "High Network Usage Alert", "More than 1GB of data transferred.")

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
