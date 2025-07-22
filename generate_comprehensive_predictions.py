#!/usr/bin/env python3
"""
Comprehensive Prediction Data Generator
Generates 100 prediction samples with special characters and various scenarios
"""

import pandas as pd
import random
import string
from datetime import datetime

def generate_comprehensive_predictions():
    """Generate 100 comprehensive prediction samples"""
    predictions = []
    
    # Base company names with special characters
    base_companies = [
        "Alpha & Beta Corporation",
        "Gamma & Delta Limited",
        "Epsilon & Zeta Incorporated",
        "Eta & Theta Company",
        "Iota & Kappa Industries",
        "Lambda & Mu Services",
        "Nu & Xi Solutions",
        "Omicron & Pi Systems",
        "Rho & Sigma Technologies",
        "Tau & Upsilon Consulting",
        "Phi & Chi Manufacturing",
        "Psi & Omega Trading",
        "Alpha & Beta International",
        "Gamma & Delta Global",
        "Epsilon & Zeta National",
        "Eta & Theta Regional",
        "Iota & Kappa Local",
        "Lambda & Mu Worldwide",
        "Nu & Xi American",
        "Omicron & Pi European",
        "Rho & Sigma Asian",
        "Tau & Upsilon Pacific",
        "Phi & Chi Atlantic",
        "Psi & Omega Northern",
        "Alpha & Beta Southern",
        "Gamma & Delta Eastern",
        "Epsilon & Zeta Western",
        "Eta & Theta Central",
        "Iota & Kappa Advanced",
        "Lambda & Mu Premium",
        "Nu & Xi Elite",
        "Omicron & Pi Professional",
        "Rho & Sigma Services",
        "Tau & Upsilon Solutions",
        "Phi & Chi Systems",
        "Psi & Omega Technologies",
        "Alpha & Beta Industries",
        "Gamma & Delta Manufacturing",
        "Epsilon & Zeta Distribution",
        "Eta & Theta Trading",
        "Iota & Kappa Investment",
        "Lambda & Mu Financial",
        "Nu & Xi Insurance",
        "Omicron & Pi Real Estate",
        "Rho & Sigma Development",
        "Tau & Upsilon Construction",
        "Phi & Chi Engineering",
        "Psi & Omega Consulting",
        "Alpha & Beta Management",
        "Gamma & Delta Administration",
        "Epsilon & Zeta Operations",
        "Eta & Theta Marketing",
        "Iota & Kappa Sales",
        "Lambda & Mu Customer",
        "Nu & Xi Client",
        "Omicron & Pi Partner",
        "Rho & Sigma Associate",
        "Tau & Upsilon Group",
        "Phi & Chi Team",
        "Psi & Omega Network",
        "Alpha & Beta Alliance",
        "Gamma & Delta Federation",
        "Epsilon & Zeta Consortium",
        "Eta & Theta Foundation",
        "Iota & Kappa Institute",
        "Lambda & Mu Academy",
        "Nu & Xi University",
        "Omicron & Pi College",
        "Rho & Sigma School",
        "Tau & Upsilon Center",
        "Phi & Chi Laboratory",
        "Psi & Omega Research",
        "Alpha & Beta Development",
        "Gamma & Delta Innovation",
        "Epsilon & Zeta Creative",
        "Eta & Theta Digital",
        "Iota & Kappa Online",
        "Lambda & Mu Virtual",
        "Nu & Xi Cloud",
        "Omicron & Pi Mobile",
        "Rho & Sigma Smart",
        "Tau & Upsilon Intelligent",
        "Phi & Chi Automated",
        "Psi & Omega Robotic",
        "Alpha & Beta Artificial",
        "Gamma & Delta Machine",
        "Epsilon & Zeta Learning",
        "Eta & Theta Data",
        "Iota & Kappa Analytics",
        "Lambda & Mu Information",
        "Nu & Xi Technology",
        "Omicron & Pi Software",
        "Rho & Sigma Hardware",
        "Tau & Upsilon Network",
        "Phi & Chi Security",
        "Psi & Omega Privacy",
        "Alpha & Beta Compliance",
        "Gamma & Delta Regulatory",
        "Epsilon & Zeta Legal",
        "Eta & Theta Corporate",
        "Iota & Kappa Business",
        "Lambda & Mu Enterprise",
        "Nu & Xi Commercial",
        "Omicron & Pi Industrial",
        "Rho & Sigma Manufacturing",
        "Tau & Upsilon Production",
        "Phi & Chi Quality",
        "Psi & Omega Standard"
    ]
    
    # Special characters for variations
    special_chars = [
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
    
    # Legal suffixes
    legal_suffixes = [
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
    
    # Common word variations
    common_words = [
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
    
    # Generate 100 prediction samples
    for i in range(100):
        base_company = random.choice(base_companies)
        
        # Create variations
        variation_type = random.choice(['special_char', 'legal_suffix', 'common_word', 'case_change', 'abbreviation'])
        
        if variation_type == 'special_char':
            # Add special characters
            char = random.choice(special_chars)
            name1 = base_company
            name2 = base_company + " " + char
            
        elif variation_type == 'legal_suffix':
            # Change legal suffix
            suffix = random.choice(legal_suffixes)
            if "Corporation" in base_company:
                name1 = base_company
                name2 = base_company.replace("Corporation", suffix)
            elif "Limited" in base_company:
                name1 = base_company
                name2 = base_company.replace("Limited", suffix)
            elif "Incorporated" in base_company:
                name1 = base_company
                name2 = base_company.replace("Incorporated", suffix)
            elif "Company" in base_company:
                name1 = base_company
                name2 = base_company.replace("Company", suffix)
            else:
                name1 = base_company
                name2 = base_company + " " + suffix
                
        elif variation_type == 'common_word':
            # Change common words
            word = random.choice(common_words)
            if "International" in base_company:
                name1 = base_company
                name2 = base_company.replace("International", word)
            elif "Global" in base_company:
                name1 = base_company
                name2 = base_company.replace("Global", word)
            elif "National" in base_company:
                name1 = base_company
                name2 = base_company.replace("National", word)
            elif "Regional" in base_company:
                name1 = base_company
                name2 = base_company.replace("Regional", word)
            elif "Local" in base_company:
                name1 = base_company
                name2 = base_company.replace("Local", word)
            else:
                name1 = base_company
                name2 = base_company + " " + word
                
        elif variation_type == 'case_change':
            # Change case
            name1 = base_company
            case_type = random.choice(['upper', 'lower', 'title'])
            if case_type == 'upper':
                name2 = base_company.upper()
            elif case_type == 'lower':
                name2 = base_company.lower()
            else:
                name2 = base_company.title()
                
        else:  # abbreviation
            # Create abbreviation
            words = base_company.split()
            if len(words) > 1:
                name1 = base_company
                name2 = " ".join([word[0] for word in words])
            else:
                name1 = base_company
                name2 = base_company + " " + random.choice(special_chars)
        
        predictions.append({
            'name1': name1,
            'name2': name2
        })
    
    return predictions

def main():
    """Main function to generate comprehensive prediction data"""
    print("🔄 Generating comprehensive prediction data...")
    
    # Generate prediction data
    prediction_data = generate_comprehensive_predictions()
    prediction_df = pd.DataFrame(prediction_data)
    
    # Save to Excel file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prediction_filename = f"comprehensive_prediction_data_{timestamp}.xlsx"
    
    prediction_df.to_excel(prediction_filename, index=False)
    
    print(f"✅ Generated {len(prediction_data)} prediction samples")
    print(f"📁 Prediction data saved to: {prediction_filename}")
    
    # Print some examples
    print("\n📋 Sample Prediction Data:")
    print(prediction_df.head(15).to_string(index=False))
    
    # Print statistics
    print(f"\n📊 Data Statistics:")
    print(f"   Total samples: {len(prediction_df)}")
    print(f"   Unique name1: {prediction_df['name1'].nunique()}")
    print(f"   Unique name2: {prediction_df['name2'].nunique()}")
    
    # Show some special character examples
    special_char_examples = prediction_df[prediction_df['name2'].str.contains(r'[®™©℠§¶†‡°±×÷¢£¥€№℅‰∞≈≠≤≥∑∏√∫αβγδμπστφωΩθ]', regex=True)]
    if not special_char_examples.empty:
        print(f"\n🎯 Special Character Examples:")
        print(special_char_examples.head(5).to_string(index=False))

if __name__ == "__main__":
    main() 