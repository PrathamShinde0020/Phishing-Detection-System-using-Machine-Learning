#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
from pathlib import Path
from utils.logger import setup_logger

class DeploymentManager:
    """Handles deployment operations for the phishing detection system"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.base_dir = Path(__file__).parent.parent
        
    def setup_environment(self):
        """Setup the deployment environment"""
        try:
            self.logger.info("Setting up deployment environment")
            
            # Create necessary directories
            directories = [
                'logs',
                'models/saved_models',
                'data',
                'tmp'
            ]
            
            for directory in directories:
                dir_path = self.base_dir / directory
                dir_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created directory: {directory}")
            
            # Set permissions
            os.chmod(self.base_dir / 'logs', 0o755)
            os.chmod(self.base_dir / 'models', 0o755)
            
            self.logger.info("Environment setup completed")
            
        except Exception as e:
            self.logger.error(f"Environment setup failed: {str(e)}")
            raise
    
    def install_dependencies(self):
        """Install Python dependencies"""
        try:
            self.logger.info("Installing dependencies")
            
            requirements_file = self.base_dir / 'requirements.txt'
            if not requirements_file.exists():
                raise FileNotFoundError("requirements.txt not found")
            
            # Install requirements
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
            ], check=True)
            
            self.logger.info("Dependencies installed successfully")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install dependencies: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Dependency installation error: {str(e)}")
            raise
    
    def train_models(self):
        """Train and save models"""
        try:
            self.logger.info("Starting model training")
            
            # Check if datasets exist
            email_data = self.base_dir / 'data' / 'Phishing_Email.csv'
            url_data = self.base_dir / 'data' / 'PhishingData.csv'
            
            if not email_data.exists() or not url_data.exists():
                self.logger.warning("Dataset files not found. Skipping model training.")
                self.logger.warning("Please place dataset files in the data/ directory")
                return
            
            # Import and run training
            from training.model_trainer import ModelTrainer
            
            trainer = ModelTrainer()
            
            # Train email classifier
            email_results = trainer.train_email_classifier(
                str(email_data),
                str(self.base_dir / 'models' / 'saved_models')
            )
            
            # Train URL classifier
            url_results = trainer.train_url_classifier(
                str(url_data),
                str(self.base_dir / 'models' / 'saved_models')
            )
            
            self.logger.info("Model training completed successfully")
            self.logger.info(f"Email model best F1 score: {email_results['best_score']:.4f}")
            self.logger.info(f"URL model best F1 score: {url_results['best_score']:.4f}")
            
        except Exception as e:
            self.logger.error(f"Model training failed: {str(e)}")
            raise
    
    def run_tests(self):
        """Run application tests"""
        try:
            self.logger.info("Running application tests")
            
            # Check if test directory exists
            test_dir = self.base_dir / 'tests'
            if test_dir.exists():
                subprocess.run([
                    sys.executable, '-m', 'pytest', str(test_dir), '-v'
                ], check=True)
                self.logger.info("All tests passed")
            else:
                self.logger.warning("No tests directory found")
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Tests failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Test execution error: {str(e)}")
            raise
    
    def deploy_local(self):
        """Deploy application locally"""
        try:
            self.logger.info("Starting local deployment")
            
            # Set environment variables
            os.environ['FLASK_ENV'] = 'production'
            os.environ['LOG_LEVEL'] = 'INFO'
            
            # Start the application
            subprocess.run([
                sys.executable, 'main.py'
            ], cwd=self.base_dir)
            
        except Exception as e:
            self.logger.error(f"Local deployment failed: {str(e)}")
            raise
    
    def deploy_docker(self):
        """Deploy application using Docker"""
        try:
            self.logger.info("Starting Docker deployment")
            
            # Build Docker image
            subprocess.run([
                'docker', 'build', '-t', 'phishing-detector', '.'
            ], cwd=self.base_dir, check=True)
            
            # Run with docker-compose
            subprocess.run([
                'docker-compose', 'up', '-d'
            ], cwd=self.base_dir, check=True)
            
            self.logger.info("Docker deployment completed")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Docker deployment failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Docker deployment error: {str(e)}")
            raise
    
    def check_system_requirements(self):
        """Check system requirements"""
        try:
            self.logger.info("Checking system requirements")
            
            # Check Python version
            python_version = sys.version_info
            if python_version < (3, 8):
                raise RuntimeError("Python 3.8 or higher is required")
            
            # Check available disk space
            import shutil
            total, used, free = shutil.disk_usage(self.base_dir)
            free_gb = free // (2**30)
            
            if free_gb < 2:
                self.logger.warning(f"Low disk space: {free_gb}GB available")
            
            self.logger.info("System requirements check passed")
            
        except Exception as e:
            self.logger.error(f"System requirements check failed: {str(e)}")
            raise

def main():
    """Main deployment script"""
    parser = argparse.ArgumentParser(description='Phishing Detection System Deployment')
    parser.add_argument('--mode', choices=['local', 'docker'], default='local',
                       help='Deployment mode')
    parser.add_argument('--skip-training', action='store_true',
                       help='Skip model training')
    parser.add_argument('--skip-tests', action='store_true',
                       help='Skip running tests')
    
    args = parser.parse_args()
    
    deployer = DeploymentManager()
    
    try:
        # Pre-deployment checks
        deployer.check_system_requirements()
        deployer.setup_environment()
        deployer.install_dependencies()
        
        # Model training
        if not args.skip_training:
            deployer.train_models()
        
        # Run tests
        if not args.skip_tests:
            deployer.run_tests()
        
        # Deploy based on mode
        if args.mode == 'docker':
            deployer.deploy_docker()
        else:
            deployer.deploy_local()
            
        print("Deployment completed successfully!")
        
    except Exception as e:
        print(f"Deployment failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()