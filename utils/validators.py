import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from utils.logger import setup_logger

class InputValidator:
    """Input validation utilities for the phishing detection system"""
    
    logger = setup_logger(__name__)
    
    @staticmethod
    def validate_prediction_input(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate prediction request input
        
        Args:
            data: Request data dictionary
            
        Returns:
            Validation result with is_valid flag and error message
        """
        try:
            # Check if required fields exist
            if not data:
                return {
                    'is_valid': False,
                    'error': 'Request data is required'
                }
            
            if 'text' not in data:
                return {
                    'is_valid': False,
                    'error': 'Text field is required'
                }
            
            if 'type' not in data:
                return {
                    'is_valid': False,
                    'error': 'Type field is required'
                }
            
            # Validate detection type
            valid_types = ['email', 'url']
            if data['type'] not in valid_types:
                return {
                    'is_valid': False,
                    'error': f'Type must be one of: {", ".join(valid_types)}'
                }
            
            # Validate text content
            text_validation = InputValidator._validate_text_content(
                data['text'], 
                data['type']
            )
            
            if not text_validation['is_valid']:
                return text_validation
            
            return {'is_valid': True, 'error': None}
            
        except Exception as e:
            InputValidator.logger.error(f"Error validating input: {str(e)}")
            return {
                'is_valid': False,
                'error': 'Validation error occurred'
            }
    
    @staticmethod
    def _validate_text_content(text: str, content_type: str) -> Dict[str, Any]:
        """
        Validate text content based on type
        
        Args:
            text: Text content to validate
            content_type: Type of content ('email' or 'url')
            
        Returns:
            Validation result
        """
        # Check if text is provided and is string
        if not text or not isinstance(text, str):
            return {
                'is_valid': False,
                'error': 'Text content must be a non-empty string'
            }
        
        # Remove whitespace for validation
        text = text.strip()
        
        if not text:
            return {
                'is_valid': False,
                'error': 'Text content cannot be empty'
            }
        
        # Length validation
        if len(text) > 10000:
            return {
                'is_valid': False,
                'error': 'Text content is too long (max 10,000 characters)'
            }
        
        if len(text) < 3:
            return {
                'is_valid': False,
                'error': 'Text content is too short (min 3 characters)'
            }
        
        # Type-specific validation
        if content_type == 'email':
            return InputValidator._validate_email_content(text)
        elif content_type == 'url':
            return InputValidator._validate_url_content(text)
        
        return {'is_valid': True, 'error': None}
    
    @staticmethod
    def _validate_email_content(text: str) -> Dict[str, Any]:
        """
        Validate email content
        
        Args:
            text: Email text content
            
        Returns:
            Validation result
        """
        # Basic email content validation
        if len(text.split()) < 2:
            return {
                'is_valid': False,
                'error': 'Email content must contain at least 2 words'
            }
        
        # Check for potentially malicious content patterns
        suspicious_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',                # JavaScript protocols
            r'data:text/html',            # Data URLs with HTML
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                return {
                    'is_valid': False,
                    'error': 'Email content contains potentially malicious patterns'
                }
        
        return {'is_valid': True, 'error': None}
    
    @staticmethod
    def _validate_url_content(text: str) -> Dict[str, Any]:
        """
        Validate URL content
        
        Args:
            text: URL string
            
        Returns:
            Validation result
        """
        try:
            # Basic URL format validation
            url_pattern = re.compile(
                r'^(?:http|ftp)s?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
                r'localhost|'  # localhost
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE
            )
            
            # Try to add protocol if missing
            test_url = text
            if not text.startswith(('http://', 'https://')):
                test_url = 'http://' + text
            
            # Basic format check
            if not url_pattern.match(test_url):
                # Try more lenient validation
                try:
                    parsed = urlparse(test_url)
                    if not parsed.netloc:
                        return {
                            'is_valid': False,
                            'error': 'Invalid URL format'
                        }
                except Exception:
                    return {
                        'is_valid': False,
                        'error': 'Invalid URL format'
                    }
            
            # Length check
            if len(text) > 2048:
                return {
                    'is_valid': False,
                    'error': 'URL is too long (max 2048 characters)'
                }
            
            return {'is_valid': True, 'error': None}
            
        except Exception as e:
            InputValidator.logger.error(f"Error validating URL: {str(e)}")
            return {
                'is_valid': False,
                'error': 'URL validation error'
            }
    
    @staticmethod
    def validate_file_upload(file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate file upload data
        
        Args:
            file_data: File upload data
            
        Returns:
            Validation result
        """
        try:
            if not file_data:
                return {
                    'is_valid': False,
                    'error': 'File data is required'
                }
            
            # Check file size (max 5MB)
            max_size = 5 * 1024 * 1024
            if 'size' in file_data and file_data['size'] > max_size:
                return {
                    'is_valid': False,
                    'error': 'File size exceeds 5MB limit'
                }
            
            # Check file type
            allowed_types = ['text/plain', 'text/csv', 'application/json']
            if 'type' in file_data and file_data['type'] not in allowed_types:
                return {
                    'is_valid': False,
                    'error': f'File type must be one of: {", ".join(allowed_types)}'
                }
            
            return {'is_valid': True, 'error': None}
            
        except Exception as e:
            InputValidator.logger.error(f"Error validating file upload: {str(e)}")
            return {
                'is_valid': False,
                'error': 'File validation error'
            }