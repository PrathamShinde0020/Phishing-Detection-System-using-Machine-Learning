import joblib
import numpy as np
import re
from typing import Tuple, List, Dict
from urllib.parse import urlparse
from utils.logger import setup_logger

class URLClassifier:
    """URL phishing detection classifier"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.model = None
        self.is_loaded = False
        self.expected_features = 30  # Default, will be updated when model loads
    
    def load_model(self, model_path: str) -> None:
        """
        Load trained URL classifier model
        
        Args:
            model_path: Path to the model file
        """
        try:
            model_file = f"{model_path}/url_classifier.pkl"
            self.model = joblib.load(model_file)
            
            # Get expected number of features from the model
            self.expected_features = self.model.n_features_in_
            self.logger.info(f"Model expects {self.expected_features} features")
            
            self.is_loaded = True
            self.logger.info("URL classifier loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading URL classifier: {str(e)}")
            raise
    
    def extract_features(self, url: str) -> np.ndarray:
        """
        Extract features from URL for classification
        
        Args:
            url: URL string to extract features from
            
        Returns:
            Numpy array of extracted features
        """
        try:
            features = []
            parsed_url = urlparse(url)
            
            # Feature 1: Having IP Address
            features.append(self._has_ip_address(url))
            
            # Feature 2: URL Length
            features.append(self._get_url_length_category(len(url)))
            
            # Feature 3: Shortening Service
            features.append(self._has_shortening_service(url))
            
            # Feature 4: Having @ Symbol
            features.append(1 if '@' in url else -1)
            
            # Feature 5: Double slash redirecting
            features.append(self._has_double_slash_redirect(url))
            
            # Feature 6: Prefix Suffix
            features.append(self._has_prefix_suffix(parsed_url.netloc))
            
            # Feature 7: Having Sub Domain
            features.append(self._count_subdomains(parsed_url.netloc))
            
            # Feature 8-30: Additional features (dynamic based on model expectation)
            # Calculate remaining features needed
            remaining_features = self.expected_features - len(features)
            for i in range(remaining_features):
                features.append(0)
            
            feature_array = np.array(features).reshape(1, -1)
            self.logger.debug(f"Generated {len(features)} features for model expecting {self.expected_features}")
            
            return feature_array
            
        except Exception as e:
            self.logger.error(f"Error extracting URL features: {str(e)}")
            raise
    
    def _has_ip_address(self, url: str) -> int:
        """Check if URL contains IP address"""
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        return 1 if re.search(ip_pattern, url) else -1
    
    def _get_url_length_category(self, length: int) -> int:
        """Categorize URL based on length"""
        if length < 54:
            return -1  # Legitimate
        elif length <= 75:
            return 0   # Suspicious
        else:
            return 1   # Phishing
    
    def _has_shortening_service(self, url: str) -> int:
        """Check if URL uses shortening service"""
        shortening_services = [
            'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 
            'short.link', 'ow.ly', 'is.gd'
        ]
        return 1 if any(service in url.lower() for service in shortening_services) else -1
    
    def _has_double_slash_redirect(self, url: str) -> int:
        """Check for double slash redirecting"""
        return 1 if url.count('//') > 1 else -1
    
    def _has_prefix_suffix(self, domain: str) -> int:
        """Check if domain has prefix-suffix separated by dash"""
        return 1 if '-' in domain else -1
    
    def _count_subdomains(self, domain: str) -> int:
        """Count number of subdomains"""
        if not domain:
            return -1
        
        subdomain_count = domain.count('.')
        if subdomain_count <= 1:
            return -1  # Legitimate
        elif subdomain_count == 2:
            return 0   # Suspicious
        else:
            return 1   # Phishing
    
    def predict(self, features: np.ndarray) -> Tuple[int, float]:
        """
        Predict if URL is phishing based on features
        
        Args:
            features: Extracted URL features
            
        Returns:
            Tuple of (prediction, confidence)
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            prediction = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]
            confidence = np.max(probabilities)
            
            # Debug logging
            self.logger.info(f"URL prediction - Raw: {prediction}, Confidence: {confidence:.4f}")
            
            return prediction, confidence
            
        except Exception as e:
            self.logger.error(f"Error making URL prediction: {str(e)}")
            raise
    
    def predict_proba(self, features: np.ndarray) -> np.ndarray:
        """
        Get prediction probabilities
        
        Args:
            features: Extracted URL features
            
        Returns:
            Array of probabilities for each class
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            probabilities = self.model.predict_proba(features)[0]
            return probabilities
            
        except Exception as e:
            self.logger.error(f"Error getting URL probabilities: {str(e)}")
            raise
    
    def save_model(self, model_path: str) -> None:
        """
        Save trained URL classifier model
        
        Args:
            model_path: Path to save the model
        """
        if not self.is_loaded:
            raise RuntimeError("No model to save")
        
        try:
            model_file = f"{model_path}/url_classifier.pkl"
            joblib.dump(self.model, model_file)
            
            self.logger.info(f"URL classifier saved to {model_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving URL classifier: {str(e)}")
            raise