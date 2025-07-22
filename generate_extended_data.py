#!/usr/bin/env python3
"""
Extended Data Generator for Legal Name Comparison
Generates 100 additional training samples with special characters and various scenarios
"""

import pandas as pd
import random
import string
import re
from datetime import datetime

def generate_special_characters():
    """Generate various special characters for testing"""
    return [
        "&", "and", "AND", "And",
        "(", ")", "[", "]", "{", "}",
        "-", "_", ".", ",", ";", ":",
        "'", "'", '"', '"',
        "®", "™", "©", "℠",
        "§", "¶", "†", "‡",
        "°", "±", "×", "÷",
        "¢", "£", "¥", "€",
        "№", "℅", "‰", "∞",
        "≈", "≠", "≤", "≥",
        "∑", "∏", "√", "∫",
        "α", "β", "γ", "δ",
        "μ", "π", "σ", "τ",
        "φ", "ω", "Ω", "θ"
    ]

def generate_legal_suffixes():
    """Generate various legal entity suffixes"""
    return [
        "LTD", "Limited", "LIMITED", "Ltd", "Ltd.",
        "LLC", "L.L.C.", "L.L.C",
        "INC", "Inc", "Inc.", "Incorporated", "INCORPORATED",
        "CORP", "Corp", "Corp.", "Corporation", "CORPORATION",
        "CO", "Co", "Co.", "Company", "COMPANY",
        "LP", "L.P.", "L.P",
        "LLP", "L.L.P.", "L.L.P",
        "PC", "P.C.", "P.C",
        "PA", "P.A.", "P.A",
        "PLC", "P.L.C.", "P.L.C",
        "GMBH", "GmbH", "GmbH.",
        "AG", "A.G.", "A.G",
        "SA", "S.A.", "S.A",
        "NV", "N.V.", "N.V",
        "BV", "B.V.", "B.V",
        "PTY", "Pty", "Pty.", "Proprietary", "PROPRIETARY",
        "PTE", "Pte", "Pte.", "Private", "PRIVATE",
        "SPA", "S.p.A.", "S.p.A",
        "SRL", "S.r.l.", "S.r.l",
        "SARL", "S.à.r.l.", "S.à.r.l",
        "KG", "K.G.", "K.G",
        "OHG", "O.H.G.", "O.H.G",
        "GMBH", "G.m.b.H.", "G.m.b.H"
    ]

def generate_common_words():
    """Generate common business words"""
    return [
        "International", "INTERNATIONAL", "Int'l", "INT'L",
        "Global", "GLOBAL", "Glbl", "GLBL",
        "Worldwide", "WORLDWIDE", "WW", "W.W.",
        "National", "NATIONAL", "Natl", "NATL",
        "Regional", "REGIONAL", "Reg", "REG",
        "Local", "LOCAL", "Loc", "LOC",
        "United", "UNITED", "Utd", "UTD",
        "American", "AMERICAN", "Amer", "AMER",
        "European", "EUROPEAN", "Eur", "EUR",
        "Asian", "ASIAN", "Asia", "ASIA",
        "Pacific", "PACIFIC", "Pac", "PAC",
        "Atlantic", "ATLANTIC", "Atl", "ATL",
        "Northern", "NORTHERN", "Nth", "NTH",
        "Southern", "SOUTHERN", "Sth", "STH",
        "Eastern", "EASTERN", "Est", "EST",
        "Western", "WESTERN", "Wst", "WST",
        "Central", "CENTRAL", "Ctr", "CTR",
        "Advanced", "ADVANCED", "Adv", "ADV",
        "Premium", "PREMIUM", "Prem", "PREM",
        "Elite", "ELITE", "Elt", "ELT",
        "Professional", "PROFESSIONAL", "Prof", "PROF",
        "Services", "SERVICES", "Svc", "SVC",
        "Solutions", "SOLUTIONS", "Sol", "SOL",
        "Systems", "SYSTEMS", "Sys", "SYS",
        "Technologies", "TECHNOLOGIES", "Tech", "TECH",
        "Industries", "INDUSTRIES", "Ind", "IND",
        "Manufacturing", "MANUFACTURING", "Mfg", "MFG",
        "Distribution", "DISTRIBUTION", "Dist", "DIST",
        "Trading", "TRADING", "Trdg", "TRDG",
        "Investment", "INVESTMENT", "Inv", "INV",
        "Financial", "FINANCIAL", "Fin", "FIN",
        "Insurance", "INSURANCE", "Ins", "INS",
        "Real Estate", "REAL ESTATE", "RE", "R.E.",
        "Development", "DEVELOPMENT", "Dev", "DEV",
        "Construction", "CONSTRUCTION", "Constr", "CONSTR",
        "Engineering", "ENGINEERING", "Eng", "ENG",
        "Consulting", "CONSULTING", "Cons", "CONS",
        "Management", "MANAGEMENT", "Mgmt", "MGMT",
        "Administration", "ADMINISTRATION", "Admin", "ADMIN",
        "Operations", "OPERATIONS", "Ops", "OPS",
        "Marketing", "MARKETING", "Mktg", "MKTG",
        "Sales", "SALES", "Sl", "SL",
        "Customer", "CUSTOMER", "Cust", "CUST",
        "Client", "CLIENT", "Clt", "CLT",
        "Partner", "PARTNER", "Ptnr", "PTNR",
        "Associate", "ASSOCIATE", "Assoc", "ASSOC",
        "Group", "GROUP", "Grp", "GRP",
        "Team", "TEAM", "Tm", "TM",
        "Network", "NETWORK", "Net", "NET",
        "Alliance", "ALLIANCE", "All", "ALL",
        "Federation", "FEDERATION", "Fed", "FED",
        "Consortium", "CONSORTIUM", "Cons", "CONS",
        "Foundation", "FOUNDATION", "Fdn", "FDN",
        "Institute", "INSTITUTE", "Inst", "INST",
        "Academy", "ACADEMY", "Acad", "ACAD",
        "University", "UNIVERSITY", "Univ", "UNIV",
        "College", "COLLEGE", "Coll", "COLL",
        "School", "SCHOOL", "Sch", "SCH",
        "Center", "CENTER", "Ctr", "CTR",
        "Laboratory", "LABORATORY", "Lab", "LAB",
        "Research", "RESEARCH", "Rsch", "RSCH",
        "Development", "DEVELOPMENT", "Dev", "DEV",
        "Innovation", "INNOVATION", "Innov", "INNOV",
        "Creative", "CREATIVE", "Creat", "CREAT",
        "Digital", "DIGITAL", "Dig", "DIG",
        "Online", "ONLINE", "Onl", "ONL",
        "Virtual", "VIRTUAL", "Virt", "VIRT",
        "Cloud", "CLOUD", "Cld", "CLD",
        "Mobile", "MOBILE", "Mob", "MOB",
        "Smart", "SMART", "Smt", "SMT",
        "Intelligent", "INTELLIGENT", "Intel", "INTEL",
        "Automated", "AUTOMATED", "Auto", "AUTO",
        "Robotic", "ROBOTIC", "Robot", "ROBOT",
        "Artificial", "ARTIFICIAL", "Art", "ART",
        "Machine", "MACHINE", "Mach", "MACH",
        "Learning", "LEARNING", "Learn", "LEARN",
        "Data", "DATA", "Dat", "DAT",
        "Analytics", "ANALYTICS", "Anal", "ANAL",
        "Information", "INFORMATION", "Info", "INFO",
        "Technology", "TECHNOLOGY", "Tech", "TECH",
        "Software", "SOFTWARE", "Soft", "SOFT",
        "Hardware", "HARDWARE", "Hard", "HARD",
        "Network", "NETWORK", "Net", "NET",
        "Security", "SECURITY", "Sec", "SEC",
        "Privacy", "PRIVACY", "Priv", "PRIV",
        "Compliance", "COMPLIANCE", "Comp", "COMP",
        "Regulatory", "REGULATORY", "Reg", "REG",
        "Legal", "LEGAL", "Lgl", "LGL",
        "Corporate", "CORPORATE", "Corp", "CORP",
        "Business", "BUSINESS", "Bus", "BUS",
        "Enterprise", "ENTERPRISE", "Ent", "ENT",
        "Commercial", "COMMERCIAL", "Comm", "COMM",
        "Industrial", "INDUSTRIAL", "Ind", "IND",
        "Manufacturing", "MANUFACTURING", "Mfg", "MFG",
        "Production", "PRODUCTION", "Prod", "PROD",
        "Quality", "QUALITY", "Qual", "QUAL",
        "Standard", "STANDARD", "Std", "STD",
        "Certified", "CERTIFIED", "Cert", "CERT",
        "Accredited", "ACCREDITED", "Accr", "ACCR",
        "Licensed", "LICENSED", "Lic", "LIC",
        "Registered", "REGISTERED", "Reg", "REG",
        "Approved", "APPROVED", "App", "APP",
        "Authorized", "AUTHORIZED", "Auth", "AUTH",
        "Certified", "CERTIFIED", "Cert", "CERT",
        "Verified", "VERIFIED", "Ver", "VER",
        "Validated", "VALIDATED", "Val", "VAL",
        "Tested", "TESTED", "Test", "TEST",
        "Proven", "PROVEN", "Prov", "PROV",
        "Reliable", "RELIABLE", "Rel", "REL",
        "Trusted", "TRUSTED", "Trust", "TRUST",
        "Secure", "SECURE", "Sec", "SEC",
        "Safe", "SAFE", "Sf", "SF",
        "Protected", "PROTECTED", "Prot", "PROT",
        "Guaranteed", "GUARANTEED", "Guar", "GUAR",
        "Warranted", "WARRANTED", "Warr", "WARR",
        "Insured", "INSURED", "Ins", "INS",
        "Bonded", "BONDED", "Bond", "BOND",
        "Licensed", "LICENSED", "Lic", "LIC",
        "Permitted", "PERMITTED", "Perm", "PERM",
        "Approved", "APPROVED", "App", "APP",
        "Authorized", "AUTHORIZED", "Auth", "AUTH",
        "Certified", "CERTIFIED", "Cert", "CERT",
        "Verified", "VERIFIED", "Ver", "VER",
        "Validated", "VALIDATED", "Val", "VAL",
        "Tested", "TESTED", "Test", "TEST",
        "Proven", "PROVEN", "Prov", "PROV",
        "Reliable", "RELIABLE", "Rel", "REL",
        "Trusted", "TRUSTED", "Trust", "TRUST",
        "Secure", "SECURE", "Sec", "SEC",
        "Safe", "SAFE", "Sf", "SF",
        "Protected", "PROTECTED", "Prot", "PROT",
        "Guaranteed", "GUARANTEED", "Guar", "GUAR",
        "Warranted", "WARRANTED", "Warr", "WARR",
        "Insured", "INSURED", "Ins", "INS",
        "Bonded", "BONDED", "Bond", "BOND"
    ]

def generate_immaterial_scenarios():
    """Generate immaterial change scenarios"""
    scenarios = []
    
    # Case variations
    base_names = [
        "ABC Corporation", "XYZ Limited", "Tech Solutions Inc",
        "Global Industries", "Premium Services", "Elite Consulting",
        "Advanced Systems", "Professional Group", "International Trading",
        "National Manufacturing", "Regional Distribution", "Local Operations"
    ]
    
    for base in base_names:
        # Different case variations
        scenarios.append((base, base.upper(), False))  # Uppercase
        scenarios.append((base, base.lower(), False))  # Lowercase
        scenarios.append((base, base.title(), False))  # Title case
        
        # Abbreviation variations
        words = base.split()
        if len(words) > 1:
            abbrev = " ".join([word[0] for word in words])
            scenarios.append((base, abbrev, False))  # Abbreviated
            scenarios.append((abbrev, base, False))  # Expanded
        
        # Common word variations
        if "Corporation" in base:
            scenarios.append((base, base.replace("Corporation", "Corp"), False))
            scenarios.append((base, base.replace("Corporation", "Corp."), False))
        if "Limited" in base:
            scenarios.append((base, base.replace("Limited", "Ltd"), False))
            scenarios.append((base, base.replace("Limited", "Ltd."), False))
        if "Incorporated" in base:
            scenarios.append((base, base.replace("Incorporated", "Inc"), False))
            scenarios.append((base, base.replace("Incorporated", "Inc."), False))
        if "Company" in base:
            scenarios.append((base, base.replace("Company", "Co"), False))
            scenarios.append((base, base.replace("Company", "Co."), False))
    
    return scenarios

def generate_material_scenarios():
    """Generate material change scenarios"""
    scenarios = []
    
    # Different company names (material changes)
    companies = [
        ("ABC Corporation", "XYZ Corporation", True),
        ("Tech Solutions Inc", "Data Systems Inc", True),
        ("Global Industries", "Local Industries", True),
        ("Premium Services", "Basic Services", True),
        ("Elite Consulting", "Standard Consulting", True),
        ("Advanced Systems", "Simple Systems", True),
        ("Professional Group", "Amateur Group", True),
        ("International Trading", "Domestic Trading", True),
        ("National Manufacturing", "Regional Manufacturing", True),
        ("Regional Distribution", "Local Distribution", True),
        ("Local Operations", "Remote Operations", True),
        ("ABC Tech Solutions", "XYZ Tech Solutions", True),
        ("Global Data Corp", "Local Data Corp", True),
        ("Premium Consulting LLC", "Standard Consulting LLC", True),
        ("Elite Systems Inc", "Basic Systems Inc", True),
        ("Advanced Group Ltd", "Simple Group Ltd", True),
        ("International Services", "Domestic Services", True),
        ("National Solutions", "Regional Solutions", True),
        ("Regional Operations", "Local Operations", True),
        ("Local Manufacturing", "Remote Manufacturing", True),
        ("ABC International", "XYZ International", True),
        ("Tech Global Corp", "Data Global Corp", True),
        ("Premium Elite LLC", "Standard Elite LLC", True),
        ("Advanced Professional", "Simple Professional", True),
        ("International Systems", "Domestic Systems", True),
        ("National Consulting", "Regional Consulting", True),
        ("Regional Trading", "Local Trading", True),
        ("Local Industries", "Remote Industries", True),
        ("ABC Premium Corp", "XYZ Premium Corp", True),
        ("Tech Elite Inc", "Data Elite Inc", True),
        ("Global Advanced LLC", "Local Advanced LLC", True),
        ("International Professional", "Domestic Professional", True),
        ("National Systems", "Regional Systems", True),
        ("Regional Services", "Local Services", True),
        ("Local Solutions", "Remote Solutions", True),
        ("ABC Global Inc", "XYZ Global Inc", True),
        ("Tech International LLC", "Data International LLC", True),
        ("Premium National Corp", "Standard National Corp", True),
        ("Elite Regional Inc", "Basic Regional Inc", True),
        ("Advanced Local LLC", "Simple Local LLC", True),
        ("Professional Remote Corp", "Amateur Remote Corp", True),
        ("International Domestic Inc", "Domestic International Inc", True),
        ("National Regional LLC", "Regional National LLC", True),
        ("Regional Local Corp", "Local Regional Corp", True),
        ("Local Remote Inc", "Remote Local Inc", True),
        ("ABC Tech Global", "XYZ Tech Global", True),
        ("Data Premium Elite", "Tech Premium Elite", True),
        ("Global Advanced Professional", "Local Advanced Professional", True),
        ("International National Systems", "Domestic National Systems", True),
        ("National Regional Consulting", "Regional National Consulting", True),
        ("Regional Local Trading", "Local Regional Trading", True),
        ("Local Remote Industries", "Remote Local Industries", True)
    ]
    
    scenarios.extend(companies)
    return scenarios

def generate_special_character_scenarios():
    """Generate scenarios with special characters"""
    scenarios = []
    
    base_names = [
        "ABC & Associates",
        "Smith & Sons",
        "Johnson & Partners",
        "Williams & Co",
        "Brown & Associates",
        "Jones & Brothers",
        "Garcia & Sisters",
        "Miller & Family",
        "Davis & Group",
        "Rodriguez & Team"
    ]
    
    special_chars = generate_special_characters()
    
    for base in base_names:
        # Replace & with different special characters
        for char in special_chars[:10]:  # Use first 10 special chars
            new_name = base.replace("&", char)
            scenarios.append((base, new_name, False))  # Immaterial - same company, different symbol
        
        # Add special characters to existing names
        scenarios.append((base, base + "®", False))  # Trademark
        scenarios.append((base, base + "™", False))  # Trademark
        scenarios.append((base, base + "©", False))  # Copyright
        scenarios.append((base, base + "℠", False))  # Service mark
        scenarios.append((base, base + "§", False))  # Section symbol
        scenarios.append((base, base + "¶", False))  # Paragraph symbol
        scenarios.append((base, base + "†", False))  # Dagger
        scenarios.append((base, base + "‡", False))  # Double dagger
        scenarios.append((base, base + "°", False))  # Degree
        scenarios.append((base, base + "±", False))  # Plus-minus
        scenarios.append((base, base + "×", False))  # Multiplication
        scenarios.append((base, base + "÷", False))  # Division
        scenarios.append((base, base + "¢", False))  # Cent
        scenarios.append((base, base + "£", False))  # Pound
        scenarios.append((base, base + "¥", False))  # Yen
        scenarios.append((base, base + "€", False))  # Euro
        scenarios.append((base, base + "№", False))  # Numero
        scenarios.append((base, base + "℅", False))  # Care of
        scenarios.append((base, base + "‰", False))  # Per mille
        scenarios.append((base, base + "∞", False))  # Infinity
        scenarios.append((base, base + "≈", False))  # Approximately
        scenarios.append((base, base + "≠", False))  # Not equal
        scenarios.append((base, base + "≤", False))  # Less than or equal
        scenarios.append((base, base + "≥", False))  # Greater than or equal
        scenarios.append((base, base + "∑", False))  # Summation
        scenarios.append((base, base + "∏", False))  # Product
        scenarios.append((base, base + "√", False))  # Square root
        scenarios.append((base, base + "∫", False))  # Integral
        scenarios.append((base, base + "α", False))  # Alpha
        scenarios.append((base, base + "β", False))  # Beta
        scenarios.append((base, base + "γ", False))  # Gamma
        scenarios.append((base, base + "δ", False))  # Delta
        scenarios.append((base, base + "μ", False))  # Mu
        scenarios.append((base, base + "π", False))  # Pi
        scenarios.append((base, base + "σ", False))  # Sigma
        scenarios.append((base, base + "τ", False))  # Tau
        scenarios.append((base, base + "φ", False))  # Phi
        scenarios.append((base, base + "ω", False))  # Omega
        scenarios.append((base, base + "Ω", False))  # Omega
        scenarios.append((base, base + "θ", False))  # Theta
    
    return scenarios

def generate_legal_suffix_scenarios():
    """Generate scenarios with different legal suffixes"""
    scenarios = []
    
    base_names = [
        "ABC Corporation",
        "XYZ Limited",
        "Tech Solutions Inc",
        "Global Industries",
        "Premium Services",
        "Elite Consulting",
        "Advanced Systems",
        "Professional Group",
        "International Trading",
        "National Manufacturing"
    ]
    
    suffixes = generate_legal_suffixes()
    
    for base in base_names:
        # Replace existing suffixes with different ones
        for suffix in suffixes[:20]:  # Use first 20 suffixes
            if "Corporation" in base:
                new_name = base.replace("Corporation", suffix)
                scenarios.append((base, new_name, False))  # Immaterial - same company, different legal form
            elif "Limited" in base:
                new_name = base.replace("Limited", suffix)
                scenarios.append((base, new_name, False))
            elif "Inc" in base:
                new_name = base.replace("Inc", suffix)
                scenarios.append((base, new_name, False))
            elif "Industries" in base:
                new_name = base.replace("Industries", suffix)
                scenarios.append((base, new_name, False))
            elif "Services" in base:
                new_name = base.replace("Services", suffix)
                scenarios.append((base, new_name, False))
            elif "Consulting" in base:
                new_name = base.replace("Consulting", suffix)
                scenarios.append((base, new_name, False))
            elif "Systems" in base:
                new_name = base.replace("Systems", suffix)
                scenarios.append((base, new_name, False))
            elif "Group" in base:
                new_name = base.replace("Group", suffix)
                scenarios.append((base, new_name, False))
            elif "Trading" in base:
                new_name = base.replace("Trading", suffix)
                scenarios.append((base, new_name, False))
            elif "Manufacturing" in base:
                new_name = base.replace("Manufacturing", suffix)
                scenarios.append((base, new_name, False))
    
    return scenarios

def generate_common_word_scenarios():
    """Generate scenarios with common word variations"""
    scenarios = []
    
    base_names = [
        "ABC International Corp",
        "XYZ Global Ltd",
        "Tech National Inc",
        "Data Regional LLC",
        "Systems Local Corp",
        "Services Worldwide Inc",
        "Consulting American Ltd",
        "Solutions European Corp",
        "Operations Asian Inc",
        "Trading Pacific LLC"
    ]
    
    common_words = generate_common_words()
    
    for base in base_names:
        # Replace common words with variations
        for word in common_words[:30]:  # Use first 30 common words
            if "International" in base:
                new_name = base.replace("International", word)
                scenarios.append((base, new_name, True))  # Material - different scope
            elif "Global" in base:
                new_name = base.replace("Global", word)
                scenarios.append((base, new_name, True))
            elif "National" in base:
                new_name = base.replace("National", word)
                scenarios.append((base, new_name, True))
            elif "Regional" in base:
                new_name = base.replace("Regional", word)
                scenarios.append((base, new_name, True))
            elif "Local" in base:
                new_name = base.replace("Local", word)
                scenarios.append((base, new_name, True))
            elif "Worldwide" in base:
                new_name = base.replace("Worldwide", word)
                scenarios.append((base, new_name, True))
            elif "American" in base:
                new_name = base.replace("American", word)
                scenarios.append((base, new_name, True))
            elif "European" in base:
                new_name = base.replace("European", word)
                scenarios.append((base, new_name, True))
            elif "Asian" in base:
                new_name = base.replace("Asian", word)
                scenarios.append((base, new_name, True))
            elif "Pacific" in base:
                new_name = base.replace("Pacific", word)
                scenarios.append((base, new_name, True))
    
    return scenarios

def generate_training_data():
    """Generate comprehensive training data"""
    all_scenarios = []
    
    # Add different types of scenarios
    all_scenarios.extend(generate_immaterial_scenarios())
    all_scenarios.extend(generate_material_scenarios())
    all_scenarios.extend(generate_special_character_scenarios())
    all_scenarios.extend(generate_legal_suffix_scenarios())
    all_scenarios.extend(generate_common_word_scenarios())
    
    # Shuffle to randomize the order
    random.shuffle(all_scenarios)
    
    # Take first 100 scenarios
    selected_scenarios = all_scenarios[:100]
    
    # Create training data
    training_data = []
    for i, (name1, name2, is_material) in enumerate(selected_scenarios):
        training_data.append({
            'source1': name1,
            'source2': name2,
            'source3': '',  # Empty for training data
            'is_material': is_material
        })
    
    return training_data

def generate_prediction_data():
    """Generate prediction data with special characters"""
    prediction_data = []
    
    # Generate 50 prediction samples with special characters
    base_names = [
        "Alpha & Beta Corp",
        "Gamma & Delta Ltd",
        "Epsilon & Zeta Inc",
        "Eta & Theta LLC",
        "Iota & Kappa Corp",
        "Lambda & Mu Ltd",
        "Nu & Xi Inc",
        "Omicron & Pi LLC",
        "Rho & Sigma Corp",
        "Tau & Upsilon Ltd",
        "Phi & Chi Inc",
        "Psi & Omega LLC",
        "Alpha & Beta Corp®",
        "Gamma & Delta Ltd™",
        "Epsilon & Zeta Inc©",
        "Eta & Theta LLC℠",
        "Iota & Kappa Corp§",
        "Lambda & Mu Ltd¶",
        "Nu & Xi Inc†",
        "Omicron & Pi LLC‡",
        "Rho & Sigma Corp°",
        "Tau & Upsilon Ltd±",
        "Phi & Chi Inc×",
        "Psi & Omega LLC÷",
        "Alpha & Beta Corp¢",
        "Gamma & Delta Ltd£",
        "Epsilon & Zeta Inc¥",
        "Eta & Theta LLC€",
        "Iota & Kappa Corp№",
        "Lambda & Mu Ltd℅",
        "Nu & Xi Inc‰",
        "Omicron & Pi LLC∞",
        "Rho & Sigma Corp≈",
        "Tau & Upsilon Ltd≠",
        "Phi & Chi Inc≤",
        "Psi & Omega LLC≥",
        "Alpha & Beta Corp∑",
        "Gamma & Delta Ltd∏",
        "Epsilon & Zeta Inc√",
        "Eta & Theta LLC∫",
        "Iota & Kappa Corpα",
        "Lambda & Mu Ltdβ",
        "Nu & Xi Incγ",
        "Omicron & Pi LLCδ",
        "Rho & Sigma Corpμ",
        "Tau & Upsilon Ltdπ",
        "Phi & Chi Incσ",
        "Psi & Omega LLCτ",
        "Alpha & Beta Corpφ",
        "Gamma & Delta Ltdω",
        "Epsilon & Zeta IncΩ",
        "Eta & Theta LLCθ"
    ]
    
    for i, name1 in enumerate(base_names):
        # Create variations for name2
        if "&" in name1:
            name2 = name1.replace("&", "and")
        elif "and" in name1.lower():
            name2 = name1.replace("and", "&")
        else:
            # Add special characters
            special_chars = generate_special_characters()
            char = random.choice(special_chars)
            name2 = name1 + " " + char
        
        prediction_data.append({
            'name1': name1,
            'name2': name2
        })
    
    return prediction_data

def main():
    """Main function to generate data"""
    print("🔄 Generating extended training and prediction data...")
    
    # Generate training data
    training_data = generate_training_data()
    training_df = pd.DataFrame(training_data)
    
    # Generate prediction data
    prediction_data = generate_prediction_data()
    prediction_df = pd.DataFrame(prediction_data)
    
    # Save to Excel files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    training_filename = f"extended_training_data_{timestamp}.xlsx"
    prediction_filename = f"extended_prediction_data_{timestamp}.xlsx"
    
    training_df.to_excel(training_filename, index=False)
    prediction_df.to_excel(prediction_filename, index=False)
    
    print(f"✅ Generated {len(training_data)} training samples")
    print(f"✅ Generated {len(prediction_data)} prediction samples")
    print(f"📁 Training data saved to: {training_filename}")
    print(f"📁 Prediction data saved to: {prediction_filename}")
    
    # Print some examples
    print("\n📋 Sample Training Data:")
    print(training_df.head(10).to_string(index=False))
    
    print("\n📋 Sample Prediction Data:")
    print(prediction_df.head(10).to_string(index=False))
    
    # Print statistics
    material_count = training_df['is_material'].sum()
    immaterial_count = len(training_df) - material_count
    
    print(f"\n📊 Data Statistics:")
    print(f"   Material changes: {material_count}")
    print(f"   Immaterial changes: {immaterial_count}")
    print(f"   Total samples: {len(training_df)}")
    print(f"   Material ratio: {material_count/len(training_df)*100:.1f}%")

if __name__ == "__main__":
    main() 