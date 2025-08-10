#!/usr/bin/env python3
"""
Debug script to check what labels your model was trained with
Run this to understand the correct label mapping
"""

import pandas as pd
import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder

def check_training_data_labels():
    """Check the labels in your training data"""
    print("=== CHECKING TRAINING DATA LABELS ===")
    
    try:
        # Load your email training data
        df = pd.read_csv("data/Phishing_Email.csv")
        print(f"Dataset shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Check the label column (assuming it's 'Email Type')
        label_column = 'Email Type'  # Adjust if different
        if label_column in df.columns:
            print(f"\nOriginal {label_column} values:")
            print(df[label_column].value_counts())
            
            # Check data types
            print(f"\nData type: {df[label_column].dtype}")
            
            # If it's string labels, show what LabelEncoder would do
            if df[label_column].dtype == 'object':
                print("\nWhat LabelEncoder would create:")
                le = LabelEncoder()
                encoded_labels = le.fit_transform(df[label_column])
                
                # Show the mapping
                for i, label in enumerate(le.classes_):
                    print(f"'{label}' -> {i}")
                
                print(f"\nEncoded label distribution:")
                unique, counts = np.unique(encoded_labels, return_counts=True)
                for label_num, count in zip(unique, counts):
                    original_label = le.inverse_transform([label_num])[0]
                    print(f"{label_num} ({original_label}): {count} samples")
            
            else:
                print(f"\nNumeric label distribution:")
                print(df[label_column].value_counts().sort_index())
                
        else:
            print(f"Column '{label_column}' not found!")
            print(f"Available columns: {list(df.columns)}")
            
    except FileNotFoundError:
        print("Training data file not found!")
    except Exception as e:
        print(f"Error reading training data: {e}")

def check_saved_model():
    """Check what the saved model predicts on known samples"""
    print("\n=== CHECKING SAVED MODEL ===")
    
    try:
        # Load the model and vectorizer
        model = joblib.load("models/saved_models/email_classifier.pkl")
        vectorizer = joblib.load("models/saved_models/email_vectorizer.pkl")
        print("✓ Models loaded successfully")
        
        # Test samples (you know these are phishing/safe)
        test_samples = {
            "OBVIOUS PHISHING": "Urgent! Your account will be suspended! Click here immediately to verify your password and save your account: http://fake-bank.com/verify",
            "OBVIOUS SAFE": "Hi, hope you're doing well. Let's meet for coffee tomorrow at 3pm. Looking forward to catching up!"
        }
        
        print("\n=== TESTING KNOWN SAMPLES ===")
        for label, text in test_samples.items():
            # Preprocess (you might need to adjust this based on your preprocessing)
            processed_text = text.lower().strip()  # Basic preprocessing
            
            # Transform and predict
            text_features = vectorizer.transform([processed_text])
            prediction = model.predict(text_features)[0]
            probabilities = model.predict_proba(text_features)[0]
            
            print(f"\nText: {text[:80]}...")
            print(f"Expected: {label}")
            print(f"Model output: {prediction}")
            print(f"Probabilities: {probabilities}")
            print(f"Max probability: {np.max(probabilities)}")
            
            # Show what each class means
            if hasattr(model, 'classes_'):
                print(f"Model classes: {model.classes_}")
                for i, prob in enumerate(probabilities):
                    print(f"  Class {i}: {prob:.4f}")
    
    except FileNotFoundError:
        print("Saved model files not found!")
    except Exception as e:
        print(f"Error loading model: {e}")

def suggest_fix():
    """Suggest the correct fix based on findings"""
    print("\n=== SUGGESTED FIXES ===")
    
    print("""
    Based on the debug output above:
    
    1. CHECK YOUR TRAINING DATA:
       - Look at the original label values and their encoded numbers
       - Note which number corresponds to 'Phishing' and which to 'Safe'
    
    2. COMMON PATTERNS:
       - If LabelEncoder was used: alphabetical order applies
         'Phishing' comes before 'Safe' -> Phishing=0, Safe=1
         OR 'Safe' comes before 'Phishing' -> Safe=0, Phishing=1
    
    3. CORRECT THE PREDICTION MAPPING:
       In prediction_service.py, use the CORRECT mapping:
       
       # If Phishing=0 and Safe=1:
       prediction = "Phishing" if prediction_num == 0 else "Safe"
       
       # If Phishing=1 and Safe=0:
       prediction = "Phishing" if prediction_num == 1 else "Safe"
    
    4. TEST WITH KNOWN SAMPLES:
       - Use obviously phishing emails to verify the mapping
       - Use obviously safe emails to double-check
    """)

if __name__ == "__main__":
    check_training_data_labels()
    check_saved_model()
    suggest_fix()