import os
import json
import shutil
import smtplib
import subprocess
from datetime import datetime
from email.mime.text import MIMEText

CONFIG_PATH = "config/config.json"


def load_config():
    with open(CONFIG_PATH, "r") as file:
        return json.load(file)


def write_log(message, log_file):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    with open(log_file, "a") as file:
        file.write(f"[{timestamp}] {message}\n")

    print(f"[{timestamp}] {message}")


def get_cpu_usage():
    load_avg = os.getloadavg()[0]
    cpu_count = os.cpu_count()
    return round((load_avg / cpu_count) * 100, 2)


def get_memory_usage():
    with open("/proc/meminfo", "r") as file:
        meminfo = file.readlines()

    mem_total = int(meminfo[0].split()[1])
    mem_available = int(meminfo[2].split()[1])

    used_percent = ((mem_total - mem_available) / mem_total) * 100
    return round(used_percent, 2)


def get_disk_usage():
    total, used, free = shutil.disk_usage("/")
    return round((used / total) * 100, 2)


def is_service_running(service_name):
    result = subprocess.run(
        ["systemctl", "is-active", service_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result.stdout.strip() == "active"


def restart_service(service_name, log_file):
    write_log(f"Attempting to restart service: {service_name}", log_file)

    result = subprocess.run(
        ["sudo", "systemctl", "restart", service_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode == 0:
        write_log(f"Successfully restarted service: {service_name}", log_file)
    else:
        write_log(f"Failed to restart service: {service_name}. Error: {result.stderr}", log_file)


def send_alert(subject, body, log_file):
    """
    Placeholder for email alerting.
    In production, configure SMTP credentials using environment variables.
    """
    write_log(f"ALERT: {subject} - {body}", log_file)


def rotate_log(log_file, max_size_mb=5):
    if not os.path.exists(log_file):
        return

    file_size_mb = os.path.getsize(log_file) / (1024 * 1024)

    if file_size_mb >= max_size_mb:
        rotated_file = f"{log_file}.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        os.rename(log_file, rotated_file)


def main():
    config = load_config()

    cpu_threshold = config["cpu_threshold"]
    memory_threshold = config["memory_threshold"]
    disk_threshold = config["disk_threshold"]
    service_name = config["service_name"]
    log_file = config["log_file"]

    rotate_log(log_file)

    cpu_usage = get_cpu_usage()
    memory_usage = get_memory_usage()
    disk_usage = get_disk_usage()

    write_log(f"CPU Usage: {cpu_usage}%", log_file)
    write_log(f"Memory Usage: {memory_usage}%", log_file)
    write_log(f"Disk Usage: {disk_usage}%", log_file)

    if cpu_usage > cpu_threshold:
        send_alert("High CPU Usage", f"CPU usage is {cpu_usage}%", log_file)

    if memory_usage > memory_threshold:
        send_alert("High Memory Usage", f"Memory usage is {memory_usage}%", log_file)

    if disk_usage > disk_threshold:
        send_alert("High Disk Usage", f"Disk usage is {disk_usage}%", log_file)

    if not is_service_running(service_name):
        write_log(f"Service {service_name} is DOWN", log_file)
        send_alert("Service Down", f"{service_name} is not running. Restarting service.", log_file)
        restart_service(service_name, log_file)
    else:
        write_log(f"Service {service_name} is running normally", log_file)


if __name__ == "__main__":
    main()
