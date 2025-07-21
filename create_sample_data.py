import pandas as pd
import numpy as np

def create_training_sample():
    """Create sample training data Excel file"""
    training_data = {
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
    
    df = pd.DataFrame(training_data)
    df.to_excel('sample_training_data.xlsx', index=False)
    print("Created sample_training_data.xlsx")

def create_prediction_sample():
    """Create sample prediction data Excel file"""
    prediction_data = {
        'name1': [
            'ABC LTD', 'ABC Limited', 'XYZ Corporation', 'DEF Inc',
            'Smith & Associates', 'Global Tech Solutions', 'Johnson Brothers',
            'Acme Corporation', 'Tech Solutions Inc', 'Data Analytics LLC'
        ],
        'name2': [
            'ABC Limited', 'XYZ Limited', 'XYZ Corp', 'DEF Incorporated',
            'Smith and Associates', 'Global Technology Solutions', 'Johnson Bros',
            'Acme Corp', 'Tech Solutions Corp', 'Data Analytics Limited'
        ]
    }
    
    df = pd.DataFrame(prediction_data)
    df.to_excel('sample_prediction_data.xlsx', index=False)
    print("Created sample_prediction_data.xlsx")

if __name__ == "__main__":
    create_training_sample()
    create_prediction_sample()
    print("\nSample files created successfully!")
    print("Use these files to test the system:")
    print("1. sample_training_data.xlsx - for training the model")
    print("2. sample_prediction_data.xlsx - for making predictions") 