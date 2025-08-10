import joblib
import numpy as np
from typing import Tuple, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from utils.logger import setup_logger

class EmailClassifier:
    """Email phishing detection classifier"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.model = None
        self.vectorizer = None
        self.is_loaded = False
    
    def load_model(self, model_path: str) -> None:
        """
        Load trained model and vectorizer
        
        Args:
            model_path: Path to the model directory
        """
        try:
            model_file = f"{model_path}/email_classifier.pkl"
            vectorizer_file = f"{model_path}/email_vectorizer.pkl"
            
            self.model = joblib.load(model_file)
            self.vectorizer = joblib.load(vectorizer_file)
            
            self.is_loaded = True
            self.logger.info("Email classifier loaded successfully")
            
            # Debug: Print model info
            if hasattr(self.model, 'classes_'):
                self.logger.info(f"Model classes: {self.model.classes_}")
            
        except Exception as e:
            self.logger.error(f"Error loading email classifier: {str(e)}")
            raise
    
    def predict(self, text: str) -> Tuple[int, float]:
        """
        Predict if email text is phishing
        
        Args:
            text: Preprocessed email text
            
        Returns:
            Tuple of (prediction, confidence)
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            # Transform text using loaded vectorizer
            text_features = self.vectorizer.transform([text])
            
            # Get prediction and probability
            prediction = self.model.predict(text_features)[0]
            probabilities = self.model.predict_proba(text_features)[0]
            confidence = np.max(probabilities)
            
            # Debug logging
            self.logger.info(f"Email prediction - Raw: {prediction}, Confidence: {confidence:.4f}")
            
            return prediction, confidence
            
        except Exception as e:
            self.logger.error(f"Error making email prediction: {str(e)}")
            raise
    
    def predict_proba(self, text: str) -> np.ndarray:
        """
        Get prediction probabilities
        
        Args:
            text: Preprocessed email text
            
        Returns:
            Array of probabilities for each class
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            text_features = self.vectorizer.transform([text])
            probabilities = self.model.predict_proba(text_features)[0]
            return probabilities
            
        except Exception as e:
            self.logger.error(f"Error getting email probabilities: {str(e)}")
            raise
    
    def transform(self, text: str) -> np.ndarray:
        """
        Transform text to features
        
        Args:
            text: Raw text to transform
            
        Returns:
            Feature vector
        """
        if not self.is_loaded:
            raise RuntimeError("Vectorizer not loaded")
        
        try:
            return self.vectorizer.transform([text])
        except Exception as e:
            self.logger.error(f"Error transforming text: {str(e)}")
            raise
    
    def predict_batch(self, texts: List[str]) -> List[Tuple[int, float]]:
        """
        Predict multiple emails at once
        
        Args:
            texts: List of preprocessed email texts
            
        Returns:
            List of (prediction, confidence) tuples
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            text_features = self.vectorizer.transform(texts)
            predictions = self.model.predict(text_features)
            probabilities = self.model.predict_proba(text_features)
            confidences = np.max(probabilities, axis=1)
            
            return list(zip(predictions, confidences))
            
        except Exception as e:
            self.logger.error(f"Error making batch email predictions: {str(e)}")
            raise
    
    def save_model(self, model_path: str) -> None:
        """
        Save trained model and vectorizer
        
        Args:
            model_path: Path to save the model files
        """
        if not self.is_loaded:
            raise RuntimeError("No model to save")
        
        try:
            model_file = f"{model_path}/email_classifier.pkl"
            vectorizer_file = f"{model_path}/email_vectorizer.pkl"
            
            joblib.dump(self.model, model_file)
            joblib.dump(self.vectorizer, vectorizer_file)
            
            self.logger.info(f"Email classifier saved to {model_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving email classifier: {str(e)}")
            raise