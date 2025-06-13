# utils/usage_logger.py

import csv
from datetime import datetime
import os

LOG_FILE = "usage_logs.csv"

def log_usage(format_choice, duration=None):
    """Ajoute une ligne de log dans usage_logs.csv"""
    now = datetime.now().isoformat(timespec='seconds')
    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["timestamp", "format", "duration_minutes"])
        writer.writerow([now, format_choice, round(duration or 0, 2)])
