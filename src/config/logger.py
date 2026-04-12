"""
Logger: Configurazione del logging per debug e monitoraggio
"""

import logging
import sys
from pathlib import Path


def setup_logger(name: str, log_level: str = "INFO", log_file: str = None) -> logging.Logger:
    """
    Configura il logger per CDN-FRAMEWORK
    
    Args:
        name: Nome del logger
        log_level: Livello di log (DEBUG, INFO, WARNING, ERROR)
        log_file: File dove salvare i log (None = solo console)
    
    Returns:
        Logger configurato
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level))
    
    # Formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    # File handler (opzionale)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
