"""
Structured logging system for FlowNotes
Provides consistent logging across all modules with file rotation
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime


class FlowNotesLogger:
    """Centralized logging configuration for FlowNotes"""

    _instance = None
    _loggers = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.log_dir = Path.home() / "Projects" / "notes" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Set up root logger configuration
        self._setup_root_logger()

    def _setup_root_logger(self):
        """Configure the root logger with handlers"""
        root_logger = logging.getLogger("flownotes")
        root_logger.setLevel(logging.DEBUG)

        # Remove existing handlers to avoid duplicates
        root_logger.handlers.clear()

        # File handler with rotation (10MB max, keep 5 backups)
        log_file = self.log_dir / f"flownotes_{datetime.now():%Y%m%d}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        # Console handler (only INFO and above)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Detailed formatter for file
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Simple formatter for console
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )

        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)

        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger for a specific module

        Args:
            name: Module name (e.g., 'learning_enhancements', 'note_system')

        Returns:
            Configured logger instance
        """
        full_name = f"flownotes.{name}"

        if full_name not in self._loggers:
            logger = logging.getLogger(full_name)
            self._loggers[full_name] = logger

        return self._loggers[full_name]

    def set_level(self, level: str):
        """
        Set logging level for all loggers

        Args:
            level: One of 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        """
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }

        log_level = level_map.get(level.upper(), logging.INFO)
        logging.getLogger("flownotes").setLevel(log_level)


# Convenience function for getting logger
def get_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for the specified module

    Usage:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Starting note consolidation")

    Args:
        module_name: Name of the module (use __name__)

    Returns:
        Configured logger instance
    """
    logger_manager = FlowNotesLogger()
    return logger_manager.get_logger(module_name)


# Example usage patterns:
if __name__ == "__main__":
    # Test the logging system
    logger = get_logger("test_module")

    logger.debug("This is a debug message")
    logger.info("Starting process...")
    logger.warning("This might be an issue")
    logger.error("Something went wrong")

    try:
        raise ValueError("Test exception")
    except Exception as e:
        logger.exception("Exception occurred: %s", str(e))

    print(f"\nLog file created at: {FlowNotesLogger().log_dir}")
