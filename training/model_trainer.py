import pandas as pd
import numpy as np
import joblib
import os
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.preprocessing import LabelEncoder
from utils.text_preprocessor import TextPreprocessor
from utils.logger import setup_logger
from config.settings import MODEL_PATHS, MODEL_CONFIG

class ModelTrainer:
    """Model training and evaluation for phishing detection"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.text_preprocessor = TextPreprocessor()
        
    def train_email_classifier(self, data_path: str, save_path: str = None) -> dict:
        """
        Train email phishing classifier
        
        Args:
            data_path: Path to the email dataset CSV
            save_path: Path to save trained models
            
        Returns:
            Training results dictionary
        """
        try:
            self.logger.info("Starting email classifier training")
            
            # Load and preprocess data
            df = pd.read_csv(data_path)
            df = self._preprocess_email_data(df)
            
            # Prepare features and labels
            X, y = self._prepare_email_features(df)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train multiple models and select best
            models = {
                'logistic_regression': LogisticRegression(
                    max_iter=1000,
                    random_state=42
                ),
                'random_forest': RandomForestClassifier(
                    n_estimators=100,
                    random_state=42
                ),
                'mlp': MLPClassifier(
                    hidden_layer_sizes=(100, 50),
                    max_iter=500,
                    random_state=42
                )
            }
            
            best_model = None
            best_score = 0
            results = {}
            
            for name, model in models.items():
                self.logger.info(f"Training {name}")
                
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                
                accuracy = accuracy_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred)
                
                results[name] = {
                    'accuracy': accuracy,
                    'f1_score': f1,
                    'classification_report': classification_report(y_test, y_pred)
                }
                
                if f1 > best_score:
                    best_score = f1
                    best_model = model
                    best_model_name = name
            
            # Save best model
            if save_path:
                self._save_email_model(best_model, save_path)
            
            self.logger.info(f"Best model: {best_model_name} (F1: {best_score:.4f})")
            
            return {
                'best_model': best_model_name,
                'best_score': best_score,
                'all_results': results
            }
            
        except Exception as e:
            self.logger.error(f"Error training email classifier: {str(e)}")
            raise
    
    def train_url_classifier(self, data_path: str, save_path: str = None) -> dict:
        """
        Train URL phishing classifier
        
        Args:
            data_path: Path to the URL dataset CSV
            save_path: Path to save trained models
            
        Returns:
            Training results dictionary
        """
        try:
            self.logger.info("Starting URL classifier training")
            
            # Load and preprocess data
            df = pd.read_csv(data_path)
            df = self._preprocess_url_data(df)
            
            # Prepare features and labels
            X = df.drop(['Result'], axis=1).values
            y = df['Result'].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train models
            models = {
                'random_forest': RandomForestClassifier(
                    n_estimators=100,
                    random_state=42
                ),
                'logistic_regression': LogisticRegression(
                    max_iter=1000,
                    random_state=42
                )
            }
            
            best_model = None
            best_score = 0
            results = {}
            
            for name, model in models.items():
                self.logger.info(f"Training {name}")
                
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                
                accuracy = accuracy_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred)
                
                results[name] = {
                    'accuracy': accuracy,
                    'f1_score': f1,
                    'classification_report': classification_report(y_test, y_pred)
                }
                
                if f1 > best_score:
                    best_score = f1
                    best_model = model
                    best_model_name = name
            
            # Save best model
            if save_path:
                self._save_url_model(best_model, save_path)
            
            self.logger.info(f"Best URL model: {best_model_name} (F1: {best_score:.4f})")
            
            return {
                'best_model': best_model_name,
                'best_score': best_score,
                'all_results': results
            }
            
        except Exception as e:
            self.logger.error(f"Error training URL classifier: {str(e)}")
            raise
    
    def _preprocess_email_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess email dataset"""
        # Drop unnecessary columns
        if 'Unnamed: 0' in df.columns:
            df = df.drop(['Unnamed: 0'], axis=1)
        
        # Remove duplicates and null values
        df = df.drop_duplicates()
        df = df.dropna()
        
        # Encode labels
        if df['Email Type'].dtype == 'object':
            le = LabelEncoder()
            df['Email Type'] = le.fit_transform(df['Email Type'])
        
        # Preprocess email text
        df['Email Text'] = df['Email Text'].apply(
            self.text_preprocessor.preprocess_email
        )
        
        return df
    
    def _preprocess_url_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess URL dataset"""
        # Drop index column if present
        if 'index ' in df.columns:
            df = df.drop(['index '], axis=1)
        
        # Remove duplicates and null values
        df = df.drop_duplicates()
        df = df.dropna()
        
        # Ensure all features are numeric
        feature_columns = [col for col in df.columns if col != 'Result']
        for col in feature_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove any remaining null values
        df = df.dropna()
        
        return df
    
    def _prepare_email_features(self, df: pd.DataFrame) -> tuple:
        """Prepare features for email classification"""
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=MODEL_CONFIG['email']['max_features'],
            ngram_range=MODEL_CONFIG['email']['ngram_range'],
            min_df=MODEL_CONFIG['email']['min_df'],
            max_df=MODEL_CONFIG['email']['max_df']
        )
        
        # Transform text to features
        X = vectorizer.fit_transform(df['Email Text']).toarray()
        y = df['Email Type'].values
        
        # Save vectorizer for later use
        self.email_vectorizer = vectorizer
        
        return X, y
    
    def _save_email_model(self, model, save_path: str):
        """Save email model and vectorizer"""
        os.makedirs(save_path, exist_ok=True)
        
        model_file = os.path.join(save_path, 'email_classifier.pkl')
        vectorizer_file = os.path.join(save_path, 'email_vectorizer.pkl')
        
        joblib.dump(model, model_file)
        joblib.dump(self.email_vectorizer, vectorizer_file)
        
        self.logger.info(f"Email model saved to {save_path}")
    
    def _save_url_model(self, model, save_path: str):
        """Save URL model"""
        os.makedirs(save_path, exist_ok=True)
        
        model_file = os.path.join(save_path, 'url_classifier.pkl')
        joblib.dump(model, model_file)
        
        self.logger.info(f"URL model saved to {save_path}")

def main():
    """Main training script"""
    trainer = ModelTrainer()
    
    # Paths to datasets
    email_data_path = "data/Phishing_Email.csv"
    url_data_path = "data/PhishingData.csv"
    
    # Model save path
    save_path = MODEL_PATHS['email_model']
    
    try:
        # Train email classifier
        if os.path.exists(email_data_path):
            email_results = trainer.train_email_classifier(
                email_data_path, 
                save_path
            )
            print("Email Classifier Results:")
            for model, results in email_results['all_results'].items():
                print(f"{model}: Accuracy={results['accuracy']:.4f}, F1={results['f1_score']:.4f}")
        
        # Train URL classifier
        if os.path.exists(url_data_path):
            url_results = trainer.train_url_classifier(
                url_data_path,
                save_path
            )
            print("\nURL Classifier Results:")
            for model, results in url_results['all_results'].items():
                print(f"{model}: Accuracy={results['accuracy']:.4f}, F1={results['f1_score']:.4f}")
    
    except Exception as e:
        print(f"Training failed: {str(e)}")

if __name__ == "__main__":
    main()