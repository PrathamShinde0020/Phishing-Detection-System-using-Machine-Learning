import re
import string
from typing import List, Optional
from utils.logger import setup_logger

class TextPreprocessor:
    """Text preprocessing utilities for email and URL text processing"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
    
    def preprocess_email(self, text: str) -> str:
        """
        Preprocess email text for classification
        
        Args:
            text: Raw email text
            
        Returns:
            Preprocessed email text
        """
        try:
            if not text or not isinstance(text, str):
                return ""
            
            # Remove hyperlinks
            text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
            
            # Remove email addresses
            text = re.sub(r'\S+@\S+', '', text)
            
            # Remove phone numbers
            text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '', text)
            
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', text)
            
            # Remove extra whitespace and newlines
            text = re.sub(r'\s+', ' ', text)
            
            # Convert to lowercase
            text = text.lower()
            
            # Remove punctuation
            text = text.translate(str.maketrans('', '', string.punctuation))
            
            # Remove numbers
            text = re.sub(r'\d+', '', text)
            
            # Strip leading/trailing whitespace
            text = text.strip()
            
            return text
            
        except Exception as e:
            self.logger.error(f"Error preprocessing email text: {str(e)}")
            return ""
    
    def preprocess_url(self, url: str) -> str:
        """
        Preprocess URL for feature extraction
        
        Args:
            url: Raw URL string
            
        Returns:
            Cleaned URL string
        """
        try:
            if not url or not isinstance(url, str):
                return ""
            
            # Remove leading/trailing whitespace
            url = url.strip()
            
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            
            # Convert to lowercase
            url = url.lower()
            
            return url
            
        except Exception as e:
            self.logger.error(f"Error preprocessing URL: {str(e)}")
            return ""
    
    def extract_words(self, text: str, min_length: int = 2) -> List[str]:
        """
        Extract words from text with minimum length filter
        
        Args:
            text: Input text
            min_length: Minimum word length
            
        Returns:
            List of extracted words
        """
        try:
            if not text:
                return []
            
            # Split into words and filter by length
            words = [
                word.strip() for word in text.split() 
                if len(word.strip()) >= min_length
            ]
            
            return words
            
        except Exception as e:
            self.logger.error(f"Error extracting words: {str(e)}")
            return []
    
    def remove_stop_words(self, text: str, stop_words: Optional[List[str]] = None) -> str:
        """
        Remove stop words from text
        
        Args:
            text: Input text
            stop_words: List of stop words to remove
            
        Returns:
            Text with stop words removed
        """
        try:
            if not text:
                return ""
            
            if stop_words is None:
                # Basic English stop words
                stop_words = [
                    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'been', 'by',
                    'for', 'from', 'has', 'he', 'in', 'is', 'it', 'its', 'of',
                    'on', 'that', 'the', 'to', 'was', 'will', 'with', 'you',
                    'your', 'yours', 'this', 'they', 'them', 'their'
                ]
            
            words = text.split()
            filtered_words = [word for word in words if word.lower() not in stop_words]
            
            return ' '.join(filtered_words)
            
        except Exception as e:
            self.logger.error(f"Error removing stop words: {str(e)}")
            return text
    
    def clean_special_characters(self, text: str, keep_patterns: Optional[List[str]] = None) -> str:
        """
        Clean special characters from text with option to keep specific patterns
        
        Args:
            text: Input text
            keep_patterns: List of regex patterns to preserve
            
        Returns:
            Cleaned text
        """
        try:
            if not text:
                return ""
            
            # Preserve specified patterns temporarily
            preserved = {}
            if keep_patterns:
                for i, pattern in enumerate(keep_patterns):
                    placeholder = f"__PRESERVE_{i}__"
                    matches = re.findall(pattern, text)
                    for j, match in enumerate(matches):
                        key = f"{placeholder}_{j}"
                        preserved[key] = match
                        text = text.replace(match, key, 1)
            
            # Remove special characters
            text = re.sub(r'[^\w\s]', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Restore preserved patterns
            for key, value in preserved.items():
                text = text.replace(key, value)
            
            return text
            
        except Exception as e:
            self.logger.error(f"Error cleaning special characters: {str(e)}")
            return text