import os
import logging.config
import logging
from datetime import datetime

def setup_logging(log_dir="logs"):
    """
    Set up logging configuration for the application.
    Creates different log files for different logging levels.
    """
    os.makedirs(log_dir, exist_ok=True)
    
    # Create formatters
    verbose_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # Create handlers for different log levels
    info_handler = logging.FileHandler(
        os.path.join(log_dir, f'info_{datetime.now().strftime("%Y%m%d")}.log')
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(verbose_formatter)
    
    error_handler = logging.FileHandler(
        os.path.join(log_dir, f'error_{datetime.now().strftime("%Y%m%d")}.log')
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(verbose_formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(simple_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(info_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    # Create module loggers
    modules = ['deck', 'session', 'word']
    loggers = {}
    
    for module in modules:
        logger = logging.getLogger(f'remembering_words.{module}')
        logger.setLevel(logging.INFO)
        loggers[module] = logger
    
    return loggers