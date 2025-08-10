from flask import Blueprint, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from services.prediction_service import PredictionService
from utils.validators import InputValidator
from utils.logger import setup_logger, SecurityLogger
from config.settings import API_CONFIG

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Initialize components
logger = setup_logger(__name__)
security_logger = SecurityLogger()
limiter = Limiter(key_func=get_remote_address)

# Initialize prediction service
try:
    prediction_service = PredictionService()
except Exception as e:
    logger.error(f"Failed to initialize prediction service: {str(e)}")
    prediction_service = None

@api_bp.route('/predict', methods=['POST'])
@limiter.limit(API_CONFIG['rate_limits']['predict'])
def api_predict():
    """API endpoint for single prediction"""
    try:
        # Log request
        client_ip = get_remote_address()
        logger.info(f"Prediction request from {client_ip}")
        
        if not prediction_service:
            return jsonify({
                'success': False,
                'error': 'Prediction service unavailable'
            }), 503
        
        # Get and validate input
        data = request.get_json()
        validation_result = InputValidator.validate_prediction_input(data)
        
        if not validation_result['is_valid']:
            security_logger.log_suspicious_activity(
                'Invalid input attempt',
                {'ip': client_ip, 'error': validation_result['error']}
            )
            return jsonify({
                'success': False,
                'error': validation_result['error']
            }), 400
        
        # Make prediction
        result = prediction_service.predict(
            text=data['text'],
            detection_type=data['type']
        )
        
        # Log prediction for audit
        security_logger.log_model_prediction(
            data['type'],
            result['prediction'],
            result['confidence']
        )
        
        return jsonify({
            'success': True,
            'data': {
                'prediction': result['prediction'],
                'confidence': round(result['confidence'], 4),
                'risk_level': result['risk_level'],
                'detection_type': data['type']
            },
            'metadata': {
                'timestamp': logger.handlers[0].formatter.formatTime(
                    logger.makeRecord('', 0, '', 0, '', (), None)
                ),
                'version': API_CONFIG['version']
            }
        })
        
    except Exception as e:
        logger.error(f"API prediction error: {str(e)}")
        security_logger.log_potential_attack(
            'API Error',
            client_ip,
            {'error': str(e)}
        )
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@api_bp.route('/batch-predict', methods=['POST'])
@limiter.limit(API_CONFIG['rate_limits']['batch_predict'])
def api_batch_predict():
    """API endpoint for batch predictions"""
    try:
        client_ip = get_remote_address()
        logger.info(f"Batch prediction request from {client_ip}")
        
        if not prediction_service:
            return jsonify({
                'success': False,
                'error': 'Prediction service unavailable'
            }), 503
        
        data = request.get_json()
        
        # Validate batch input
        if not data or 'items' not in data:
            return jsonify({
                'success': False,
                'error': 'Items array is required for batch prediction'
            }), 400
        
        items = data['items']
        if not isinstance(items, list) or len(items) == 0:
            return jsonify({
                'success': False,
                'error': 'Items must be a non-empty array'
            }), 400
        
        if len(items) > 50:  # Limit batch size
            return jsonify({
                'success': False,
                'error': 'Batch size cannot exceed 50 items'
            }), 400
        
        # Process each item
        results = []
        for i, item in enumerate(items):
            try:
                validation_result = InputValidator.validate_prediction_input(item)
                if not validation_result['is_valid']:
                    results.append({
                        'index': i,
                        'success': False,
                        'error': validation_result['error']
                    })
                    continue
                
                prediction_result = prediction_service.predict(
                    text=item['text'],
                    detection_type=item['type']
                )
                
                results.append({
                    'index': i,
                    'success': True,
                    'data': {
                        'prediction': prediction_result['prediction'],
                        'confidence': round(prediction_result['confidence'], 4),
                        'risk_level': prediction_result['risk_level'],
                        'detection_type': item['type']
                    }
                })
                
            except Exception as e:
                logger.error(f"Error processing batch item {i}: {str(e)}")
                results.append({
                    'index': i,
                    'success': False,
                    'error': 'Processing error'
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'metadata': {
                'total_items': len(items),
                'successful_predictions': len([r for r in results if r['success']]),
                'version': API_CONFIG['version']
            }
        })
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@api_bp.route('/models/status', methods=['GET'])
def api_model_status():
    """Get model status information"""
    try:
        if not prediction_service:
            return jsonify({
                'success': False,
                'error': 'Prediction service unavailable'
            }), 503
        
        status = prediction_service.get_model_info()
        
        return jsonify({
            'success': True,
            'data': status,
            'metadata': {
                'version': API_CONFIG['version']
            }
        })
        
    except Exception as e:
        logger.error(f"Model status error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Unable to retrieve model status'
        }), 500

@api_bp.route('/health', methods=['GET'])
def api_health():
    """Health check endpoint"""
    try:
        health_status = {
            'status': 'healthy',
            'models_loaded': prediction_service is not None,
            'version': API_CONFIG['version']
        }
        
        if prediction_service:
            model_info = prediction_service.get_model_info()
            health_status['models_ready'] = model_info['models_ready']
        
        return jsonify(health_status), 200
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': 'Health check failed'
        }), 500

@api_bp.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded"""
    client_ip = get_remote_address()
    security_logger.log_suspicious_activity(
        'Rate limit exceeded',
        {'ip': client_ip, 'limit': str(e.description)}
    )
    
    return jsonify({
        'success': False,
        'error': 'Rate limit exceeded. Please try again later.',
        'retry_after': e.retry_after
    }), 429

@api_bp.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@api_bp.errorhandler(405)
def method_not_allowed(e):
    """Handle method not allowed errors"""
    return jsonify({
        'success': False,
        'error': 'Method not allowed'
    }), 405

@api_bp.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500