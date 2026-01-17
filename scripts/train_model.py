import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import warnings

warnings.filterwarnings('ignore')

def train_and_save_model():
    print(">>> Loading Data...")
    # ---------------------------------------------------------
    # 1. Load Data (Expanded)
    # ---------------------------------------------------------
    print(">>> Loading Data (All Sheets)...")
    
    # Load Features (All Sheets)
    xls_p2 = pd.ExcelFile("Model Datası, Phase 2.xlsx")
    all_features = []
    
    for sheet_name in xls_p2.sheet_names:
        print(f"Loading Features from: {sheet_name}")
        df = pd.read_excel(xls_p2, sheet_name)
        df.columns = [c.strip() for c in df.columns]
        all_features.append(df)
        
    df_phase2 = pd.concat(all_features, ignore_index=True)
    
    # Load Labels (All Sheets)
    xls_p1 = pd.ExcelFile("Model Datası, Phase 1.xlsx")
    all_labels = []
    
    # Unified Mapping
    target_mapping = {
        # 5 - Vision
        'Vision': 5, 'Visionary': 5, 'Visionaries': 5, 'Visionary Partner': 5,
        
        # 4 - Hope
        'Hope': 4, 'Groundbreaker': 4, 'Groundbreakers': 4, 'Groundbreaking Partner': 4, 'Excellence Partner': 4,
        
        # 3 - Dream
        'Dream': 3, 'Pioneer': 3, 'Pioneers': 3, 'Inspiration Partner': 3,
        
        # 2 - Inspire
        'Inspire': 2, 'Champion': 2, 'Champions': 2, 'Champion Partner': 2,
        
        # 1 - Believe
        'Believe': 1, 'Guardian': 1, 'Guardians': 1, 'Guiding Partner': 1, 'Caring Partner': 1, 'Guardian Partner': 1
    }

    for sheet_name in xls_p1.sheet_names:
        print(f"Processing sheet: {sheet_name}")
        df = pd.read_excel(xls_p1, sheet_name)
        df.columns = [c.strip() for c in df.columns]
        
        # Normalize Target Column
        if 'Partnerlik Seviyesi' in df.columns:
            df['Mapped_Target'] = df['Partnerlik Seviyesi'].map(target_mapping)
            # Drop unmapped rows (like 'Brand Ambassador')
            dropped = df[df['Mapped_Target'].isna()]
            if not dropped.empty:
               print(f"   - Dropping {len(dropped)} rows with unmapped labels: {dropped['Partnerlik Seviyesi'].unique()}")
            
            df = df.dropna(subset=['Mapped_Target'])
            
            # --- SANITATION LOGIC (User Request) ---
            # Rule 1: Big Companies (>10k) cannot be Low Tier (1 or 2)
            # Rule 2: High Governance (Score >= 2) cannot be Tier 1
            
            # We need features to filter, but here we only have Labels.
            # So we must wait until merge to filter? NO, we can filter after merge.
            # Saving just label data for now.
            all_labels.append(df[['Partner Adı', 'Mapped_Target']])
            
    # Combine all labels
    df_labels_combined = pd.concat(all_labels, ignore_index=True)
    
    # Merge Features & Labels
    merged_df = pd.merge(
        df_phase2, 
        df_labels_combined, 
        left_on='Company Name', 
        right_on='Partner Adı', 
        how='inner'
    )
    
    merged_df.rename(columns={'Mapped_Target': 'Target'}, inplace=True)
    
    # --- ADVANCED SANITATION (POST-MERGE) ---
    print(f"\n>>> Sanitation Check (Pre-clean size: {len(merged_df)})")
    
    # Calculate Governance for filtering (Naive calculation before full engineering)
    # Ensure cols exist
    for col in ['ESG Content', 'UN Global Impact', 'Publicly Traded']:
        merged_df[col] = merged_df[col].fillna(0)
    
    gov_score_temp = merged_df['ESG Content'] + merged_df['UN Global Impact'] + merged_df['Publicly Traded']
    
    # Rule 1: Drop Big (>10k) but Low Tier (<=2)
    # "The bigger the company the greater the potential"
    mask_big_low = (merged_df['Employee Count'] > 10000) & (merged_df['Target'] <= 2)
    
    # Rule 2: High Governance (>=2) but Tier 1
    # "IPO / UN Global / Sustainability means more potential"
    mask_high_gov_low = (gov_score_temp >= 2) & (merged_df['Target'] == 1)
    
    # Drop them
    outliers = merged_df[mask_big_low | mask_high_gov_low]
    if not outliers.empty:
        print(f"   - DROPPING {len(outliers)} Logic Violators (Big/Public but Low Tier).")
        print(f"     Examples: {outliers['Company Name'].head(5).tolist()}")
        merged_df = merged_df[~ (mask_big_low | mask_high_gov_low)]
        
    print(f"Final Training Set Size: {len(merged_df)} samples")
    
    # ---------------------------------------------------------
    # Feature Engineering
    # ---------------------------------------------------------
    print("\n>>> Feature Engineering...")
    df_eng = merged_df.copy()
    
    # Handle Numeric Nulls
    numeric_cols = ['Employee Count', 'Years Active']
    for col in numeric_cols:
        if df_eng[col].isnull().any():
            df_eng[col] = df_eng[col].fillna(df_eng[col].median())

    # Log Transforms
    df_eng['Log_Employee'] = np.log1p(df_eng['Employee Count'])
    df_eng['Log_Years'] = np.log1p(df_eng['Years Active'])
    
    # Governance Score
    df_eng['Governance_Score'] = (
        df_eng['ESG Content'] + 
        df_eng['UN Global Impact'] + 
        df_eng['Publicly Traded']
    )
    
    # Interaction
    df_eng['Size_x_Gov'] = df_eng['Log_Employee'] * (df_eng['Governance_Score'] + 1)
    
    # Industry Encoding
    # For production, we need to save the map
    industry_means = df_eng.groupby('Industry Type')['Target'].mean()
    # Fill any missing industry in future (if new appears) with global mean
    global_mean = df_eng['Target'].mean()
    
    df_eng['Industry_Target_Encoded'] = df_eng['Industry Type'].map(industry_means).fillna(global_mean)
    
    features = [
        'Log_Employee', 'Log_Years', 
        'Governance_Score', 'Size_x_Gov',
        'Industry_Target_Encoded',
        'Business Type', 'Is Subsidiary'
    ]
    
    X = df_eng[features]
    y = df_eng['Target']
    
    # ---------------------------------------------------------
    # Model Training
    # ---------------------------------------------------------
    print("\n>>> Training Final Model (V1.5 - Expanded Data)...")
    # Back to standard Random Forest
    rf = RandomForestClassifier(
        n_estimators=200, 
        random_state=42, 
        max_depth=7,
        min_samples_leaf=2
    )
    rf.fit(X, y)
    
    print("Model Score (Training Accuracy):", rf.score(X, y))
    
    # ---------------------------------------------------------
    # Saving Artifacts
    # ---------------------------------------------------------
    print("\n>>> Saving Model & Artifacts...")
    
    artifacts = {
        'model': rf,
        'industry_map': industry_means.to_dict(),
        'global_mean': global_mean,
        'features': features
    }
    
    joblib.dump(artifacts, 'tkd_model_artifacts.pkl')
    print("Saved to 'tkd_model_artifacts.pkl'")

if __name__ == "__main__":
    train_and_save_model()
