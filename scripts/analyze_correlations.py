import pandas as pd
import numpy as np
# import seaborn as sns
# import matplotlib.pyplot as plt

def analyze_clean_correlations():
    print(">>> Loading Data...")
    
    # 1. Load & Merge (Replicating train_model.py logic)
    xls_p2 = pd.ExcelFile("Model Datası, Phase 2.xlsx")
    all_features = [pd.read_excel(xls_p2, s) for s in xls_p2.sheet_names]
    df_features = pd.concat(all_features, ignore_index=True)
    df_features.columns = [c.strip() for c in df_features.columns]
    
    xls_p1 = pd.ExcelFile("Model Datası, Phase 1.xlsx")
    target_mapping = {
        'Vision':5, 'Visionary':5, 'Visionaries':5, 'Visionary Partner':5,
        'Hope':4, 'Groundbreaker':4, 'Groundbreakers':4, 'Groundbreaking Partner':4,
        'Dream':3, 'Pioneer':3, 'Pioneers':3, 'Inspiration Partner':3,
        'Inspire':2, 'Champion':2, 'Champions':2, 'Champion Partner':2,
        'Believe':1, 'Guardian':1, 'Guardians':1, 'Guiding Partner':1
    }
    
    all_labels = []
    for s in xls_p1.sheet_names:
        df = pd.read_excel(xls_p1, s)
        df.columns = [c.strip() for c in df.columns]
        if 'Partnerlik Seviyesi' in df.columns:
            df['Target'] = df['Partnerlik Seviyesi'].map(target_mapping)
            all_labels.append(df[['Partner Adı', 'Target']].dropna())
            
    df_labels = pd.concat(all_labels, ignore_index=True)
    
    merged = pd.merge(df_features, df_labels, left_on='Company Name', right_on='Partner Adı', how='inner')
    
    # 2. APPLY SANITATION (Crucial Step)
    print(f"Pre-clean size: {len(merged)}")
    for col in ['ESG Content', 'UN Global Impact', 'Publicly Traded']:
        merged[col] = merged[col].fillna(0)
    merged['Employee Count'] = merged['Employee Count'].fillna(merged['Employee Count'].median())
    
    gov_score = merged['ESG Content'] + merged['UN Global Impact'] + merged['Publicly Traded']
    mask_big_low = (merged['Employee Count'] > 10000) & (merged['Target'] <= 2)
    mask_high_gov_low = (gov_score >= 2) & (merged['Target'] == 1)
    
    clean_df = merged[~ (mask_big_low | mask_high_gov_low)]
    print(f"Post-clean size: {len(clean_df)}")
    
    # 3. Calculate Correlations
    # We want to see correlation with Target
    cols_to_check = [
        'Employee Count', 
        'Years Active', 
        'Business Type', # B2B=0, B2C=1
        'Publicly Traded', 
        'ESG Content', 
        'UN Global Impact', 
        'Is Subsidiary',
        'Target'
    ]
    
    corr_matrix = clean_df[cols_to_check].corr()
    target_corr = corr_matrix['Target'].sort_values(ascending=False)
    
    print("\n>>> CORRELATIONS WITH TARGET (Clean Data):")
    print(target_corr)
    
    print("\n>>> Interpretation:")
    print("Positive value = Higher Feature leads to Higher Potential.")
    print("If Employee Count correlation is high, then Big = High Potential is working.")

if __name__ == "__main__":
    analyze_clean_correlations()
