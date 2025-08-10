import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name: str) -> logging.Logger:
    """
    Setup and configure logger for the application
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Set log level from environment or default to INFO
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, 'phishing_detector.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, 'errors.log'),
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Add formatter to handlers
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    return logger

class SecurityLogger:
    """Security-specific logging for monitoring suspicious activities"""
    
    def __init__(self):
        self.logger = setup_logger(f"{__name__}.security")
        self.security_log_file = 'logs/security.log'
        self._setup_security_handler()
    
    def _setup_security_handler(self):
        """Setup dedicated security log handler"""
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        security_handler = RotatingFileHandler(
            filename=self.security_log_file,
            maxBytes=20 * 1024 * 1024,  # 20MB
            backupCount=10
        )
        security_handler.setLevel(logging.WARNING)
        
        security_formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )
        security_handler.setFormatter(security_formatter)
        
        self.logger.addHandler(security_handler)
    
    def log_suspicious_activity(self, activity: str, details: dict = None):
        """Log suspicious activity"""
        message = f"Suspicious Activity: {activity}"
        if details:
            message += f" | Details: {details}"
        self.logger.warning(message)
    
    def log_potential_attack(self, attack_type: str, source: str, details: dict = None):
        """Log potential security attacks"""
        message = f"Potential Attack: {attack_type} from {source}"
        if details:
            message += f" | Details: {details}"
        self.logger.error(message)
    
    def log_model_prediction(self, prediction_type: str, result: str, confidence: float):
        """Log model predictions for audit trail"""
        message = f"Model Prediction: {prediction_type} -> {result} (confidence: {confidence:.2f})"
        self.logger.info(message)