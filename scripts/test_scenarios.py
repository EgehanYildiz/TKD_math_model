import requests
import json
import pandas as pd

API_URL = "http://localhost:5328/predict"

# 1. Define Realistic Scenarios
scenarios = [
    {
        "name": "The Titan (e.g., Koc Holding)",
        "data": {
            "industry_type": "ENERGY_UTILITIES", # Often conglomerates fall here or Finance
            "employee_count": 80000,
            "years_active": 90,
            "publicly_traded": 1,
            "esg_content": 1,
            "un_global": 1,
            "is_subsidiary": 0,
            "business_type": 1 
        },
        "expected": "Vision"
    },
    {
        "name": "The Global Retailer (e.g., LC Waikiki)",
        "data": {
            "industry_type": "RETAIL_CONSUMER",
            "employee_count": 50000,
            "years_active": 30,
            "publicly_traded": 0, # Private
            "esg_content": 1,
            "un_global": 0,
            "is_subsidiary": 0,
            "business_type": 1
        },
        "expected": "Dream" 
    },
    {
        "name": "The Tech Unicorn (e.g., Mid-Size Software)",
        "data": {
            "industry_type": "TECH_TELECOM",
            "employee_count": 800,
            "years_active": 10,
            "publicly_traded": 0,
            "esg_content": 0,
            "un_global": 0,
            "is_subsidiary": 0,
            "business_type": 1
        },
        "expected": "Inspire" # or Believe
    },
    {
        "name": "The Local SME (e.g., Local Construction)",
        "data": {
            "industry_type": "MANUFACTURING",
            "employee_count": 150,
            "years_active": 15,
            "publicly_traded": 0,
            "esg_content": 0,
            "un_global": 0,
            "is_subsidiary": 0,
            "business_type": 0 # B2B
        },
        "expected": "Believe"
    },
    {
        "name": "Global Bank Branch (e.g., Citi Turkey)",
        "data": {
            "industry_type": "FINANCE_INSURANCE",
            "employee_count": 2500,
            "years_active": 25,
            "publicly_traded": 1, 
            "esg_content": 1,
            "un_global": 1,
            "is_subsidiary": 1, # Subsidiary
            "business_type": 1
        },
        "expected": "Hope" # High potential but maybe subsidiary penalty?
    },
    # --- HYPOTHESIS TESTS (User Logic) ---
    # 1. Size Impact (Small vs Big)
    {
        "name": "Hypothesis: Small Company (10 emp)",
        "data": { "industry_type": "RETAIL_CONSUMER", "employee_count": 10, "years_active": 10, "business_type": 1, "esg_content": 0, "publicly_traded": 0, "un_global": 0, "is_subsidiary": 0 },
        "expected": "Believe"
    },
    {
        "name": "Hypothesis: Big Company (10k emp)",
        "data": { "industry_type": "RETAIL_CONSUMER", "employee_count": 10000, "years_active": 10, "business_type": 1, "esg_content": 0, "publicly_traded": 0, "un_global": 0, "is_subsidiary": 0 },
        "expected": "Hope" 
    },

    # 2. B2C vs B2B (Same size/industry)
    {
        "name": "Hypothesis: B2B Company",
        "data": { "industry_type": "MANUFACTURING", "employee_count": 500, "years_active": 20, "business_type": 0, "esg_content": 0, "publicly_traded": 0, "un_global": 0, "is_subsidiary": 0 }, 
        "expected": "Inspire"
    },
    {
        "name": "Hypothesis: B2C Company",
        "data": { "industry_type": "MANUFACTURING", "employee_count": 500, "years_active": 20, "business_type": 1, "esg_content": 0, "publicly_traded": 0, "un_global": 0, "is_subsidiary": 0 }, 
        "expected": "Dream" 
    },

    # 3. IPO Impact
    {
        "name": "Hypothesis: Private Company",
        "data": { "industry_type": "TECH_TELECOM", "employee_count": 1000, "years_active": 10, "publicly_traded": 0, "business_type": 0, "esg_content": 0, "un_global": 0, "is_subsidiary": 0 },
        "expected": "Inspire"
    },
    {
        "name": "Hypothesis: Public Company (IPO)",
        "data": { "industry_type": "TECH_TELECOM", "employee_count": 1000, "years_active": 10, "publicly_traded": 1, "business_type": 0, "esg_content": 0, "un_global": 0, "is_subsidiary": 0 },
        "expected": "Dream" 
    },

    # 4. UN Global Compact Impact
    {
        "name": "Hypothesis: Non-UNGC",
        "data": { "industry_type": "ENERGY_UTILITIES", "employee_count": 5000, "years_active": 30, "un_global": 0, "business_type": 0, "esg_content": 0, "publicly_traded": 0, "is_subsidiary": 0 },
        "expected": "Dream"
    },
    {
        "name": "Hypothesis: UNGC Member",
        "data": { "industry_type": "ENERGY_UTILITIES", "employee_count": 5000, "years_active": 30, "un_global": 1, "business_type": 0, "esg_content": 0, "publicly_traded": 0, "is_subsidiary": 0 },
        "expected": "Hope" 
    },

    # 5. Global Branch (Subsidiary)
    {
        "name": "Hypothesis: Local",
        "data": { "industry_type": "FINANCE_INSURANCE", "employee_count": 2000, "is_subsidiary": 0, "business_type": 0, "esg_content": 0, "publicly_traded": 0, "un_global": 0 },
        "expected": "Dream"
    },
    {
        "name": "Hypothesis: Global Branch",
        "data": { "industry_type": "FINANCE_INSURANCE", "employee_count": 2000, "is_subsidiary": 1, "business_type": 0, "esg_content": 0, "publicly_traded": 0, "un_global": 0 },
        "expected": "Hope"
    }
]

def run_tests():
    results = []
    print(f"{'Scenario Name':<40} | {'Prediction':<10} | {'Confidence':<10} | {'Match?'}")
    print("-" * 80)
    
    for s in scenarios:
        try:
            res = requests.post(API_URL, json=s['data'])
            if res.status_code == 200:
                pred = res.json()
                tier = pred['tier']
                conf = pred['confidence']
                match = "YES" if tier == s['expected'] else f"NO (Exp: {s['expected']})"
                
                print(f"{s['name']:<40} | {tier:<10} | {conf:.2f}       | {match}")
                
                results.append({
                    "Scenario": s['name'],
                    "Employees": s['data']['employee_count'],
                    "Public": bool(s['data']['publicly_traded']),
                    "Predicted": tier,
                    "Confidence": conf,
                    "Probabilities": pred['probabilities']
                })
            else:
                print(f"Error for {s['name']}: {res.text}")
        except Exception as e:
            print(f"Connection failed: {e}")

if __name__ == "__main__":
    run_tests()
