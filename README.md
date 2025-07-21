# Legal Name Comparison ML System

A machine learning system that uses XGBoost and multiple algorithms to evaluate material vs immaterial changes in legal names. The system provides a web interface for uploading Excel files and getting predictions.

## Features

- **Multiple Algorithm Integration**: Combines fuzzy string matching, Jellyfish metrics, word-level analysis, and character-level features
- **XGBoost Model**: Advanced gradient boosting for accurate predictions
- **Web UI**: Modern, responsive interface with drag-and-drop file upload
- **Real-time Analysis**: Individual name comparison testing
- **Visual Analytics**: Feature importance plots and prediction distributions
- **Excel Integration**: Direct upload and download of results

## Examples

### Immaterial Changes (Same Company, Different Format)
- ABC LTD vs ABC Limited
- ABC LLC vs ABC Ltd
- Smith & Associates vs Smith and Associates
- Global Tech Solutions vs Global Technology Solutions

### Material Changes (Different Companies)
- ABC Limited vs XYZ Limited
- ABC Corp vs DEF Inc
- Johnson Brothers vs Smith Associates

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd legal-name-comparison
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
python app.py
```

4. **Access the web interface**:
Open your browser and go to `http://localhost:5000`

## Usage

### Step 1: Train the Model

1. Prepare an Excel file with training data containing these columns:
   - `source1`: Legal name from first source
   - `source2`: Legal name from second source  
   - `source3`: Legal name from third source (can be empty)
   - `is_material`: 1 for material changes, 0 for immaterial changes

2. Upload the file through the web interface
3. The system will train the XGBoost model and show accuracy metrics

### Step 2: Make Predictions

1. Prepare an Excel file with prediction data containing:
   - `name1`: First legal name to compare
   - `name2`: Second legal name to compare

2. Upload the file to get predictions
3. Download results as Excel file

### Step 3: Test Individual Names

Use the "Test Individual Prediction" section to compare single pairs of names in real-time.

## Sample Data Formats

### Training Data Format (training_data.xlsx)

| source1 | source2 | source3 | is_material |
|---------|---------|---------|-------------|
| ABC LTD | ABC Limited | ABC LLC | 0 |
| ABC Limited | XYZ Limited | ABC Limited | 1 |
| Smith & Associates | Smith and Associates | Smith Associates | 0 |
| Global Tech Solutions | Global Technology Solutions | Global Tech | 0 |

### Prediction Data Format (prediction_data.xlsx)

| name1 | name2 |
|-------|-------|
| ABC LTD | ABC Limited |
| XYZ Corporation | ABC Corp |
| Johnson Brothers | Smith Associates |

## Technical Details

### Algorithms Used

1. **Fuzzy String Matching**:
   - Ratio similarity
   - Partial ratio
   - Token sort ratio
   - Token set ratio

2. **Jellyfish String Metrics**:
   - Levenshtein distance
   - Jaro distance
   - Jaro-Winkler similarity
   - Hamming distance

3. **Word-level Analysis**:
   - Word overlap ratio
   - Jaccard similarity
   - Acronym similarity

4. **Character-level Analysis**:
   - Character overlap ratio
   - Character Jaccard similarity

5. **Legal Entity Detection**:
   - Legal suffix counting
   - Entity type indicators

### Model Features

The XGBoost model uses 15+ features including:
- Exact match indicator
- Length differences and ratios
- Multiple fuzzy matching scores
- Word and character-level similarities
- Legal entity indicators
- Acronym similarity

### Model Performance

- **Accuracy**: Typically 85-95% on well-labeled data
- **Training Time**: 1-5 seconds for 1000+ data pairs
- **Prediction Time**: <1 second per comparison

## API Endpoints

### POST /upload
Upload training data Excel file
- **Input**: Excel file with columns: source1, source2, source3, is_material
- **Output**: Training results with accuracy and feature importance

### POST /predict  
Upload prediction data Excel file
- **Input**: Excel file with columns: name1, name2
- **Output**: Predictions with probabilities and downloadable results

### POST /test_prediction
Test individual name comparison
- **Input**: JSON with name1, name2
- **Output**: Prediction result with confidence scores

### GET /download_predictions
Download prediction results as Excel file

## File Structure

```
legal-name-comparison/
├── app.py                          # Flask web application
├── legal_name_comparison.py        # Core ML system
├── requirements.txt                 # Python dependencies
├── README.md                       # This file
├── templates/
│   └── index.html                  # Web interface template
├── static/
│   └── js/
│       └── app.js                  # Frontend JavaScript
└── uploads/                        # Temporary file storage
```

## Customization

### Adding New Features

To add new similarity features, modify the `extract_features` method in `LegalNameComparator`:

```python
def extract_features(self, name1, name2):
    features = {}
    # ... existing features ...
    
    # Add your new feature
    features['your_new_feature'] = your_calculation(name1, name2)
    
    return features
```

### Model Parameters

Adjust XGBoost parameters in the `train_model` method:

```python
params = {
    'objective': 'binary:logistic',
    'eval_metric': 'logloss',
    'max_depth': 6,              # Tree depth
    'learning_rate': 0.1,        # Learning rate
    'n_estimators': 100,         # Number of trees
    'subsample': 0.8,            # Row sampling
    'colsample_bytree': 0.8,     # Column sampling
    'random_state': 42
}
```

## Troubleshooting

### Common Issues

1. **"No trained model available"**
   - Upload training data first before making predictions

2. **"Missing required columns"**
   - Ensure your Excel file has the correct column names
   - Check for typos in column headers

3. **"No valid data pairs found"**
   - Ensure at least 2 sources have data in each row
   - Check for empty or invalid data

4. **Model accuracy is low**
   - Review your training data labels
   - Add more diverse examples
   - Check for data quality issues

### Performance Tips

1. **Large Files**: For files with 10,000+ rows, consider processing in batches
2. **Memory**: The system uses ~500MB RAM for typical datasets
3. **Speed**: Predictions are cached for repeated comparisons

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the sample data formats
3. Open an issue on GitHub

## Future Enhancements

- [ ] Support for additional file formats (CSV, JSON)
- [ ] Batch processing for large datasets
- [ ] Model versioning and A/B testing
- [ ] API rate limiting and authentication
- [ ] Docker containerization
- [ ] Database integration for persistent storage 