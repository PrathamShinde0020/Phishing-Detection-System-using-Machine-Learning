# Phishing Detection System - Project Structure

## Production-Ready Project Organization

```
phishing-detection-system/
│
├── main.py                          # Flask application entry point
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Docker configuration
├── docker-compose.yml              # Container orchestration
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore rules
├── README.md                        # Project documentation
│
├── api/                             # API layer
│   ├── __init__.py
│   └── routes.py                    # API route handlers
│
├── config/                          # Configuration management
│   ├── __init__.py
│   └── settings.py                  # Application settings
│
├── models/                          # Model definitions and storage
│   ├── __init__.py
│   ├── email_classifier.py         # Email classification model
│   ├── url_classifier.py           # URL classification model
│   └── saved_models/                # Trained model files
│       ├── email_classifier.pkl
│       ├── email_vectorizer.pkl
│       └── url_classifier.pkl
│
├── services/                        # Business logic layer
│   ├── __init__.py
│   └── prediction_service.py       # Core prediction logic
│
├── utils/                           # Utility modules
│   ├── __init__.py
│   ├── text_preprocessor.py        # Text preprocessing utilities
│   ├── validators.py               # Input validation
│   └── logger.py                   # Logging configuration
│
├── templates/                       # Frontend templates
│   └── index.html                  # Main web interface
│
├── static/                         # Static assets (optional)
│   ├── css/
│   ├── js/
│   └── images/
│
├── training/                       # Model training scripts
│   ├── __init__.py
│   ├── model_trainer.py           # Training orchestration
│   └── evaluation.py              # Model evaluation utilities
│
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── test_models.py             # Model tests
│   ├── test_api.py                # API endpoint tests
│   ├── test_utils.py              # Utility function tests
│   └── fixtures/                  # Test data and fixtures
│
├── scripts/                        # Deployment and utility scripts
│   ├── deploy.py                  # Deployment automation
│   ├── backup_models.py           # Model backup utility
│   └── health_check.py            # System health monitoring
│
├── data/                           # Dataset storage (development only)
│   ├── Phishing_Email.csv         # Email dataset
│   ├── PhishingData.csv           # URL dataset
│   └── processed/                 # Processed datasets
│
├── logs/                           # Application logs
│   ├── phishing_detector.log      # Main application logs
│   ├── errors.log                 # Error logs
│   └── security.log               # Security audit logs
│
├── docs/                           # Documentation
│   ├── API.md                     # API documentation
│   ├── DEPLOYMENT.md              # Deployment guide
│   └── CONTRIBUTING.md            # Contribution guidelines
│
└── notebooks/                     # Development notebooks (optional)
    ├── email_model_development.ipynb
    └── url_model_development.ipynb
```

## Key Design Principles

### 1. Separation of Concerns
- **API Layer**: Handles HTTP requests and responses
- **Service Layer**: Contains business logic and orchestration
- **Model Layer**: Encapsulates ML model operations
- **Utils Layer**: Reusable utility functions
- **Config Layer**: Centralized configuration management

### 2. Production Readiness
- **Error Handling**: Comprehensive exception handling throughout
- **Logging**: Structured logging with rotation and security auditing
- **Validation**: Input sanitization and validation
- **Security**: Security headers, rate limiting, and input validation
- **Monitoring**: Health checks and system monitoring
- **Scalability**: Docker containerization and load balancer ready

### 3. Code Organization
- **Modular Design**: Each component has a single responsibility
- **Clean Interfaces**: Well-defined APIs between components
- **Configuration Management**: Environment-based configuration
- **Type Hints**: Python type annotations for better code quality
- **Documentation**: Comprehensive docstrings and comments

### 4. Development Workflow
- **Training Pipeline**: Automated model training and evaluation
- **Testing**: Unit tests and integration tests
- **Deployment**: Automated deployment scripts
- **CI/CD Ready**: Structure supports continuous integration

## File Responsibilities

### Core Application Files
- `main.py`: Flask application entry point and routing
- `requirements.txt`: Python package dependencies
- `Dockerfile`: Container configuration for production deployment

### Business Logic
- `services/prediction_service.py`: Core prediction orchestration
- `models/email_classifier.py`: Email-specific classification logic
- `models/url_classifier.py`: URL-specific classification logic

### Infrastructure
- `config/settings.py`: Environment and application configuration
- `utils/logger.py`: Logging and monitoring setup
- `utils/validators.py`: Input validation and security

### Frontend
- `templates/index.html`: User interface with modern responsive design
- `api/routes.py`: RESTful API endpoints for external integration

### Training and Deployment
- `training/model_trainer.py`: Model training and evaluation pipeline
- `scripts/deploy.py`: Automated deployment and setup

## Environment Variables

Create a `.env` file in the root directory:

```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
LOG_LEVEL=INFO
PORT=5000
```

## Quick Start Commands

```bash
# Setup environment
python scripts/deploy.py --mode local

# Train models (if datasets available)
python training/model_trainer.py

# Run application
python main.py

# Run with Docker
docker-compose up -d
```

## Security Features

- Input validation and sanitization
- Rate limiting on API endpoints
- Security headers and CSRF protection
- Comprehensive audit logging
- Container security with non-root user
- Secret management through environment variables

This structure provides a robust, scalable, and maintainable foundation for a production phishing detection system.