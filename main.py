from flask import Flask, render_template, request, jsonify
from services.prediction_service import PredictionService
from utils.logger import setup_logger
import os

app = Flask(__name__)
logger = setup_logger(__name__)

# Initialize prediction service
prediction_service = PredictionService()
prediction_service.load_models()  # Make sure to load models

@app.route('/')
def index():
    """Main web interface"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        text = data.get('text', '').strip()
        content_type = data.get('type', '').strip().lower()
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'Text content is required'
            }), 400
        
        if content_type not in ['email', 'url']:
            return jsonify({
                'success': False,
                'error': 'Type must be either "email" or "url"'
            }), 400
        
        # FIXED: Use predict_text instead of predict
        result = prediction_service.predict_text(text, content_type)
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Prediction failed: {str(e)}'
        }), 500

@app.route('/api/v1/batch-predict', methods=['POST'])
def batch_predict():
    """Handle batch prediction requests"""
    try:
        data = request.get_json()
        items = data.get('items', [])
        
        if not items:
            return jsonify({
                'success': False,
                'error': 'No items provided'
            }), 400
        
        results = prediction_service.predict_batch(items)
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/models/status', methods=['GET'])
def model_status():
    """Get model status"""
    try:
        status = prediction_service.get_model_status()
        return jsonify({
            'success': True,
            **status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        status = prediction_service.get_model_status()
        
        if status['models_loaded']:
            return jsonify({
                'status': 'healthy',
                'models_loaded': True
            }), 200
        else:
            return jsonify({
                'status': 'unhealthy',
                'models_loaded': False
            }), 503
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)