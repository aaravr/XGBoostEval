import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder
from fuzzywuzzy import fuzz
import jellyfish
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pickle
import os

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class LegalNameComparator:
    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        
    def preprocess_legal_name(self, name):
        """Preprocess legal name for comparison"""
        if pd.isna(name) or name == '':
            return ''
        
        # Convert to string and lowercase
        name = str(name).lower().strip()
        
        # Remove common legal suffixes and standardize
        legal_suffixes = ['ltd', 'limited', 'llc', 'inc', 'incorporated', 'corp', 'corporation', 
                         'plc', 'gmbh', 'ag', 'sa', 'nv', 'bv', 'oy', 'ab']
        
        # Remove punctuation and extra spaces
        name = re.sub(r'[^\w\s]', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Remove legal suffixes
        words = name.split()
        filtered_words = []
        for word in words:
            if word not in legal_suffixes:
                filtered_words.append(word)
        
        return ' '.join(filtered_words)
    
    def extract_features(self, name1, name2):
        """Extract multiple similarity features between two legal names"""
        # Preprocess names
        proc_name1 = self.preprocess_legal_name(name1)
        proc_name2 = self.preprocess_legal_name(name2)
        
        features = {}
        
        # Basic string similarity metrics
        features['exact_match'] = 1.0 if proc_name1 == proc_name2 else 0.0
        features['length_diff'] = abs(len(proc_name1) - len(proc_name2))
        features['length_ratio'] = min(len(proc_name1), len(proc_name2)) / max(len(proc_name1), len(proc_name2)) if max(len(proc_name1), len(proc_name2)) > 0 else 0
        
        # Fuzzy string matching
        features['fuzzy_ratio'] = fuzz.ratio(proc_name1, proc_name2) / 100.0
        features['fuzzy_partial_ratio'] = fuzz.partial_ratio(proc_name1, proc_name2) / 100.0
        features['fuzzy_token_sort_ratio'] = fuzz.token_sort_ratio(proc_name1, proc_name2) / 100.0
        features['fuzzy_token_set_ratio'] = fuzz.token_set_ratio(proc_name1, proc_name2) / 100.0
        
        # Jellyfish string metrics
        features['levenshtein_distance'] = jellyfish.levenshtein_distance(proc_name1, proc_name2)
        features['jaro_similarity'] = jellyfish.jaro_similarity(proc_name1, proc_name2)
        features['jaro_winkler_similarity'] = jellyfish.jaro_winkler_similarity(proc_name1, proc_name2)
        features['hamming_distance'] = jellyfish.hamming_distance(proc_name1, proc_name2) if len(proc_name1) == len(proc_name2) else -1
        
        # Word-level features
        words1 = set(proc_name1.split())
        words2 = set(proc_name2.split())
        
        features['word_overlap'] = len(words1.intersection(words2)) / max(len(words1), len(words2)) if max(len(words1), len(words2)) > 0 else 0
        features['word_jaccard'] = len(words1.intersection(words2)) / len(words1.union(words2)) if len(words1.union(words2)) > 0 else 0
        
        # Character-level features
        chars1 = set(proc_name1.replace(' ', ''))
        chars2 = set(proc_name2.replace(' ', ''))
        
        features['char_overlap'] = len(chars1.intersection(chars2)) / max(len(chars1), len(chars2)) if max(len(chars1), len(chars2)) > 0 else 0
        features['char_jaccard'] = len(chars1.intersection(chars2)) / len(chars1.union(chars2)) if len(chars1.union(chars2)) > 0 else 0
        
        # Common legal entity indicators
        legal_indicators1 = self.count_legal_indicators(name1)
        legal_indicators2 = self.count_legal_indicators(name2)
        features['legal_indicators_diff'] = abs(legal_indicators1 - legal_indicators2)
        
        # Acronym detection
        features['acronym_similarity'] = self.acronym_similarity(proc_name1, proc_name2)
        
        return features
    
    def count_legal_indicators(self, name):
        """Count legal entity indicators in name"""
        if pd.isna(name):
            return 0
        
        indicators = ['ltd', 'limited', 'llc', 'inc', 'incorporated', 'corp', 'corporation']
        name_lower = str(name).lower()
        count = 0
        for indicator in indicators:
            if indicator in name_lower:
                count += 1
        return count
    
    def acronym_similarity(self, name1, name2):
        """Calculate similarity based on acronyms"""
        def get_acronym(name):
            words = name.split()
            return ''.join([word[0].upper() for word in words if word])
        
        acronym1 = get_acronym(name1)
        acronym2 = get_acronym(name2)
        
        if not acronym1 or not acronym2:
            return 0.0
        
        return fuzz.ratio(acronym1, acronym2) / 100.0
    
    def create_training_data(self, data):
        """Create training data from Excel file"""
        features_list = []
        labels = []
        
        # Assuming the Excel has columns: source1, source2, source3, is_material
        for _, row in data.iterrows():
            sources = [row['source1'], row['source2'], row['source3']]
            sources = [s for s in sources if pd.notna(s) and str(s).strip() != '']
            
            if len(sources) < 2:
                continue
            
            # Create pairs from all sources
            for i in range(len(sources)):
                for j in range(i + 1, len(sources)):
                    features = self.extract_features(sources[i], sources[j])
                    features_list.append(features)
                    labels.append(row['is_material'])
        
        return pd.DataFrame(features_list), labels
    
    def train_model(self, X, y):
        """Train XGBoost model"""
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
        
        # XGBoost parameters
        params = {
            'objective': 'binary:logistic',
            'eval_metric': 'logloss',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42
        }
        
        # Train model
        self.model = xgb.XGBClassifier(**params)
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model Accuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Immaterial', 'Material']))
        
        return accuracy
    
    def predict_materiality(self, name1, name2):
        """Predict if the difference between two names is material"""
        if self.model is None:
            raise ValueError("Model not trained. Please train the model first.")
        
        features = self.extract_features(name1, name2)
        features_df = pd.DataFrame([features])
        
        # Make prediction
        prediction = self.model.predict(features_df)[0]
        probability = self.model.predict_proba(features_df)[0]
        
        result = {
            'name1': name1,
            'name2': name2,
            'is_material': bool(prediction),
            'materiality_probability': float(probability[1]),
            'immateriality_probability': float(probability[0]),
            'features': features
        }
        
        return result
    
    def save_model(self, filepath):
        """Save the trained model"""
        model_data = {
            'model': self.model,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_names
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, filepath):
        """Load a trained model"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.label_encoder = model_data['label_encoder']
        self.feature_names = model_data['feature_names']
    
    def get_feature_importance(self):
        """Get feature importance from the trained model"""
        if self.model is None:
            return None
        
        importance = self.model.feature_importances_
        feature_names = self.model.feature_names_in_
        
        return dict(zip(feature_names, importance))

def create_sample_training_data():
    """Create sample training data for demonstration"""
    sample_data = {
        'source1': [
            'ABC LTD', 'ABC Limited', 'ABC LLC', 'XYZ Corporation', 'DEF Inc',
            'ABC Limited', 'XYZ Limited', 'ABC\'s LTD', 'ABCS Limited', 'ABC Corp',
            'Smith & Associates', 'Smith and Associates', 'Smith Associates',
            'Global Tech Solutions', 'Global Technology Solutions', 'Global Tech',
            'Johnson Brothers', 'Johnson Bros', 'Johnson Brothers Ltd',
            'Acme Corporation', 'Acme Corp', 'Acme Limited'
        ],
        'source2': [
            'ABC Limited', 'ABC Ltd', 'ABC LLC', 'XYZ Corp', 'DEF Incorporated',
            'XYZ Limited', 'ABC Limited', 'ABCS Limited', 'ABC\'s Limited', 'ABC Corporation',
            'Smith and Associates', 'Smith Associates', 'Smith & Associates',
            'Global Technology Solutions', 'Global Tech', 'Global Tech Solutions',
            'Johnson Bros', 'Johnson Brothers', 'Johnson Brothers Limited',
            'Acme Corp', 'Acme Limited', 'Acme Corporation'
        ],
        'source3': [
            'ABC LLC', 'ABC Limited', 'ABC LTD', 'XYZ Inc', 'DEF Corp',
            'ABC Limited', 'XYZ Limited', 'ABC Limited', 'ABCS Limited', 'ABC Corp',
            'Smith Associates', 'Smith & Associates', 'Smith and Associates',
            'Global Tech', 'Global Tech Solutions', 'Global Technology Solutions',
            'Johnson Brothers', 'Johnson Bros', 'Johnson Brothers Ltd',
            'Acme Limited', 'Acme Corporation', 'Acme Corp'
        ],
        'is_material': [
            0, 0, 0, 0, 0,  # Immaterial changes (same company, different formats)
            1, 1, 0, 0, 0,  # Material changes (different companies)
            0, 0, 0, 0, 0, 0,  # Immaterial changes
            0, 0, 0, 0, 0, 0   # Immaterial changes
        ]
    }
    
    return pd.DataFrame(sample_data)

if __name__ == "__main__":
    # Create sample data and train model
    print("Creating sample training data...")
    sample_data = create_sample_training_data()
    
    # Initialize comparator
    comparator = LegalNameComparator()
    
    # Create training data
    print("Extracting features...")
    X, y = comparator.create_training_data(sample_data)
    
    # Train model
    print("Training XGBoost model...")
    accuracy = comparator.train_model(X, y)
    
    # Save model
    print("Saving model...")
    comparator.save_model('legal_name_model.pkl')
    
    # Test predictions
    print("\nTesting predictions:")
    test_cases = [
        ('ABC LTD', 'ABC Limited'),
        ('ABC Limited', 'XYZ Limited'),
        ('ABC\'s LTD', 'ABCS Limited'),
        ('Smith & Associates', 'Smith and Associates'),
        ('Global Tech Solutions', 'Global Technology Solutions')
    ]
    
    for name1, name2 in test_cases:
        result = comparator.predict_materiality(name1, name2)
        print(f"{name1} vs {name2}: {'Material' if result['is_material'] else 'Immaterial'} "
              f"(confidence: {result['materiality_probability']:.3f})")
    
    # Feature importance
    importance = comparator.get_feature_importance()
    print("\nTop 5 most important features:")
    sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    for feature, score in sorted_importance[:5]:
        print(f"{feature}: {score:.4f}") 