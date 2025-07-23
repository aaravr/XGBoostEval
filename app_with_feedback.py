#!/usr/bin/env python3
"""
Legal Name Comparison System with Feedback Loop
Simplified version with basic feedback collection and model retraining
"""

import os
import json
import logging
import time
from datetime import datetime
from functools import wraps
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
import sqlite3
import pickle
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

from legal_name_comparison import LegalNameComparator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MODEL_FOLDER'] = 'models'

# Authentication configuration
app.config['ADMIN_USERNAME'] = os.environ.get('ADMIN_USERNAME', 'admin')
app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', 'admin123')  # Change in production
app.config['SESSION_TIMEOUT'] = 3600  # 1 hour

# Organization branding placeholders
app.config['ORG_NAME'] = os.environ.get('ORG_NAME', 'Your Organization')
app.config['ORG_LOGO'] = os.environ.get('ORG_LOGO', '/static/images/logo.png')
app.config['ORG_BACKGROUND'] = os.environ.get('ORG_BACKGROUND', '/static/images/background.jpg')
app.config['ORG_PRIMARY_COLOR'] = os.environ.get('ORG_PRIMARY_COLOR', '#007bff')
app.config['ORG_SECONDARY_COLOR'] = os.environ.get('ORG_SECONDARY_COLOR', '#6c757d')

# Azure AD configuration placeholders
app.config['AZURE_CLIENT_ID'] = os.environ.get('AZURE_CLIENT_ID', 'your-azure-client-id')
app.config['AZURE_CLIENT_SECRET'] = os.environ.get('AZURE_CLIENT_SECRET', 'your-azure-client-secret')
app.config['AZURE_TENANT_ID'] = os.environ.get('AZURE_TENANT_ID', 'your-azure-tenant-id')
app.config['AZURE_REDIRECT_URI'] = os.environ.get('AZURE_REDIRECT_URI', 'http://localhost:5001/auth/callback')

# Enable CORS
CORS(app)

# Initialize ML model
comparator = None

# Database setup
def init_db():
    """Initialize SQLite database for feedback"""
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    
    # Create feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_id TEXT,
            name1 TEXT NOT NULL,
            name2 TEXT NOT NULL,
            original_prediction BOOLEAN NOT NULL,
            user_correction BOOLEAN NOT NULL,
            confidence_score REAL,
            feedback_text TEXT,
            processed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create model versions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL,
            accuracy REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT FALSE
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect('feedback.db')

# Feedback collection
def save_feedback(name1, name2, original_prediction, user_correction, confidence_score, feedback_text=""):
    """Save user feedback to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO feedback (name1, name2, original_prediction, user_correction, confidence_score, feedback_text)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name1, name2, original_prediction, user_correction, confidence_score, feedback_text))
    
    feedback_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return feedback_id

def get_unprocessed_feedback(limit=100):
    """Get unprocessed feedback for retraining"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT name1, name2, original_prediction, user_correction, confidence_score
        FROM feedback 
        WHERE processed = FALSE
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    
    feedback = cursor.fetchall()
    conn.close()
    
    return feedback

def mark_feedback_processed(feedback_ids):
    """Mark feedback as processed"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for feedback_id in feedback_ids:
        cursor.execute('UPDATE feedback SET processed = TRUE WHERE id = ?', (feedback_id,))
    
    conn.commit()
    conn.close()

def save_model_version(accuracy):
    """Save model version information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Deactivate previous model
    cursor.execute('UPDATE model_versions SET is_active = FALSE')
    
    # Save new model version
    version = datetime.now().strftime('%Y%m%d_%H%M%S')
    cursor.execute('''
        INSERT INTO model_versions (version, accuracy, is_active)
        VALUES (?, ?, TRUE)
    ''', (version, accuracy))
    
    model_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return model_id

# Retraining logic
def should_retrain_model():
    """Check if model should be retrained based on feedback"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Count unprocessed feedback
    cursor.execute('SELECT COUNT(*) FROM feedback WHERE processed = FALSE')
    unprocessed_count = cursor.fetchone()[0]
    
    # Count total feedback
    cursor.execute('SELECT COUNT(*) FROM feedback')
    total_feedback = cursor.fetchone()[0]
    
    conn.close()
    
    logger.info(f"Feedback check: {unprocessed_count} unprocessed, {total_feedback} total")
    
    # Retrain if we have enough new feedback (10+ new feedback items)
    return unprocessed_count >= 10

def retrain_model_with_feedback():
    """Retrain model using feedback data"""
    global comparator
    
    try:
        logger.info("Starting retrain_model_with_feedback")
        
        # Check if we should retrain
        if not should_retrain_model():
            logger.info("Not enough feedback for retraining. Need 10+ unprocessed items")
            return False
        
        # Get unprocessed feedback
        feedback_data = get_unprocessed_feedback()
        
        # Create training data from feedback
        training_data = []
        for name1, name2, original_prediction, user_correction, confidence in feedback_data:
            # Use user correction as the true label
            training_data.append({
                'source1': name1,
                'source2': name2,
                'source3': '',  # Empty for feedback data
                'is_material': user_correction
            })
        
        # Convert to DataFrame
        df = pd.DataFrame(training_data)
        
        # Initialize new comparator
        new_comparator = LegalNameComparator()
        X, y = new_comparator.create_training_data(df)
        
        if len(X) == 0:
            logger.warning("No valid training data from feedback")
            return False
        
        # Train new model
        accuracy = new_comparator.train_model(X, y)
        
        # Save new model
        model_path = f"models/model_feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        os.makedirs('models', exist_ok=True)
        new_comparator.save_model(model_path)
        
        # Update global comparator
        comparator = new_comparator
        
        # Save model version
        save_model_version(accuracy)
        
        # Mark feedback as processed
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE feedback SET processed = TRUE WHERE processed = FALSE')
        conn.commit()
        conn.close()
        
        logger.info(f"Model retrained with {len(feedback_data)} feedback items. New accuracy: {accuracy:.4f}")
        return True
        
    except Exception as e:
        logger.error(f"Error retraining model: {str(e)}")
        return False

def login_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def init_auth_db():
    """Initialize authentication database"""
    conn = sqlite3.connect('auth.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create default admin user if not exists
    cursor.execute('SELECT * FROM users WHERE username = ?', (app.config['ADMIN_USERNAME'],))
    if not cursor.fetchone():
        password_hash = generate_password_hash(app.config['ADMIN_PASSWORD'])
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
        ''', (app.config['ADMIN_USERNAME'], password_hash, 'admin@example.com', 'admin'))
    
    conn.commit()
    conn.close()

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        conn = get_db_connection()
        conn.close()
        
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and authentication"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect('auth.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[4]
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/auth/azure')
def azure_auth():
    """Azure AD authentication endpoint (placeholder)"""
    # TODO: Implement Azure AD authentication
    # This would typically redirect to Azure AD login
    return jsonify({'message': 'Azure AD authentication not implemented yet'})

@app.route('/auth/callback')
def azure_callback():
    """Azure AD callback endpoint (placeholder)"""
    # TODO: Handle Azure AD callback and token exchange
    return jsonify({'message': 'Azure AD callback not implemented yet'})

# Main application endpoints
@app.route('/')
@login_required
def index():
    """Main application page"""
    return render_template('index_with_feedback.html', 
                         org_name=app.config['ORG_NAME'],
                         org_logo=app.config['ORG_LOGO'],
                         org_background=app.config['ORG_BACKGROUND'],
                         org_primary_color=app.config['ORG_PRIMARY_COLOR'],
                         org_secondary_color=app.config['ORG_SECONDARY_COLOR'])

@app.route('/upload', methods=['POST'])
@login_required
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
        
        # Save model version
        save_model_version(accuracy)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': f'Model trained successfully with {len(X)} data pairs',
            'accuracy': round(accuracy, 4)
        })
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/predict', methods=['POST'])
@login_required
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
        
        # Get column names or indices for accessing data
        # Handle both column names and integer indices
        try:
            # Try to access by column names first
            name1_col = 'name1'
            name2_col = 'name2'
            
            # Test if columns exist by name
            _ = df[name1_col].iloc[0]
        except (KeyError, IndexError):
            # If column names don't work, use integer indices
            # Assuming standard order: name1, name2
            name1_col = 0
            name2_col = 1
        
        for _, row in df.iterrows():
            name1 = str(row[name1_col])
            name2 = str(row[name2_col])
            
            prediction, probabilities = comparator.predict_materiality(name1, name2)
            
            result = {
                'name1': name1,
                'name2': name2,
                'prediction': 'Material' if prediction else 'Immaterial',
                'is_material': prediction,
                'materiality_probability': float(probabilities[1]),
                'immateriality_probability': float(probabilities[0]),
                'prediction_id': f"{name1}_{name2}_{int(time.time())}"  # Simple ID generation
            }
            results.append(result)
        
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

@app.route('/test_prediction', methods=['POST'])
@login_required
def test_prediction():
    """Handle single name pair prediction for manual evaluation"""
    global comparator
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        name1 = data.get('name1')
        name2 = data.get('name2')
        
        if not name1 or not name2:
            return jsonify({'error': 'Both name1 and name2 are required'}), 400
        
        if comparator is None:
            return jsonify({'error': 'No trained model available. Please train a model first.'}), 400
        
        # Make prediction
        prediction, probabilities = comparator.predict_materiality(name1, name2)
        
        result = {
            'name1': name1,
            'name2': name2,
            'prediction': 'Material' if prediction else 'Immaterial',
            'is_material': prediction,
            'materiality_probability': float(probabilities[1]),
            'immateriality_probability': float(probabilities[0]),
            'prediction_id': f"{name1}_{name2}_{int(time.time())}"
        }
        
        return jsonify({
            'success': True,
            'result': result
        })
    
    except Exception as e:
        logger.error(f"Test prediction error: {str(e)}")
        return jsonify({'error': f'Error making test prediction: {str(e)}'}), 500

@app.route('/feedback', methods=['POST'])
@login_required
def submit_feedback():
    """Submit feedback on predictions"""
    try:
        data = request.get_json()
        name1 = data.get('name1')
        name2 = data.get('name2')
        original_prediction = data.get('original_prediction')
        user_correction = data.get('user_correction')
        confidence_score = data.get('confidence_score', 0.0)
        feedback_text = data.get('feedback_text', '')
        
        if not all([name1, name2, original_prediction is not None, user_correction is not None]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Save feedback
        feedback_id = save_feedback(
            name1, name2, original_prediction, user_correction, confidence_score, feedback_text
        )
        
        # Check if we should retrain
        if should_retrain_model():
            logger.info("Triggering model retraining due to sufficient feedback")
            retrain_success = retrain_model_with_feedback()
            
            return jsonify({
                'success': True,
                'feedback_id': feedback_id,
                'message': 'Feedback submitted successfully',
                'model_retrained': retrain_success
            })
        
        return jsonify({
            'success': True,
            'feedback_id': feedback_id,
            'message': 'Feedback submitted successfully'
        })
    
    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        return jsonify({'error': f'Error submitting feedback: {str(e)}'}), 500

@app.route('/feedback/stats', methods=['GET'])
@login_required
def get_feedback_stats():
    """Get feedback statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total feedback count
        cursor.execute('SELECT COUNT(*) FROM feedback')
        total_feedback = cursor.fetchone()[0]
        
        # Get unprocessed feedback count
        cursor.execute('SELECT COUNT(*) FROM feedback WHERE processed = FALSE')
        unprocessed_feedback = cursor.fetchone()[0]
        
        # Get feedback accuracy (how often user corrections differ from original predictions)
        cursor.execute('''
            SELECT COUNT(*) FROM feedback 
            WHERE original_prediction != user_correction
        ''')
        corrections_count = cursor.fetchone()[0]
        
        correction_rate = (corrections_count / total_feedback * 100) if total_feedback > 0 else 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_feedback': total_feedback,
                'unprocessed_feedback': unprocessed_feedback,
                'corrections_count': corrections_count,
                'correction_rate': round(correction_rate, 2)
            }
        })
    
    except Exception as e:
        logger.error(f"Feedback stats error: {str(e)}")
        return jsonify({'error': f'Error fetching feedback stats: {str(e)}'}), 500

@app.route('/model/retrain', methods=['POST'])
@login_required
def manual_retrain():
    """Manually trigger model retraining"""
    try:
        logger.info("Manual retrain requested")
        success = retrain_model_with_feedback()
        logger.info(f"Manual retrain result: {success}")
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Model retrained successfully with feedback data'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Not enough feedback data for retraining (need 10+ items)'
            })
    
    except Exception as e:
        logger.error(f"Manual retrain error: {str(e)}")
        return jsonify({'error': f'Error retraining model: {str(e)}'}), 500

@app.route('/debug/retrain', methods=['GET'])
@login_required
def debug_retrain():
    """Debug endpoint to check retraining logic"""
    try:
        should_retrain = should_retrain_model()
        feedback_data = get_unprocessed_feedback()
        
        return jsonify({
            'should_retrain': should_retrain,
            'feedback_count': len(feedback_data),
            'feedback_sample': feedback_data[:3] if feedback_data else []
        })
    
    except Exception as e:
        logger.error(f"Debug retrain error: {str(e)}")
        return jsonify({'error': f'Debug error: {str(e)}'}), 500

@app.route('/model/versions', methods=['GET'])
@login_required
def get_model_versions():
    """Get model version history"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT version, accuracy, created_at, is_active
            FROM model_versions
            ORDER BY created_at DESC
        ''')
        
        versions = []
        for row in cursor.fetchall():
            versions.append({
                'version': row[0],
                'accuracy': row[1],
                'created_at': row[2],
                'is_active': bool(row[3])
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'versions': versions
        })
    
    except Exception as e:
        logger.error(f"Model versions error: {str(e)}")
        return jsonify({'error': f'Error fetching model versions: {str(e)}'}), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    init_auth_db() # Initialize authentication database
    
    # Create uploads directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['MODEL_FOLDER'], exist_ok=True) # Ensure models directory exists
    
    # Run the application
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port) 