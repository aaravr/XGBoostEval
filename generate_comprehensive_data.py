#!/usr/bin/env python3
"""
Generate comprehensive training and test data for legal name comparison
Creates realistic synthetic data with both material and immaterial changes
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime
import os

def generate_realistic_legal_names():
    """Generate realistic legal entity names"""
    
    # Company types and their variations
    company_types = [
        "Ltd", "Limited", "LLC", "L.L.C.", "Corp", "Corporation", "Inc", "Incorporated",
        "Co", "Company", "Partnership", "LLP", "L.L.P.", "PLC", "P.L.C."
    ]
    
    # Industry sectors
    sectors = [
        "Technology", "Finance", "Healthcare", "Manufacturing", "Retail", "Energy",
        "Consulting", "Services", "Solutions", "Systems", "International", "Global",
        "Digital", "Innovation", "Enterprise", "Group", "Holdings", "Ventures"
    ]
    
    # Common business words
    business_words = [
        "Alpha", "Beta", "Gamma", "Delta", "Omega", "Sigma", "Tech", "Data", "Cloud",
        "Smart", "Digital", "Advanced", "Precision", "Quality", "Excellence", "Prime",
        "Elite", "Premium", "Standard", "Professional", "Expert", "Specialist", "Partner",
        "Associate", "Consultant", "Advisor", "Manager", "Director", "Executive", "Leader"
    ]
    
    # Geographic indicators
    locations = [
        "North", "South", "East", "West", "Central", "Regional", "National", "International",
        "Global", "Worldwide", "European", "American", "Asian", "Pacific", "Atlantic"
    ]
    
    # Generate realistic names
    names = []
    
    # Pattern 1: [Word] [Sector] [Type]
    for _ in range(30):
        word = random.choice(business_words)
        sector = random.choice(sectors)
        company_type = random.choice(company_types)
        names.append(f"{word} {sector} {company_type}")
    
    # Pattern 2: [Word] [Word] [Type]
    for _ in range(25):
        word1 = random.choice(business_words)
        word2 = random.choice(business_words)
        company_type = random.choice(company_types)
        names.append(f"{word1} {word2} {company_type}")
    
    # Pattern 3: [Location] [Sector] [Type]
    for _ in range(20):
        location = random.choice(locations)
        sector = random.choice(sectors)
        company_type = random.choice(company_types)
        names.append(f"{location} {sector} {company_type}")
    
    # Pattern 4: [Word] [Type] [Location]
    for _ in range(15):
        word = random.choice(business_words)
        company_type = random.choice(company_types)
        location = random.choice(locations)
        names.append(f"{word} {company_type} {location}")
    
    # Pattern 5: [Sector] [Word] [Type]
    for _ in range(10):
        sector = random.choice(sectors)
        word = random.choice(business_words)
        company_type = random.choice(company_types)
        names.append(f"{sector} {word} {company_type}")
    
    return names

def create_material_changes(name1):
    """Create material changes (different entities)"""
    
    material_changes = [
        # Different company type
        (name1, name1.replace("Ltd", "Corporation")),
        (name1, name1.replace("LLC", "Inc")),
        (name1, name1.replace("Limited", "PLC")),
        
        # Different sector/industry
        (name1, name1.replace("Technology", "Finance")),
        (name1, name1.replace("Healthcare", "Manufacturing")),
        (name1, name1.replace("Retail", "Energy")),
        
        # Different location
        (name1, name1.replace("North", "South")),
        (name1, name1.replace("International", "Regional")),
        (name1, name1.replace("Global", "National")),
        
        # Different business word
        (name1, name1.replace("Alpha", "Beta")),
        (name1, name1.replace("Tech", "Data")),
        (name1, name1.replace("Digital", "Smart")),
        
        # Completely different names
        (name1, f"New {name1.split()[0]} {name1.split()[-1]}"),
        (name1, f"{name1.split()[0]} Alternative {name1.split()[-1]}"),
        (name1, f"Different {name1.split()[1]} {name1.split()[-1]}")
    ]
    
    return random.choice(material_changes)

def create_immaterial_changes(name1):
    """Create immaterial changes (same entity, different format)"""
    
    immaterial_changes = [
        # Abbreviation changes
        (name1, name1.replace("Limited", "Ltd")),
        (name1, name1.replace("Ltd", "Limited")),
        (name1, name1.replace("Corporation", "Corp")),
        (name1, name1.replace("Corp", "Corporation")),
        (name1, name1.replace("Incorporated", "Inc")),
        (name1, name1.replace("Inc", "Incorporated")),
        (name1, name1.replace("Company", "Co")),
        (name1, name1.replace("Co", "Company")),
        
        # Punctuation changes
        (name1, name1.replace("L.L.C.", "LLC")),
        (name1, name1.replace("LLC", "L.L.C.")),
        (name1, name1.replace("L.L.P.", "LLP")),
        (name1, name1.replace("LLP", "L.L.P.")),
        (name1, name1.replace("P.L.C.", "PLC")),
        (name1, name1.replace("PLC", "P.L.C.")),
        
        # Case changes
        (name1, name1.upper()),
        (name1, name1.lower()),
        (name1, name1.title()),
        
        # Spacing changes
        (name1, name1.replace("  ", " ")),
        (name1, name1.replace(" ", "  ")),
        
        # Minor formatting
        (name1, name1.replace("&", "and")),
        (name1, name1.replace("and", "&")),
        (name1, name1.replace("-", " ")),
        (name1, name1.replace(" ", "-"))
    ]
    
    return random.choice(immaterial_changes)

def generate_training_data(num_entries=100):
    """Generate comprehensive training data"""
    
    print(f"Generating {num_entries} training entries...")
    
    # Generate base names
    base_names = generate_realistic_legal_names()
    
    training_data = []
    
    # Generate material changes (different entities)
    material_count = num_entries // 2
    for i in range(material_count):
        name1 = random.choice(base_names)
        name1, name2 = create_material_changes(name1)
        training_data.append({
            'source1': name1,
            'source2': name2,
            'source3': f"Training Entry {i+1}",
            'is_material': 1  # Material change
        })
    
    # Generate immaterial changes (same entity)
    immaterial_count = num_entries - material_count
    for i in range(immaterial_count):
        name1 = random.choice(base_names)
        name1, name2 = create_immaterial_changes(name1)
        training_data.append({
            'source1': name1,
            'source2': name2,
            'source3': f"Training Entry {material_count + i + 1}",
            'is_material': 0  # Immaterial change
        })
    
    # Shuffle the data
    random.shuffle(training_data)
    
    return training_data

def generate_test_data(num_entries=100):
    """Generate comprehensive test data"""
    
    print(f"Generating {num_entries} test entries...")
    
    # Generate base names
    base_names = generate_realistic_legal_names()
    
    test_data = []
    
    # Generate material changes (different entities)
    material_count = num_entries // 2
    for i in range(material_count):
        name1 = random.choice(base_names)
        name1, name2 = create_material_changes(name1)
        test_data.append({
            'name1': name1,
            'name2': name2
        })
    
    # Generate immaterial changes (same entity)
    immaterial_count = num_entries - material_count
    for i in range(immaterial_count):
        name1 = random.choice(base_names)
        name1, name2 = create_immaterial_changes(name1)
        test_data.append({
            'name1': name1,
            'name2': name2
        })
    
    # Shuffle the data
    random.shuffle(test_data)
    
    return test_data

def create_excel_files():
    """Create comprehensive training and test Excel files"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate training data
    training_data = generate_training_data(100)
    training_df = pd.DataFrame(training_data)
    
    # Generate test data
    test_data = generate_test_data(100)
    test_df = pd.DataFrame(test_data)
    
    # Create filenames
    training_filename = f"comprehensive_training_data_{timestamp}.xlsx"
    test_filename = f"comprehensive_test_data_{timestamp}.xlsx"
    
    # Save to Excel
    training_df.to_excel(training_filename, index=False)
    test_df.to_excel(test_filename, index=False)
    
    print(f"\n✅ Files created successfully!")
    print(f"📊 Training Data: {training_filename}")
    print(f"   - Shape: {training_df.shape}")
    print(f"   - Material changes: {len(training_df[training_df['is_material'] == 1])}")
    print(f"   - Immaterial changes: {len(training_df[training_df['is_material'] == 0])}")
    
    print(f"\n📊 Test Data: {test_filename}")
    print(f"   - Shape: {test_df.shape}")
    print(f"   - Total entries: {len(test_df)}")
    
    # Show sample entries
    print(f"\n📝 Sample Training Entries:")
    print("Material Changes (Different Entities):")
    material_samples = training_df[training_df['is_material'] == 1].head(3)
    for _, row in material_samples.iterrows():
        print(f"   {row['source1']} → {row['source2']}")
    
    print("\nImmaterial Changes (Same Entity):")
    immaterial_samples = training_df[training_df['is_material'] == 0].head(3)
    for _, row in immaterial_samples.iterrows():
        print(f"   {row['source1']} → {row['source2']}")
    
    print(f"\n📝 Sample Test Entries:")
    test_samples = test_df.head(5)
    for _, row in test_samples.iterrows():
        print(f"   {row['name1']} → {row['name2']}")
    
    return training_filename, test_filename

if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    np.random.seed(42)
    
    print("🚀 Generating Comprehensive Legal Name Data")
    print("=" * 50)
    
    training_file, test_file = create_excel_files()
    
    print(f"\n🎉 Data generation complete!")
    print(f"📁 Training file: {training_file}")
    print(f"📁 Test file: {test_file}")
    print(f"\n💡 Use these files to train and test your legal name comparison model!") 