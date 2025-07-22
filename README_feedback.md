# Legal Name Comparison System with Feedback Loop

A simplified machine learning system for comparing legal names with an integrated feedback loop for continuous model improvement.

## 🚀 **Features**

### **Core Functionality**
- **Model Training**: Upload Excel files to train XGBoost models
- **Predictions**: Make predictions on new legal name pairs
- **Feedback Collection**: Users can provide feedback on predictions
- **Automatic Retraining**: Model retrains when sufficient feedback is collected (10+ items)
- **Model Versioning**: Track model versions and performance

### **Feedback Loop**
- **User Feedback**: Users can mark predictions as correct or incorrect
- **Feedback Statistics**: View feedback metrics and correction rates
- **Automatic Retraining**: System automatically retrains when 10+ new feedback items are available
- **Manual Retraining**: Option to manually trigger retraining

## 📋 **Installation**

### **1. Install Dependencies**
```bash
pip install -r requirements_feedback.txt
```

### **2. Download NLTK Data**
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### **3. Run the Application**
```bash
python app_with_feedback.py
```

The application will be available at `http://localhost:5001`

## 📊 **Usage**

### **1. Model Training**
1. Prepare an Excel file with columns: `source1`, `source2`, `source3`, `is_material`
2. Upload the file through the web interface
3. The system will train an XGBoost model and display accuracy

### **2. Making Predictions**
1. Prepare an Excel file with columns: `name1`, `name2`
2. Upload the file through the web interface
3. View predictions and confidence scores

### **3. Providing Feedback**
1. After making predictions, click "Correct" or "Wrong" for each result
2. The system will collect feedback and automatically retrain when sufficient data is available
3. View feedback statistics in the sidebar

### **4. Monitoring**
- **System Status**: Check if the system is healthy
- **Feedback Stats**: View total feedback, unprocessed items, and correction rates
- **Model Versions**: Track model versions and their accuracy

## 🔄 **Feedback Loop Process**

### **How It Works**
1. **Prediction**: System makes predictions on legal name pairs
2. **Feedback Collection**: Users provide feedback on predictions
3. **Feedback Storage**: Feedback is stored in SQLite database
4. **Retraining Trigger**: When 10+ unprocessed feedback items are available
5. **Model Retraining**: System retrains model using feedback data
6. **Version Update**: New model version is saved with updated accuracy

### **Feedback Types**
- **Correct**: User confirms the prediction was right
- **Wrong**: User indicates the prediction was incorrect (system flips the label)

## 📁 **File Structure**

```
├── app_with_feedback.py          # Main Flask application
├── legal_name_comparison.py      # ML model logic
├── requirements_feedback.txt      # Python dependencies
├── templates/
│   └── index_with_feedback.html  # Web interface
├── static/
│   └── js/
│       └── app_with_feedback.js  # Frontend JavaScript
├── uploads/                      # Temporary file storage
├── models/                       # Saved model files
└── feedback.db                   # SQLite database for feedback
```

## 🗄️ **Database Schema**

### **Feedback Table**
```sql
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name1 TEXT NOT NULL,
    name2 TEXT NOT NULL,
    original_prediction BOOLEAN NOT NULL,
    user_correction BOOLEAN NOT NULL,
    confidence_score REAL,
    feedback_text TEXT,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Model Versions Table**
```sql
CREATE TABLE model_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL,
    accuracy REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT FALSE
);
```

## 🔧 **API Endpoints**

### **Training**
- `POST /upload` - Upload training data and train model

### **Predictions**
- `POST /predict` - Make predictions on new data

### **Feedback**
- `POST /feedback` - Submit feedback on predictions
- `GET /feedback/stats` - Get feedback statistics

### **Model Management**
- `POST /model/retrain` - Manually trigger model retraining
- `GET /model/versions` - Get model version history

### **System**
- `GET /health` - Health check endpoint

## 📈 **Sample Data**

### **Training Data Format**
```csv
source1,source2,source3,is_material
ABC LTD,ABC Limited,,false
ABC Limited,XYZ Limited,,true
ABC's LITD,ABCS Limited,,false
```

### **Prediction Data Format**
```csv
name1,name2
ABC Corporation,ABC Corp
XYZ Limited,XYZ Ltd
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **"No trained model available"**
   - Train a model first by uploading training data

2. **"Not enough feedback for retraining"**
   - Need at least 10 feedback items for automatic retraining
   - Use manual retrain button if needed

3. **"Invalid file type"**
   - Ensure you're uploading Excel files (.xlsx or .xls)

4. **Database errors**
   - The system automatically creates the SQLite database
   - Check file permissions in the application directory

### **Performance Tips**

1. **Large Files**: For large datasets, consider splitting into smaller files
2. **Feedback Quality**: Encourage users to provide accurate feedback
3. **Regular Retraining**: Monitor feedback stats and retrain when needed

## 🔮 **Future Enhancements**

- **Email Notifications**: Alert when model retraining occurs
- **Advanced Analytics**: More detailed feedback analysis
- **A/B Testing**: Compare different model versions
- **API Rate Limiting**: Prevent abuse of the system
- **User Authentication**: Secure access to the system

## 📞 **Support**

For issues or questions:
1. Check the troubleshooting section
2. Review the logs in the console
3. Ensure all dependencies are installed correctly

---

**Note**: This is a simplified version focused on the feedback loop. For enterprise features like authentication, monitoring, and advanced deployment, see the enterprise architecture documentation. 