#!/usr/bin/env python3
"""
Enterprise Legal Name Comparison System
Production-ready Flask application with monitoring, feedback loops, and automation
"""

import os
import json
import logging
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional

import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import jwt
from werkzeug.utils import secure_filename
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge

from legal_name_comparison import LegalNameComparator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS
CORS(app)

# Initialize rate limiter
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize Redis for caching
redis_client = redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'))

# Initialize PostgreSQL connection
def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        database=os.environ.get('DB_NAME', 'legal_name_comparison'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'password'),
        cursor_factory=RealDictCursor
    )

# Initialize ML model
comparator = None

# Prometheus metrics
REQUEST_COUNT = Counter('requests_total', 'Total requests', ['endpoint', 'method'])
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')
PREDICTION_COUNT = Counter('predictions_total', 'Total predictions', ['model_version'])
PREDICTION_ACCURACY = Gauge('prediction_accuracy', 'Model accuracy')
CPU_USAGE = Gauge('cpu_usage_percent', 'CPU usage')
MEMORY_USAGE = Gauge('memory_usage_percent', 'Memory usage')

# Authentication decorator
def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        token = token.replace('Bearer ', '')
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# Metrics decorator
def track_metrics(endpoint):
    """Decorator to track request metrics"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time
                
                REQUEST_COUNT.labels(endpoint=endpoint, method=request.method).inc()
                REQUEST_DURATION.observe(duration)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                REQUEST_DURATION.observe(duration)
                raise e
        
        return decorated_function
    return decorator

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        conn = get_db_connection()
        conn.close()
        
        # Check Redis connection
        redis_client.ping()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Ready check endpoint
@app.route('/ready')
def ready_check():
    """Ready check endpoint for Kubernetes"""
    return jsonify({'status': 'ready'})

# Metrics endpoint for Prometheus
@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return prometheus_client.generate_latest()

# Authentication endpoints
@app.route('/auth/login', methods=['POST'])
@track_metrics('auth_login')
def login():
    """User login endpoint"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # In production, use proper password hashing
        cursor.execute(
            "SELECT id, email, name, role FROM users WHERE email = %s AND password = %s",
            (email, password)  # Use proper password hashing in production
        )
        user = cursor.fetchone()
        
        if user:
            token = jwt.encode(
                {
                    'user_id': str(user['id']),
                    'email': user['email'],
                    'role': user['role'],
                    'exp': datetime.utcnow() + timedelta(hours=24)
                },
                app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            
            return jsonify({
                'token': token,
                'user': {
                    'id': str(user['id']),
                    'email': user['email'],
                    'name': user['name'],
                    'role': user['role']
                }
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Main application endpoints
@app.route('/')
def index():
    """Serve the main application"""
    return send_file('templates/index.html')

@app.route('/api/upload', methods=['POST'])
@require_auth
@limiter.limit("10 per minute")
@track_metrics('upload')
def upload_file():
    """Handle file upload and model training"""
    global comparator
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'error': 'Invalid file type. Please upload Excel file'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read Excel file
        df = pd.read_excel(filepath)
        logger.info(f"Processing file: {filename}, Shape: {df.shape}")
        
        # Validate required columns
        required_columns = ['source1', 'source2', 'source3', 'is_material']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return jsonify({
                'error': f'Missing required columns: {", ".join(missing_columns)}'
            }), 400
        
        # Initialize comparator and train model
        comparator = LegalNameComparator()
        X, y = comparator.create_training_data(df)
        
        if len(X) == 0:
            return jsonify({'error': 'No valid data pairs found'}), 400
        
        # Train model
        accuracy = comparator.train_model(X, y)
        
        # Save model to database
        model_id = save_model_to_db(comparator, accuracy, request.user['user_id'])
        
        # Log prediction metrics
        PREDICTION_ACCURACY.set(accuracy)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': f'Model trained successfully with {len(X)} data pairs',
            'accuracy': round(accuracy, 4),
            'model_id': str(model_id)
        })
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/api/predict', methods=['POST'])
@require_auth
@limiter.limit("100 per minute")
@track_metrics('predict')
def predict():
    """Handle prediction requests"""
    global comparator
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read Excel file
        df = pd.read_excel(filepath)
        
        # Validate required columns
        required_columns = ['name1', 'name2']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return jsonify({
                'error': f'Missing required columns: {", ".join(missing_columns)}'
            }), 400
        
        if comparator is None:
            return jsonify({'error': 'No trained model available. Please train a model first.'}), 400
        
        # Make predictions
        results = []
        for _, row in df.iterrows():
            name1 = str(row['name1'])
            name2 = str(row['name2'])
            
            prediction, probabilities = comparator.predict_materiality(name1, name2)
            
            result = {
                'name1': name1,
                'name2': name2,
                'prediction': 'Material' if prediction else 'Immaterial',
                'is_material': prediction,
                'materiality_probability': float(probabilities[1]),
                'immateriality_probability': float(probabilities[0])
            }
            results.append(result)
        
        # Save predictions to database
        save_predictions_to_db(results, request.user['user_id'])
        
        # Update metrics
        PREDICTION_COUNT.labels(model_version='latest').inc()
        
        # Generate summary
        total_predictions = len(results)
        material_count = sum(1 for r in results if r['is_material'])
        immaterial_count = total_predictions - material_count
        material_percentage = (material_count / total_predictions * 100) if total_predictions > 0 else 0
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'results': results,
            'summary': {
                'total_predictions': total_predictions,
                'material_count': material_count,
                'immaterial_count': immaterial_count,
                'material_percentage': round(material_percentage, 2)
            }
        })
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': f'Error processing predictions: {str(e)}'}), 500

@app.route('/api/feedback', methods=['POST'])
@require_auth
@track_metrics('feedback')
def submit_feedback():
    """Submit feedback on predictions"""
    try:
        data = request.get_json()
        prediction_id = data.get('prediction_id')
        user_correction = data.get('user_correction')
        confidence_score = data.get('confidence_score', 0.0)
        feedback_text = data.get('feedback_text', '')
        
        if not prediction_id or user_correction is None:
            return jsonify({'error': 'Prediction ID and user correction required'}), 400
        
        # Save feedback to database
        feedback_id = save_feedback_to_db(
            prediction_id, user_correction, confidence_score, feedback_text, request.user['user_id']
        )
        
        return jsonify({
            'success': True,
            'feedback_id': str(feedback_id),
            'message': 'Feedback submitted successfully'
        })
    
    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        return jsonify({'error': f'Error submitting feedback: {str(e)}'}), 500

@app.route('/api/analytics/daily', methods=['GET'])
@require_auth
@track_metrics('analytics_daily')
def get_daily_analytics():
    """Get daily analytics"""
    try:
        days = int(request.args.get('days', 30))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            DATE(created_at) as date,
            COUNT(*) as total_predictions,
            AVG(confidence) as avg_confidence,
            COUNT(CASE WHEN prediction = true THEN 1 END) as material_count,
            COUNT(CASE WHEN prediction = false THEN 1 END) as immaterial_count
        FROM predictions 
        WHERE created_at >= NOW() - INTERVAL '%s days'
        GROUP BY DATE(created_at)
        ORDER BY date
        """ % days
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'data': [dict(row) for row in results]
        })
    
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        return jsonify({'error': f'Error fetching analytics: {str(e)}'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Database helper functions
def save_model_to_db(comparator, accuracy, user_id):
    """Save model to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Save model file
        model_path = f"models/model_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pkl"
        os.makedirs('models', exist_ok=True)
        comparator.save_model(model_path)
        
        # Save to database
        cursor.execute("""
            INSERT INTO models (name, version, model_path, accuracy, created_at, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            'legal_name_comparison',
            datetime.utcnow().strftime('%Y%m%d_%H%M%S'),
            model_path,
            accuracy,
            datetime.utcnow(),
            True
        ))
        
        model_id = cursor.fetchone()['id']
        conn.commit()
        
        return model_id
    
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def save_predictions_to_db(results, user_id):
    """Save predictions to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for result in results:
            cursor.execute("""
                INSERT INTO predictions (user_id, name1, name2, prediction, confidence)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                user_id,
                result['name1'],
                result['name2'],
                result['is_material'],
                result['materiality_probability']
            ))
        
        conn.commit()
    
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def save_feedback_to_db(prediction_id, user_correction, confidence_score, feedback_text, user_id):
    """Save feedback to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO feedback (prediction_id, user_correction, confidence_score, feedback_text)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (prediction_id, user_correction, confidence_score, feedback_text))
        
        feedback_id = cursor.fetchone()['id']
        conn.commit()
        
        return feedback_id
    
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# System metrics update
def update_system_metrics():
    """Update system metrics"""
    import psutil
    
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.virtual_memory().percent)

# Schedule metrics update
@app.before_request
def before_request():
    """Update system metrics before each request"""
    update_system_metrics()

if __name__ == '__main__':
    # Create uploads directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Run the application
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port) 