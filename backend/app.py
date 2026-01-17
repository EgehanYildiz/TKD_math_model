from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib

app = Flask(__name__)
CORS(app) # Enable CORS for Next.js

# Load Artifacts
try:
    artifacts = joblib.load('tkd_model_artifacts.pkl')
    model = artifacts['model']
    industry_map = artifacts['industry_map']
    # industry_medians removed in V1.5
    global_mean = artifacts['global_mean']
    feature_cols = artifacts['features']
    print(">>> Model and Artifacts Loaded Successfully")
except Exception as e:
    print(f"CRITICAL ERROR: Could not load model: {e}")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        print("Received Data:", data)
        
        # Expecting:
        # employee_count (int)
        # years_active (int)
        # esg_content (bool/int)
        # un_global (bool/int)
        # publicly_traded (bool/int)
        # industry_type (str) (Original name from Excel/Dropdown)
        # business_type (int) (0 or 1)
        # is_subsidiary (int) (0 or 1)
        
        # 1. Feature Engineering (Replicate training logic)
        
        # Log Transforms
        emp_count = float(data.get('employee_count', 0))
        years = float(data.get('years_active', 0))
        
        log_emp = np.log1p(emp_count)
        log_years = np.log1p(years)
        
        # Governance Score
        esg = int(data.get('esg_content', 0))
        un_global = int(data.get('un_global', 0))
        public = int(data.get('publicly_traded', 0))
        
        gov_score = esg + un_global + public
        
        # Interaction
        size_x_gov = log_emp * (gov_score + 1)
        
        # Industry Encoding
        # Since industry map keys are integers (from encoded analysis), we might have a disconnect if UI sends strings.
        # Wait, in train_model.py we encoded 'Industry Type' using LabelEncoder in previous steps?
        # NO, in train_model.py we loaded the excel where 'Industry Type' was ALREADY encoded as 0,1,2.. in Phase 2 data?
        # Let's check `analyze_data.py` output: "Industry Type (7 unique): int64" 
        # So the input MUST be the integer code for Industry.
        
    # Industry Encoding
        # Industry Map keys are Strings (e.g., 'RETAIL_CONSUMER')
        industry_key = str(data.get('industry_type', 'RETAIL_CONSUMER')) 
        
        # Look up mean value
        val = industry_map.get(industry_key)
        if val is None:
            print(f"Warning: Industry '{industry_key}' not found in map. Using global mean.")
            industry_encoded = global_mean
        else:
            industry_encoded = val
        
        # Construct Feature Vector
        # Order: Log_Employee, Log_Years, Governance_Score, Size_x_Gov, Industry_Target_Encoded, Business Type, Is Subsidiary
        features = [
            log_emp,
            log_years,
            gov_score,
            size_x_gov,
            industry_encoded,
            int(data.get('business_type', 0)),
            int(data.get('is_subsidiary', 0))
        ]
        
        # Predict
        features_arr = np.array([features])
        prediction_class = model.predict(features_arr)[0]
        probabilities = model.predict_proba(features_arr)[0]
        confidence = max(probabilities)
        
        # Map Class to Name
        # 1: Believe, 2: Inspire, 3: Dream, 4: Hope, 5: Vision
        class_names = {1: 'Believe', 2: 'Inspire', 3: 'Dream', 4: 'Hope', 5: 'Vision'}
        result_name = class_names.get(prediction_class, "Unknown")
        
        return jsonify({
            'tier': result_name,
            'tier_code': int(prediction_class),
            'confidence': float(confidence),
            'probabilities': probabilities.tolist()
        })

    except Exception as e:
        print(f"Error predicting: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5328) # Use a custom port to avoid conflicts
