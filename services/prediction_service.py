from typing import Dict, Any, List
from models.email_classifier import EmailClassifier
from models.url_classifier import URLClassifier
from utils.text_preprocessor import TextPreprocessor
from utils.logger import setup_logger
import os

class PredictionService:
    """Main service for coordinating predictions"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.email_classifier = EmailClassifier()
        self.url_classifier = URLClassifier()
        self.text_preprocessor = TextPreprocessor()
        self.models_loaded = False
    
    def load_models(self) -> None:
        """Load all trained models"""
        try:
            models_dir = "models/saved_models"
            
            if not os.path.exists(models_dir):
                raise FileNotFoundError(f"Models directory not found: {models_dir}")
            
            self.email_classifier.load_model(models_dir)
            self.url_classifier.load_model(models_dir)
            
            self.models_loaded = True
            self.logger.info("All models loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading models: {str(e)}")
            raise
    
    def predict(self, text: str, detection_type: str) -> Dict[str, Any]:
        """
        Main predict method for Flask compatibility
        
        Args:
            text: Input text to analyze
            detection_type: 'email' or 'url'
            
        Returns:
            Dictionary with prediction results
        """
        return self.predict_text(text, detection_type)
    
    def predict_text(self, text: str, content_type: str) -> Dict[str, Any]:
        """
        Predict if text content is phishing
        
        Args:
            text: Input text to analyze
            content_type: 'email' or 'url'
            
        Returns:
            Dictionary with prediction results
        """
        if not self.models_loaded:
            raise RuntimeError("Models not loaded")
        
        try:
            if content_type.lower() == 'email':
                return self._predict_email(text)
            elif content_type.lower() == 'url':
                return self._predict_url(text)
            else:
                raise ValueError(f"Invalid content type: {content_type}")
                
        except Exception as e:
            self.logger.error(f"Error in prediction: {str(e)}")
            raise
    
    def _predict_email(self, text: str) -> Dict[str, Any]:
        """Predict email content"""
        # Preprocess email text
        processed_text = self.text_preprocessor.preprocess_email(text)
        
        # Get prediction
        prediction_num, confidence = self.email_classifier.predict(processed_text)
        
        # Debug output
        self.logger.info(f"DEBUG - Email prediction: {prediction_num}, Confidence: {confidence:.4f}")
        print(f"DEBUG - Raw prediction: {prediction_num}, Confidence: {confidence:.4f}")
        
        # TEST BOTH MAPPINGS - we'll determine which is correct
        # First try standard mapping
        if prediction_num == 1:
            prediction = "Phishing"
        else:
            prediction = "Safe"
        
        # If this gives wrong results, we'll invert it
        
        risk_level = self._calculate_risk_level(confidence, prediction == "Phishing")
        
        return {
            'prediction': prediction,
            'confidence': float(confidence),
            'risk_level': risk_level,
            'content_type': 'email',
            'raw_prediction': int(prediction_num),  # Debug info
            'processed_text': processed_text[:100]  # Debug - first 100 chars
        }
    
    def _predict_url(self, url: str) -> Dict[str, Any]:
        """Predict URL safety"""
        # Extract URL features
        features = self.url_classifier.extract_features(url)
        
        # Get prediction
        prediction_num, confidence = self.url_classifier.predict(features)
        
        # Debug output
        self.logger.info(f"DEBUG - URL prediction: {prediction_num}, Confidence: {confidence:.4f}")
        
        # Map prediction
        if prediction_num == 1:
            prediction = "Phishing"
        else:
            prediction = "Safe"
        
        risk_level = self._calculate_risk_level(confidence, prediction == "Phishing")
        
        return {
            'prediction': prediction,
            'confidence': float(confidence),
            'risk_level': risk_level,
            'content_type': 'url',
            'raw_prediction': int(prediction_num)
        }
    
    def _calculate_risk_level(self, confidence: float, is_phishing: bool) -> str:
        """Calculate risk level based on confidence and prediction"""
        if not is_phishing:
            return "Low"
        
        if confidence >= 0.8:
            return "High"
        elif confidence >= 0.6:
            return "Medium"
        else:
            return "Low"
    
    def predict_batch(self, items: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Predict multiple items at once"""
        results = []
        
        for item in items:
            try:
                result = self.predict_text(item['text'], item['type'])
                results.append({
                    'success': True,
                    **result
                })
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'text': item.get('text', '')[:50] + '...'
                })
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            'models_loaded': self.models_loaded,
            'email_classifier_loaded': self.email_classifier.is_loaded,
            'url_classifier_loaded': self.url_classifier.is_loaded,
            'models_directory': "models/saved_models"
        }
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all models (alias for compatibility)"""
        return self.get_model_info()