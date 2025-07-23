from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
import tempfile
from werkzeug.utils import secure_filename
from legal_name_comparison import LegalNameComparator
import json
import plotly.graph_objs as go
import plotly.utils
import numpy as np

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variable to store the trained model
comparator = None

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xlsx', 'xls'}

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and process"""
    global comparator
    
    print(f"Upload request received")
    
    if 'file' not in request.files:
        print("No file in request")
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        print("Empty filename")
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        print(f"Invalid file type: {file.filename}")
        return jsonify({'error': 'Invalid file type. Please upload Excel file (.xlsx or .xls)'}), 400
    
    try:
        print(f"Processing upload for file: {file.filename}")
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        print(f"File saved to: {filepath}")
        
        # Read Excel file
        df = pd.read_excel(filepath)
        print(f"Excel file read successfully. Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Validate required columns
        required_columns = ['source1', 'source2', 'source3', 'is_material']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return jsonify({
                'error': f'Missing required columns: {", ".join(missing_columns)}. '
                        f'Please ensure your Excel file has columns: source1, source2, source3, is_material'
            }), 400
        
        # Initialize comparator and train model
        comparator = LegalNameComparator()
        X, y = comparator.create_training_data(df)
        
        if len(X) == 0:
            return jsonify({'error': 'No valid data pairs found. Please check your data.'}), 400
        
        # Train model
        accuracy = comparator.train_model(X, y)
        
        # Save model
        model_path = os.path.join(app.config['UPLOAD_FOLDER'], 'trained_model.pkl')
        comparator.save_model(model_path)
        
        # Get feature importance
        importance = comparator.get_feature_importance()
        
        # Create feature importance plot
        if importance:
            sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10]
            features, scores = zip(*sorted_importance)
            
            fig = go.Figure(data=[
                go.Bar(x=list(features), y=list(scores), marker_color='lightblue')
            ])
            fig.update_layout(
                title='Top 10 Feature Importance',
                xaxis_title='Features',
                yaxis_title='Importance Score',
                height=400
            )
            feature_plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        else:
            feature_plot = None
        
        # Clean up uploaded file
        os.remove(filepath)
        
        # Convert numpy types to Python types for JSON serialization
        if importance:
            importance_serializable = {k: float(v) for k, v in importance.items()}
        else:
            importance_serializable = {}
        
        return jsonify({
            'success': True,
            'message': f'Model trained successfully with {len(X)} data pairs',
            'accuracy': round(accuracy, 4),
            'feature_plot': feature_plot,
            'feature_importance': importance_serializable
        })
        
    except Exception as e:
        print(f"Error in upload processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/predict', methods=['POST'])
def predict():
    """Make predictions on uploaded comparison data"""
    global comparator
    
    if comparator is None:
        return jsonify({'error': 'No trained model available. Please upload training data first.'}), 400
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload Excel file (.xlsx or .xls)'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read Excel file
        df = pd.read_excel(filepath)
        
        # Validate required columns for prediction
        if 'name1' not in df.columns or 'name2' not in df.columns:
            return jsonify({
                'error': 'Missing required columns: name1, name2. '
                        f'Please ensure your Excel file has columns: name1, name2'
            }), 400
        
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
            name1 = str(row[name1_col]) if pd.notna(row[name1_col]) else ''
            name2 = str(row[name2_col]) if pd.notna(row[name2_col]) else ''
            
            if name1.strip() and name2.strip():
                prediction, probabilities = comparator.predict_materiality(name1, name2)
                results.append({
                    'name1': name1,
                    'name2': name2,
                    'is_material': prediction,
                    'materiality_probability': round(float(probabilities[1]), 4),
                    'immateriality_probability': round(float(probabilities[0]), 4),
                    'prediction': 'Material' if prediction else 'Immaterial'
                })
        
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        
        # Save results to Excel
        results_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'predictions.xlsx')
        results_df.to_excel(results_filepath, index=False)
        
        # Create summary statistics
        total_predictions = len(results)
        material_count = sum(1 for r in results if r['is_material'])
        immaterial_count = total_predictions - material_count
        
        # Create prediction distribution plot
        fig = go.Figure(data=[
            go.Pie(labels=['Material', 'Immaterial'], 
                   values=[material_count, immaterial_count],
                   marker_colors=['#ff7f0e', '#1f77b4'])
        ])
        fig.update_layout(
            title='Prediction Distribution',
            height=400
        )
        prediction_plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'results': results,
            'summary': {
                'total_predictions': total_predictions,
                'material_count': material_count,
                'immaterial_count': immaterial_count,
                'material_percentage': round(material_count / total_predictions * 100, 2) if total_predictions > 0 else 0
            },
            'prediction_plot': prediction_plot,
            'download_url': '/download_predictions'
        })
        
    except Exception as e:
        return jsonify({'error': f'Error processing predictions: {str(e)}'}), 500

@app.route('/download_predictions')
def download_predictions():
    """Download predictions Excel file"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'predictions.xlsx')
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True, attachment_filename='predictions.xlsx')
    else:
        return jsonify({'error': 'No predictions file available'}), 404

@app.route('/test_prediction', methods=['POST'])
def test_prediction():
    """Test individual prediction"""
    global comparator
    
    if comparator is None:
        return jsonify({'error': 'No trained model available. Please upload training data first.'}), 400
    
    data = request.get_json()
    name1 = data.get('name1', '')
    name2 = data.get('name2', '')
    
    if not name1 or not name2:
        return jsonify({'error': 'Both names are required'}), 400
    
    try:
        prediction, probabilities = comparator.predict_materiality(name1, name2)
        return jsonify({
            'success': True,
            'result': {
                'name1': name1,
                'name2': name2,
                'is_material': prediction,
                'materiality_probability': round(float(probabilities[1]), 4),
                'immateriality_probability': round(float(probabilities[0]), 4),
                'prediction': 'Material' if prediction else 'Immaterial'
            }
        })
    except Exception as e:
        return jsonify({'error': f'Error making prediction: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001) 