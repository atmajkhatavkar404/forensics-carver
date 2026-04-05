import hashlib
import logging
import os
import datetime
from typing import Optional

def setup_logging(log_dir: str = "logs") -> logging.Logger:
    """Configures the forensic logger."""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"recovery_{timestamp}.log")
    
    logger = logging.getLogger("ForensicCarver")
    logger.setLevel(logging.DEBUG)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_file_hash(file_path: str, algorithm: str = "sha256") -> str:
    """Calculates the hash of a file."""
    hash_func = getattr(hashlib, algorithm)()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def calculate_checksum(data: bytes) -> str:
    """Calculates the SHA256 checksum of raw data."""
    return hashlib.sha256(data).hexdigest()

def format_bytes(size: int) -> str:
    """Formats bytes to human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def get_sector_offset(byte_offset: int, sector_size: int = 512) -> int:
    """Returns the sector number for a byte offset."""
    return byte_offset // sector_size
