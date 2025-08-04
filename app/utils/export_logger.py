import logging
import os
from datetime import datetime

# Set up logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "export_logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, f"export_log_{datetime.now().strftime('%Y%m%d')}.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_export(message: str):
    """Log an export-related message"""
    print(f"EXPORT LOG: {message}")  # Print to console
    logging.info(message)  # Write to log file
