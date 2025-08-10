import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Model paths
MODEL_PATHS = {
    'email_model': os.path.join(BASE_DIR, 'models', 'saved_models'),
    'url_model': os.path.join(BASE_DIR, 'models', 'saved_models')
}

# Flask configuration
class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'phishing-detector-secret-key-2024')
    DEBUG = False
    TESTING = False
    
    # Request limits
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_DEFAULT = "100 per hour"
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    
    # Production-specific security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'default')
    return config_map.get(env, config_map['default'])

# Model configuration
MODEL_CONFIG = {
    'email': {
        'max_features': 10000,
        'ngram_range': (1, 2),
        'min_df': 2,
        'max_df': 0.95,
        'stop_words': 'english'
    },
    'url': {
        'feature_count': 31,
        'feature_names': [
            'having_IP_Address', 'URL_Length', 'Shortining_Service',
            'having_At_Symbol', 'double_slash_redirecting', 'Prefix_Suffix',
            'having_Sub_Domain', 'SSLfinal_State', 'Domain_registeration_length',
            'Favicon', 'port', 'HTTPS_token', 'Request_URL', 'URL_of_Anchor',
            'Links_in_tags', 'SFH', 'Submitting_to_email', 'Abnormal_URL',
            'Redirect', 'on_mouseover', 'RightClick', 'popUpWidnow', 'Iframe',
            'age_of_domain', 'DNSRecord', 'web_traffic', 'Page_Rank',
            'Google_Index', 'Links_pointing_to_page', 'Statistical_report', 'Result'
        ]
    }
}

# API configuration
API_CONFIG = {
    'version': 'v1',
    'rate_limits': {
        'predict': '50 per minute',
        'batch_predict': '10 per minute'
    },
    'timeouts': {
        'prediction': 30,  # seconds
        'model_loading': 60  # seconds
    }
}

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'security': {
            'format': '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}