import unittest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from services.prediction_service import PredictionService

class APITestCase(unittest.TestCase):
    """Test cases for API endpoints"""
    
    def setUp(self):
        """Set up test client and mock services"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Mock prediction service
        self.mock_prediction_service = MagicMock(spec=PredictionService)
    
    def test_index_route(self):
        """Test main index route"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Phishing Detection System', response.data)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
    
    @patch('main.prediction_service')
    def test_predict_email_success(self, mock_service):
        """Test successful email prediction"""
        # Mock prediction response
        mock_service.predict.return_value = {
            'prediction': 'Safe',
            'confidence': 0.85,
            'risk_level': 'Low'
        }
        
        payload = {
            'text': 'This is a legitimate email content for testing purposes.',
            'type': 'email'
        }
        
        response = self.client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['prediction'], 'Safe')
        self.assertEqual(data['confidence'], 0.85)
        self.assertEqual(data['risk_level'], 'Low')
    
    @patch('main.prediction_service')
    def test_predict_url_success(self, mock_service):
        """Test successful URL prediction"""
        mock_service.predict.return_value = {
            'prediction': 'Phishing',
            'confidence': 0.92,
            'risk_level': 'High'
        }
        
        payload = {
            'text': 'http://suspicious-site.com/login',
            'type': 'url'
        }
        
        response = self.client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['prediction'], 'Phishing')
        self.assertEqual(data['confidence'], 0.92)
        self.assertEqual(data['risk_level'], 'High')
    
    def test_predict_missing_text(self):
        """Test prediction with missing text field"""
        payload = {
            'type': 'email'
        }
        
        response = self.client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Text field is required', data['error'])
    
    def test_predict_invalid_type(self):
        """Test prediction with invalid detection type"""
        payload = {
            'text': 'Some content',
            'type': 'invalid_type'
        }
        
        response = self.client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Type must be one of', data['error'])
    
    def test_predict_empty_text(self):
        """Test prediction with empty text"""
        payload = {
            'text': '',
            'type': 'email'
        }
        
        response = self.client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('cannot be empty', data['error'])
    
    def test_predict_too_long_text(self):
        """Test prediction with text that exceeds length limit"""
        payload = {
            'text': 'x' * 10001,  # Exceeds 10,000 character limit
            'type': 'email'
        }
        
        response = self.client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('too long', data['error'])
    
    def test_predict_invalid_json(self):
        """Test prediction with invalid JSON"""
        response = self.client.post(
            '/predict',
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_predict_missing_content_type(self):
        """Test prediction without content type header"""
        payload = {
            'text': 'Some content',
            'type': 'email'
        }
        
        response = self.client.post(
            '/predict',
            data=json.dumps(payload)
        )
        
        # Should still work but may behave differently
        self.assertIn(response.status_code, [200, 400])
    
    @patch('main.prediction_service')
    def test_predict_service_error(self, mock_service):
        """Test prediction when service throws error"""
        mock_service.predict.side_effect = Exception("Service error")
        
        payload = {
            'text': 'Test content',
            'type': 'email'
        }
        
        response = self.client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 500)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Internal server error')

class SecurityTestCase(unittest.TestCase):
    """Security-focused test cases"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_xss_protection(self):
        """Test XSS protection in input validation"""
        malicious_payload = {
            'text': '<script>alert("xss")</script>',
            'type': 'email'
        }
        
        response = self.client.post(
            '/predict',
            data=json.dumps(malicious_payload),
            content_type='application/json'
        )
        
        # Should either process safely or reject
        self.assertIn(response.status_code, [200, 400])
    
    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        malicious_payload = {
            'text': "'; DROP TABLE users; --",
            'type': 'email'
        }
        
        response = self.client.post(
            '/predict',
            data=json.dumps(malicious_payload),
            content_type='application/json'
        )
        
        # Should process safely
        self.assertIn(response.status_code, [200, 400])
    
    def test_oversized_request(self):
        """Test protection against oversized requests"""
        large_text = 'A' * 20000  # Very large text
        
        payload = {
            'text': large_text,
            'type': 'email'
        }
        
        response = self.client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()